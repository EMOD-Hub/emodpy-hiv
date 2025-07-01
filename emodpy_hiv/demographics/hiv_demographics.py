"""
This module contains the classes and functions for creating demographics files
for HIV simulations. For more information on |EMOD_s| demographics files,
see :doc:`emod-hiv:emod/software-demographics`.
"""
import pandas as pd

from typing import List

from emod_api.demographics.fertility_distribution import FertilityDistribution
from emodpy.demographics.demographics import Demographics
from emod_api.demographics.PropertiesAndAttributes import IndividualProperty
from emodpy.utils.distributions import UniformDistribution

from emodpy_hiv.demographics import DemographicsTemplates as hiv_dt
from emodpy_hiv.demographics.assortivity import Assortivity
from emodpy_hiv.demographics.hiv_node import HIVNode
from emodpy_hiv.demographics.society import Society
from emodpy_hiv.demographics.year_age_rate import YearAgeRate


class HIVDemographics(Demographics):
    def __init__(self, nodes: List[HIVNode], default_society_template: str = None):
        """
        This class is derived from :py:class:`emodpy:emodpy.demographics.demographics.Demographics` adding HIV-
        specific features and sets certain defaults for HIV in construction.

        Args:
            nodes: A list of (non-Default) HIVNode objects
            default_society_template: society template name for loading initial society information. Will apply
                to the Default node. Default society template is 'PFA-Southern-Africa'.

        Returns:
            an HIVDemographics object
         """
        # we need to generate the default node before calling super() because we need it to be an HIVNode, not Node
        society_dict = hiv_dt.get_society_dict(society_name=default_society_template)
        society = Society.from_dict(d=society_dict)
        default_node = HIVNode(name='Default', lat=0, lon=0, pop=0, forced_id=0, society=society)

        super().__init__(nodes=nodes, idref="EMOD-HIV world", default_node=default_node)

        # default individual properties for HIV
        # We are assuming Risk-based assortivity
        self.add_or_update_initial_risk_distribution(distribution=[0.6669671396606822, 0.3330328603393178, 0])

        # default individual attributes for HIV
        # Uniform age distribution by default
        initial_age_distribution = UniformDistribution(uniform_min=0, uniform_max=18250)
        self.set_age_distribution(distribution=initial_age_distribution)

        # Node attributes copied from Demographics.SetDefaultNodeAttributes (which uses self.raw, which cannot
        #   be used with HIVDemographics). These may or may not be needed by HIV.
        default_node.node_attributes.altitude = 0
        default_node.node_attributes.airport = 1
        default_node.node_attributes.region = 1
        default_node.node_attributes.seaport = 1

    @property
    def raw(self):
        raise AttributeError("raw is not a valid attribute for HIVDemographics objects")

    @raw.setter
    def raw(self, value):
        raise AttributeError("raw is not a valid attribute for HIVDemographics objects")

    def set_fertility_distribution(self,
                                   distribution: FertilityDistribution,
                                   node_ids: List[int] = None) -> None:
        """
        Sets a fertility distribution on the demographics object. Automatically handles any necessary config updates.
        Args:
            distribution: The distribution to set. Must be a FertilityDistribution object for a complex distribution.
            node_ids: The node id(s) to apply changes to. None or 0 means the default node.
        Returns:
            Nothing
        """
        from emod_api.demographics.DemographicsTemplates import _set_fertility_age_year
        self._set_distribution(distribution=distribution,
                               use_case='fertility',
                               complex_distribution_implicits=[_set_fertility_age_year],
                               node_ids=node_ids)

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

    def AddIndividualPropertyAndHINT(self, Property: str, Values: List[str], InitialDistribution: List[float] = None,
                                     TransmissionMatrix: List[List[float]] = None, Transitions: List = None,
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
                to the Default node. Default society template is 'PFA-Southern-Africa'.

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
                to the Default node. Default society template is 'PFA-Southern-Africa'.

        Returns:
            An HIVDemographics object
        """
        new_nodes = [HIVNode(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id)]
        return cls(nodes=new_nodes, default_society_template=default_society_template)

    # Disabling these functions (from the super-classes, to avoid having to test them as there is no
    # current workflow using these routes in initialization.

    @classmethod
    def from_pop_csv(cls):
        """
        This method of building demographics is not available for HIVDemographics
        """
        raise NotImplemented('This method of building demographics is not available for HIVDemographics')

    @classmethod
    def from_params(cls):
        """
        This method of building demographics is not available for HIVDemographics
        """
        raise NotImplemented('This method of building demographics is not available for HIVDemographics')

    @classmethod
    def from_year_age_rate_data(cls,
                                pop_df:               pd.DataFrame,  # noqa: E241 - node_id, name, population
                                age_distribution_yar: YearAgeRate,
                                fertility_yar:        YearAgeRate,   # noqa: E241
                                male_mortality_yar:   YearAgeRate,   # noqa: E241
                                female_mortality_yar: YearAgeRate,
                                society: Society = None):
        """
        Create an HIVDemographics object using YearAgeRate data for the initial age distribution,
        fertility, and mortality.

        Args:
            pop_df: A pandas dataframe with columns "node_id", "name", and "population" where:
                "node_id" is an unsigned integer ranging from 1 to  4,294,967,295
                "name" is a string that one can use when creating the demographics
                "population" is an unsigned integer ranging from 0 to  4,294,967,295
            age_distribution_yar: A YearAgeRate object containing data for the ages of the
                initial population
            fertility_yar: A YearAgeRate object containing the fertility rates to use during
                the simulation
            male_mortality_yar: A YearAgeRate object containing the male mortality rates to use
                during the simulation
            female_mortality_yar: A YearAgeRate object containing the fwmale mortality rates to use
                during the simulation
            society: A Society object defining how people form relationships and have coital acts.
                Defaults to None (to be set later).

        Returns:
            An HIVDemographics object
        """
        demog = cls.from_population_dataframe(df=pop_df)

        age_dist_list = age_distribution_yar.to_age_distributions()
        for node_id, age_dist in age_dist_list:
            demog.set_age_distribution(distribution=age_dist, node_ids=[node_id])

        fert_dist_list = fertility_yar.to_fertility_distributions()
        for node_id, fert_dist in fert_dist_list:
            demog.set_fertility_distribution(distribution=fert_dist, node_ids=[node_id])

        male_mort_dist_dict = male_mortality_yar.to_mortality_distributions()
        female_mort_dist_dict = female_mortality_yar.to_mortality_distributions()
        for node_id, male_mort_dist in male_mort_dist_dict.items():
            demog.set_mortality_distribution(distribution_male=male_mort_dist,
                                             distribution_female=female_mort_dist_dict[node_id],
                                             node_ids=[node_id])

        if society:
            demog.society = society

        return demog
