"""
This module contains the classes and functions for creating demographics files
for HIV simulations. For more information on |EMOD_s| demographics files,
see :doc:`emod/software-demographics`. 
"""
import math

import pandas as pd

from typing import List, Union

from emod_api.demographics import Demographics as demographics_module
from emod_api.demographics import DemographicsTemplates as dt
from emod_api.demographics.Demographics import Demographics
from emod_api.demographics.DemographicsTemplates import YearlyRate
from emod_api.demographics.PropertiesAndAttributes import IndividualAttributes, IndividualProperty, IndividualProperties

from emodpy_hiv.demographics import DemographicsTemplates as hiv_dt
from emodpy_hiv.demographics.assortivity import Assortivity
from emodpy_hiv.demographics.hiv_node import HIVNode
from emodpy_hiv.demographics.society import Society


class HIVDemographics(Demographics):
    def __init__(self, nodes: List[HIVNode], default_society_template: str = None):
        """
        This class is derived from :py:class:`emod_api:emod_api.demographics.Demographics.Demographics` adding HIV-
        specific features and sets certain defaults for HIV in construction.

        Args:
            nodes: A list of (non-Default) HIVNode objects
            default_society_template: society template name for loading initial society information. Will apply
                to the Default node.

        Returns:
            an HIVDemographics object
         """
        # we need to generate the default node before calling super() because we need it to be an HIVNode, not Node
        if default_society_template is None:
            society_dict = hiv_dt.get_default_society_dict()
        else:
            society_dict = hiv_dt.get_society_dict(society_name=default_society_template)
        society = Society.from_dict(d=society_dict)
        default_node = HIVNode(name='Default', lat=0, lon=0, pop=0, forced_id=0, society=society)

        super().__init__(nodes=nodes, idref="EMOD-HIV world", default_node=default_node)
        # TODO: cut-paste this into emod-api DemographicsBase constructor (when default_node is not None)
        #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/699

        # default individual properties for HIV
        # Note: copied from PFA-Southern-Africa society, we are assuming Risk-based assortivity
        self.add_or_update_initial_risk_distribution(distribution=[0.6669671396606822, 0.3330328603393178, 0])

        # default individual attributes for HIV

        # TODO: THIS is the problem ... altering the age distribution LATER does NOT unset these!
        #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/705
        # Uniform age distribution by default
        default_node.individual_attributes.age_distribution_flag = 1
        default_node.individual_attributes.age_distribution1 = 0
        default_node.individual_attributes.age_distribution2 = 18250

        # no initial prevalence by default
        # TODO: not currently supported in emod-api directly, update when it is
        #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/700
        default_node.individual_attributes.parameter_dict.update({'InitialPrevalence': 0})

        # Node attributes copied from Demographics.SetDefaultNodeAttributes (which uses self.raw, which cannot
        #   be used with HIVDemographics). These may or may not be needed by HIV.
        default_node.node_attributes.altitude = 0
        default_node.node_attributes.airport = 1
        default_node.node_attributes.region = 1
        default_node.node_attributes.seaport = 1
        default_birth_rate = YearlyRate(math.log(1.03567))
        self.SetBirthRate(birth_rate=default_birth_rate, node_ids=[None])

        # TODO: total workaround emod-api DemographicsBase class setting this up for raw not objects
        self.metadata = self.generate_headers()

    @property
    def raw(self):
        raise AttributeError(f"raw is not a valid attribute for HIVDemographics objects")

    @raw.setter
    def raw(self, value):
        raise AttributeError(f"raw is not a valid attribute for HIVDemographics objects")

    # TODO: push into superclass (emod-api Demographics) if able to safely
    #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/207
    def set_fertility(self, path_to_csv: str, node_ids: List[int] = None) -> None:
        """
        Set fertility based on data to the selected node(s). Simulation shall consist of individual pregnancies with
        rates by woman's age and year-of-simulation using data from provided csv. Bilinear interpolation is performed
        between supplied data points.

        Args:
            path_to_csv: path to csv file to load data from
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        distribution_dict = dt.get_fert_dist(path_to_csv, verbose=False)['FertilityDistribution']
        fertility = IndividualAttributes.FertilityDistribution()
        fertility = fertility.from_dict(fertility_distribution=distribution_dict)
        nodes = self.get_nodes_by_id(node_ids=node_ids).values()
        for node in nodes:
            node._set_fertility_distribution(distribution=fertility)
        self.implicits.append(dt._set_fertility_age_year)

    # TODO: push into superclass (emod-api Demographics) if able to safely
    #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/207
    def set_mortality(self,
                      file_male: str,
                      file_female: str,
                      node_ids: List[int] = None,
                      interval_fit: List[Union[int, float]] = None,
                      which_point: str = 'mid',
                      predict_horizon: Union[int, float] = 2050,
                      csv_out: bool = False,
                      results_scale_factor: float = 1.0/365.0) -> None:
        """
        Adds male and female non-disease-mortality to the selected node(s). Non-disease-mortality is estimated using the
        supplied raw data and arguments.

        Args:
            file_male: path to csv file to load raw male data from
            file_female: path to csv file to load raw female data from
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.
            interval_fit: A list of two years, [start, end] , defining a period of used as a 'non-disease-timeframe'
                during the non-disease-mortality calculation
            which_point: controls mapping of supplied timeframes to 'start', 'end', or 'mid'-points of the timeframes
            predict_horizon: mortality will be computed and set through this specified year
            csv_out: Writes out diagnostic files if set to True
            results_scale_factor: Daily data conversion factor: supplied_mortality * factor = daily_mortality

        Returns:
            None
        """
        female_dict, male_dict = self.infer_natural_mortality(file_male,
                                                              file_female,
                                                              interval_fit=interval_fit,
                                                              which_point=which_point,
                                                              predict_horizon=predict_horizon,
                                                              csv_out=csv_out,
                                                              results_scale_factor=results_scale_factor)
        female_mortality = IndividualAttributes.MortalityDistribution()
        female_mortality = female_mortality.from_dict(mortality_distribution=female_dict)
        male_mortality = IndividualAttributes.MortalityDistribution()
        male_mortality = male_mortality.from_dict(mortality_distribution=male_dict)
        nodes = self.get_nodes_by_id(node_ids=node_ids).values()
        for node in nodes:
            node._set_mortality_distribution_female(distribution=female_mortality)
            node._set_mortality_distribution_male(distribution=male_mortality)
        self.implicits.append(dt._set_mortality_age_gender_year)

    def set_concurrency_params_by_type_and_risk(self, relationship_type: str, risk_group: str,
                                                max_simul_rels_male: float = None, max_simul_rels_female: float = None,
                                                prob_xtra_rel_male: float = None, prob_xtra_rel_female: float = None,
                                                node_ids: List[int] = None) -> None:
        """
        Set concurrent relationship formation parameters for a given relationship type, risk group, and node(s).

        Only non-None values will be updated.

        Each agent updates their max values and their ability to have extra relationships when they change
        nodes/locations or change their Risk IP value.

        Notes on maximums:
            - A max relationships parameter can be set to 2+, but if probability of extra is zero, an agent will never
              have more than one relationship of the given type.
            - fractional max relationship parameters are probabilistically rounded up or down per agent. E.g., max
              relationships of 2.3 implies agents have a (70%, 30%) chance of getting a maximum of (2, 3), respectively.

        Note on probabilities:
            - These probabilities apply to agents currently with at least ONE relationship of the given type seeking
              an additional such relationship.

        Args:
            relationship_type: Relationship type to update: "COMMERCIAL", "MARITAL", "INFORMAL" or "TRANSITORY"
            risk_group: risk group to set concurrency parameters for. "HIGH", "MEDIUM", or "LOW"
            max_simul_rels_male: Sets the maximum simultaneous relationships of the given relationship_type for males
                in the given risk_group.
            max_simul_rels_female: Sets the maximum simultaneous relationships of the given relationship_type for
                females in the given risk_group.
            prob_xtra_rel_male: The probability of a male receiving a flag that allows him to seek additional
                relationships while currently in another relationship.
            prob_xtra_rel_female: The probability of a female receiving a flag that allows her to seek additional
                relationships while currently in another relationship.
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        for node in self.get_nodes_by_id(node_ids=node_ids).values():
            node.society.set_concurrency_parameters(relationship_type=relationship_type,
                                                    risk=risk_group,
                                                    max_simul_rels_male=max_simul_rels_male,
                                                    max_simul_rels_female=max_simul_rels_female,
                                                    prob_xtra_rel_male=prob_xtra_rel_male,
                                                    prob_xtra_rel_female=prob_xtra_rel_female)

    def set_pair_formation_parameters(self, relationship_type: str,
                                      formation_rate: float = None,
                                      assortivity_matrix: List[List[float]] = None,
                                      node_ids: List[int] = None) -> None:
        """
        Sets pair formation parameters for the specified relationship type and node(s).

        Only non-None values will be updated.

        Args:
            relationship_type: Relationship type to update: "COMMERCIAL", "MARITAL", "INFORMAL" or "TRANSITORY"
            assortivity_matrix: 3x3 row-major matrix of assortivity values, row represents male,
                column represents female. E.g. matrix[male_index][female_index]
                This matrix defines the tendency for a man of a particular Risk group to select a woman based on her
                Risk group (LOW/MEDIUM/HIGH male selecting LOW/MEDIUM/HIGH female -> 3x3 matrix).
            formation_rate: The number of new relationships per day for this relationship type that an individual will
                start. This can be changed during a simulation via a RelationshipFormationRateChanger intervention.
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        assortivity = None if assortivity_matrix is None else Assortivity(matrix=assortivity_matrix)
        for node in self.get_nodes_by_id(node_ids=node_ids).values():
            node.society.set_pair_formation_parameters(relationship_type=relationship_type,
                                                       formation_rate=formation_rate,
                                                       assortivity=assortivity)

    def set_relationship_parameters(self, relationship_type: str,
                                    coital_act_rate: float = None,
                                    condom_usage_min: float = None,
                                    condom_usage_mid: float = None,
                                    condom_usage_max: float = None,
                                    condom_usage_rate: float = None,
                                    duration_scale: float = None,
                                    duration_heterogeneity: float = None,
                                    node_ids: List[int] = None) -> None:
        """
        Sets relationship parameters for the specified relationship type and node(s).

        Only non-None values will be updated.

        Args:
            relationship_type: Relationship type to update: "COMMERCIAL", "MARITAL", "INFORMAL" or "TRANSITORY"
            coital_act_rate: Sets the per-day coital act rate for the specified relationship type. This can be changed
                during a simulation via a CoitalActRateChanger intervention.
            condom_usage_min: minimum condom usage probability (pre-inflection point). All four of these condom usage
                parameters can be changed during a simulation via a CondomUsageProbabilityChanger intervention.
            condom_usage_mid: inflection point in condom usage (a year)
            condom_usage_max: maximum condom usage probability (post-inflection point)
            condom_usage_rate: slope of condom usage at inflection point
            duration_scale: weibull distributed relationship duration value (Lambda)
            duration_heterogeneity: weibull distributed relationship heterogeneity value (1/Kappa)
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        for node in self.get_nodes_by_id(node_ids=node_ids).values():
            node.society.set_relationship_parameters(relationship_type=relationship_type,
                                                     coital_act_rate=coital_act_rate,
                                                     condom_usage_min=condom_usage_min,
                                                     condom_usage_mid=condom_usage_mid,
                                                     condom_usage_max=condom_usage_max,
                                                     condom_usage_rate=condom_usage_rate,
                                                     duration_scale=duration_scale,
                                                     duration_heterogeneity=duration_heterogeneity)

    def _add_or_update_individual_property_distribution(self, property_name: str,
                                                        values: List[str],
                                                        distribution: List[float],
                                                        node_ids: List[int] = None) -> None:
        self.AddIndividualPropertyAndHINT(Property=property_name, Values=values, InitialDistribution=distribution,
                                          node_ids=node_ids, overwrite_existing=True)

    # TODO: Should the following IP distribution setting methods accept lists of values, too? Or should we leave them
    #  hard-coded like this for "normal" usage, to be altered via _add_or_remove_... (above) if needed?
    #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/206
    def add_or_update_initial_risk_distribution(self, distribution: List[float],
                                                node_ids: List[int] = None) -> None:
        """
        Adds the Risk individual property with specified initial distribution to the specified node(s).

        Args:
            distribution: a list of three floats that sum to 1 corresponding to distribution of Risk in this order:
                'LOW', 'MEDIUM', 'HIGH'
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        property = 'Risk'
        values = ['LOW', 'MEDIUM', 'HIGH']
        self._add_or_update_individual_property_distribution(property_name=property, values=values,
                                                             distribution=distribution, node_ids=node_ids)

    # TODO: change CascadeState here (and anywhere else) to InterventionStatus for consistency with EMOD terminology
    #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/213
    def add_or_update_initial_cascade_state_distribution(self, distribution: List[float],
                                                         node_ids: List[int] = None) -> None:
        """
        Adds the CascadeState individual property with specified initial distribution to the specified node(s).

        Args:
            distribution: a list of fourteen floats that sum to 1 corresponding to distribution of CascadeState in this
                order:
                '', 'ARTStaging', 'ARTStagingDiagnosticTest', 'LinkingToART', 'LinkingToPreART', 'OnART', 'OnPreART',
                'HCTTestingLoop', 'HCTUptakeAtDebut', 'HCTUptakePostDebut', 'TestingOnANC', 'TestingOnChild6w',
                'TestingOnSymptomatic', 'LostForever'
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        property = 'CascadeState'
        values = ["", "ARTStaging", "ARTStagingDiagnosticTest", "LinkingToART", "LinkingToPreART", "OnART", "OnPreART",
                  "HCTTestingLoop", "HCTUptakeAtDebut", "HCTUptakePostDebut", "TestingOnANC", "TestingOnChild6w",
                  "TestingOnSymptomatic", "LostForever"]
        self._add_or_update_individual_property_distribution(property_name=property, values=values,
                                                             distribution=distribution, node_ids=node_ids)

    def add_or_update_initial_health_care_accessibility_distribution(self, distribution: List[float],
                                                                     node_ids: List[int] = None) -> None:
        """
        Adds the (health care) Accessibility individual property with specified initial distribution to the specified
            node(s).

        Args:
            distribution: a list of three floats that sum to 1 corresponding to distribution of Accessibility in this
                order:
                'Yes', 'No'
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        property = 'Accessibility'
        values = ['Yes', 'No']
        self._add_or_update_individual_property_distribution(property_name=property, values=values,
                                                             distribution=distribution, node_ids=node_ids)

    # TODO: push into superclass (emod-api Demographics) if able to safely
    #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/687
    def SetAgeDistribution(self, distribution: IndividualAttributes.AgeDistribution,
                           node_ids: List[int] = None) -> None:
        """
        Set the default age distribution for the specified node(s).

        Args:
            distribution: age distribution information to set.
            node_ids: the id(s) of node(s) to apply changes to. None or 0 refers to the Default node.

        Returns:
            None
        """
        for node in self.get_nodes_by_id(node_ids=node_ids).values():
            node._set_age_distribution(distribution=distribution)
        self.implicits.append(dt._set_age_complex)


    def AddIndividualPropertyAndHINT(self, Property: str, Values: List[str], InitialDistribution:List[float] = None,
                                     TransmissionMatrix:List[List[float]] = None, Transitions: List = None,
                                     node_ids: List[int] = None, overwrite_existing: bool = False) -> None:
        """
        Add Individual Properties, including an optional HINT configuration matrix.

        Individual properties act as 'labels' on model agents that can be used for identifying and targeting
        subpopulations in campaign elements and reports. E.g. model agents may be given a property ('Accessibility')
        that labels them as either having access to health care (value: 'Yes') or not (value: 'No').

        Property-based heterogeneous disease transmission (HINT) is available for generic, environmental, typhoid,
        airborne, or TBHIV simulations as other simulation types have parameters for modeling the heterogeneity of
        transmission. By default, transmission is assumed to occur homogeneously among the population within a node.

        Note: EMOD requires individual property key and values (Property and Values args) to be the same across all
            nodes. The individual distributions of individual properties (InitialDistribution) can vary acros nodes.

        Documentation of individual properties and HINT:
            https://docs.idmod.org/projects/emod-generic/en/latest/model-properties.html
            https://docs.idmod.org/projects/emod-generic/en/latest/model-hint.html

        Args:
            Property: a new individual property key to add (if property already exists an exception is raised
                unless overwrite_existing is True).
            Values: the valid values of the new property key
            InitialDistribution: The fractional initial distribution of each valid Values entry. Order must match
                Values argument.
            TransmissionMatrix: HINT transmission matrix.
            node_ids: The node ids to apply changes to. None or 0 means the 'Defaults' node.
            overwrite_existing: Determines if an error is thrown if the IP is found pre-existing at a specified node.
                False: throw exception. True: overwrite the existing property.
        Returns:
            None
        """
        # TODO: This does not play nicely with emod-api Demographics (used by malaria/other diseases). Need to remove
        #  this HIV-specific override method once demographics.raw is removed entirely from emod-api
        #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/687
        nodes = self.get_nodes_by_id(node_ids=node_ids).values()
        for node in nodes:
            if not overwrite_existing and node.has_individual_property(property_key=Property):
                raise ValueError("Property Type '{0}' already present in IndividualProperties list".format(Property))

            # Check if Property is in whitelist. If not, auto-set Disable_IP_Whitelist
            # NOTE: Disable_IP_Whitelist is no longer in the malaria-ongoing branch of EMOD (used for malaria and HIV),
            # however, because other still-active branches of EMOD exist (that utilize Disable_IP_Whitelist), this logic
            # cannot be removed yet.
            ip_whitelist = ["Age_Bin", "Accessibility", "Geographic", "Place", "Risk", "QualityOfCare", "HasActiveTB",
                            "InterventionStatus"]
            if Property not in ip_whitelist:
                def update_config(config):
                    config.parameters["Disable_IP_Whitelist"] = 1
                    return config
                self.implicits.append(update_config)

            tm_dict = None if TransmissionMatrix is None else {"Route": "Contact", "Matrix": TransmissionMatrix}
            individual_property = IndividualProperty(property=Property,
                                                     values=Values,
                                                     initial_distribution=InitialDistribution,
                                                     transitions=Transitions,
                                                     transmission_matrix=tm_dict)
            node.individual_properties.add(individual_property=individual_property, overwrite=overwrite_existing)

        if TransmissionMatrix is not None:
            def update_config(config):
                config.parameters.Enable_Heterogeneous_Intranode_Transmission = 1
                return config
            self.implicits.append(update_config)

    # TODO: test this new version
    def to_dict(self):
        demographics = {'Nodes': [], 'Metadata': self.metadata}

        # TODO: refactor this when emod-api Node.to_dict() is fixed, to be more simply:
        #  demographics['Nodes'] = [node.to_dict() for node in self.nodes]
        #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/702
        node_info = []
        for node in self.nodes:
            node_dict = node.to_dict()
            node_dict.update(node.meta)
            node_info.append(node_dict)
        demographics['Nodes'] = node_info

        demographics['Defaults'] = self.default_node.to_dict()
        demographics["Metadata"]["NodeCount"] = len(self.nodes)
        return demographics

    @classmethod
    def from_population_dataframe(cls, df: pd.DataFrame, default_society_template: str = None) -> '__class__':
        """
        Loads per-node population information from a formatted pandas DataFrame object into HIVNode objects, returning
        an HIVDemographics object containing them.

        Expected DataFrame format:

        node_id,name,population
        1,Province1,1000
        2,Province2,2500
        ...


        Args:
            df: data for initializing the nodes of an
            default_society_template: society template name for loading initial society information. Will apply
                to the Default node.

        Returns:
            an HIVDemographics object
        """
        """
        TODO: add demographics file error checks
        - no duplicate node_ids
        - node_ids are integers 1+
        - no duplicate node names
        - populations are integers 0+
        - column checking: are exactly the required columns in the file?
        """
        # TODO: consider if this can be merged into a more general emod-api call
        nodes = []
        for index, row in df.iterrows():
            nodes.append(HIVNode(lat=0, lon=0, pop=int(row['population']),
                                 name=row['name'], forced_id=int(row['node_id'])))
        return cls(nodes=nodes, default_society_template=default_society_template)

    @classmethod
    def from_template_node(cls, lat: float = 0, lon: float = 0, pop: float = 1e6, name: str = 'node1',
                           forced_id: int = 1, default_society_template: str = None) -> '__class__':
        """
        Creates a single-node HIVDemographics object from the supplied parameters

        Args:
            lat: Latitude of the centroid of the node to create.
            lon: Longitude of the centroid of the node to create.
            pop: Human population of the node.
            name: The name of the node. This may be a characteristic of the node, such as "rural" or "urban", or an
                identifying feature or value.
            forced_id: The node ID for the single node.
            default_society_template: society template name for loading initial society information. Will apply
                to the Default node.

        Returns:
            An HIVDemographics object
        """
        new_nodes = [HIVNode(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id)]
        return cls(nodes=new_nodes, default_society_template=default_society_template)

    # Disabling these functions (from the super-class, Demographics, to avoid having to test them as there is no
    # current workflow using these routes in initialization.

    @classmethod
    def from_pop_csv(cls):
        """
        This method of building demographics is not available for HIVDemographics
        """
        raise NotImplemented('This method of building demographics is not available for HIVDemographics')
        generic_demog = demographics_module.from_pop_raster_csv(pop_filename_in=pop_filename_in, pop_filename_out=pop_filename_out, site=site)
        nodes = generic_demog.nodes
        return cls(nodes=nodes, idref=site)

    @classmethod
    def from_params(cls):
        """
        This method of building demographics is not available for HIVDemographics
        """
        raise NotImplemented('This method of building demographics is not available for HIVDemographics')
        generic_demog = demographics_module.from_params(tot_pop, num_nodes, frac_rural, id_ref)
        nodes = generic_demog.nodes
        return cls(nodes=nodes, idref=id_ref)
