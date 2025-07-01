# TODO: update any doc strings as needed in here
# TODO: ensure that 'Default' setting takes None or 0 as a node number (None is all-nodes, 0 is UNKNOWN/UNINTERPRETED). Think I did this for None.

import os
from abc import ABC
from collections import defaultdict
from inspect import getfullargspec
from pathlib import Path
from typing import List, Union
import importlib
import json
import pandas as pd

import emod_api
from emod_api.schema_to_class import ReadOnlyDict

import emodpy_hiv.campaign.cascade_of_care as coc
from emodpy.emod_task import EMODTask
from emodpy_hiv.campaign.common import TargetGender
from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.parameterized_call import ParameterizedCall
from emodpy_hiv.reporters.reporters import Reporters


def get_country_class(country_class_name: str):
    """
    Import the countries module and return the class of the country.

    Args:
        country_class_name:
            The name of the country to get the class for.  The name is expected to be exactly like
            like it is in its module.  Countries with more than one word are expected to have an
            underscore ('_') between the words.

            Examples of naming convention:
            - Zambia should be located in the module emodpy_hiv.countries.zambia.zambia
            - South Africa should have a class called South_Africa and be in a module called
            emodpy_hiv.countries.south_africa.south_africa
    """
    module_name = f"emodpy_hiv.countries.{country_class_name.lower()}.{country_class_name.lower()}"
    module_name = module_name.replace(" ", "_")
    country_module = importlib.import_module(module_name)
    country_class = getattr(country_module, country_class_name)
    return country_class


class Country(ABC):
    """
    Country is an "abstract" base class for HIV models of different countries or regions.
    It is intended that a person wanting to develop a new model of a country will either
    subclass Country (or another Country model) and change the things that are different.
    One could use this to ensure that things that are supposed to be the same across all
    of the country models are the same.

    WARNING: Country models are used as the class and not an instance object.  That is,
    one does not create an object like:
    * my_country = MyCountry()
    Instead, they call the classmethods directly from the class like:
    * demographics = MyCountry.build_demographics()
    If someone attempts to create an instance, we want it to throw an exception so people
    don't use it in a way that is not intended.

    WARNING_2: As of Python 3.13, you are not supposed to combine different properties
    with the classmethod property. It should be used by itself.  This is way we are using
    class variables instead of properties.  When we do class inheritance, each subclass
    gets its own instance of the class variables.  For example, if Zambia and Kenya are
    both subclasss of Country, they will have their own instance of country_name even
    though it is declared in Country.  This allows us to set country_name for Zambia
    without it impacting Kenya.

    NOTE: We are using classes instead of modules because we can still get inheritance
    like you'd expect.  For example, with classes if BaseCountry has three methods:
    func_A(), func_B(), and func_C().  Assume func_C() calls both func_A() and func_B().
    Let's alo assume that we create Zambia as a subclass of BaseCountry and have it 
    override func_B().  With classes, when func_C()) is called for Zambia, it will use
    the overridden func_B().  If we tried to do the same thing with modules, func_C()
    would use the func_B() defined in BaseCountry.

    We use Country as a class and this idea of "parameterized calls" so that the country
    can play well with emod_workflow.  The "parameterized calls" need the functions to be
    static and these calls allow us to give a unique name to each parameter.   Unique
    parameter names allow the user to specifically refer to a parameter even when there
    are numerous instances of the object that has the parameter.

    """

    # ------------------------------------------------------------------------------------
    # --- NOTE: I tried using the "Attributes:" stuff that Google says to use, but I kept
    # --- getting this #duplicate object description ... use :noindex: for one of them"
    # --- error message from ReadTheDocs.
    # ------------------------------------------------------------------------------------

    # String: The name of the country model
    country_name = None

    # Float: The calendar year to start the simulation.  This is frequently
    # set to 1960.5 so that there is time to burn-in the population and relationships.
    base_year = 1960.5

    def __init__(self):
        msg =  "You cannot create an instance of a Country.\n" # noqa: E222
        msg += "You must use the class as the object."
        raise NotImplementedError(msg)

    @staticmethod
    def generate_label(relationship_type: str = None,
                       risk_group: str = None,
                       node_ids: Union[List[int], None] = None,
                       node_name: str = None) -> str:
        if node_name is not None:
            label_items = [str(item) for item in [relationship_type, risk_group, node_name] if item is not None]
        else:
            node_ids = [] if node_ids is None else sorted(node_ids)
            label_items = [str(item) for item in [relationship_type, risk_group, *node_ids, node_name] if item is not None]
        label = '-'.join(label_items)
        return label

    @classmethod
    def get_config_parameterized_calls(cls, config: ReadOnlyDict) -> List[ParameterizedCall]:
        """
        Return a list of ParameterizedCall objects that will complete the configuration of an 
        EMOD config object.

        Args
            config: The object to be updated when using instance methods with ParameterizedCall.

        Returns:
            List of ParameterizedCall objects
        """
        parameterized_calls = []

        def set_run_number(config, Run_Number: int = None):
            if Run_Number is not None:
                config.parameters.Run_Number = Run_Number

        pc = ParameterizedCall(func=set_run_number, hyperparameters={'Run_Number': None})
        parameterized_calls.append(pc)
        return parameterized_calls

    @classmethod
    def get_demographics_parameterized_calls(cls, demographics: HIVDemographics) -> List[ParameterizedCall]:
        """
        Return a list of ParameterizedCall objects that will complete the configuration of an
        EMOD demographics object.

        Args
            demographics: If not None, this will be the object that is updated

        Returns:
            List of ParameterizedCall objects
        """
        return []

    @classmethod
    def get_campaign_parameterized_calls(cls, campaign: emod_api.campaign) -> List[ParameterizedCall]:
        """
        Return a list of ParameterizedCall objects that will complete the configuration of an
        EMOD campaign object.

        Args
            campaign: If not None, this will be the object that is updated

        Returns:
            List of ParameterizedCall objects
        """
        return []

    @classmethod
    def initialize_config(cls, schema_path: Union[str, Path]) -> ReadOnlyDict:
        """
        Override this in the subclass to set the default values for the config object as needed.
        """
        config = EMODTask.build_default_config(schema_path=schema_path)
        return config

    @classmethod
    def initialize_demographics(cls) -> HIVDemographics:
        """
        Create the initial demographics object that will be modified by the ParameterizedCall
        objects from **get_demographics_parameterized_calls()**
        """
        demographics = HIVDemographics.from_template_node( pop=10000,
                                                           default_society_template="PFA-Southern-Africa" )

        # TODO:  How to load default node attributes?

        return demographics

    @classmethod
    def initialize_campaign(cls, schema_path: Union[str, Path]) -> emod_api.campaign:
        """
        Create the initial campaign object that will be modified by the ParameterizedCall
        objects from **get_campaign_parameterized_calls()**
        """
        campaign = EMODTask.build_default_campaign(schema_path=schema_path)
        campaign.base_year = cls.base_year
        return campaign

    #
    # Convenience functions for non-EMOD-workflow users below
    #

    @classmethod
    def build_reports(cls, reporters: Reporters) -> Reporters:
        """
        Function that creates reports to be used in the experiment. The function must have Reporters
        object as the parameter and return that object. It is assumed that all the reporters come from the
        reporters that are part of EMOD main code. EMOD also supports reporters as custom plug-in dlls,
        however, not through the current emodpy system.

        Args:
            reporters: The Reporters object to add reports to

        Returns:
            Reporters object
        """
        return reporters

    @classmethod
    def _execute_parameterized_calls_on(cls, obj, parameterized_calls: List[ParameterizedCall]):
        for parameterized_call in parameterized_calls:
            # Now modify the provided object (obj). obj is passed as context to each successive ParameterizedCall.
            prepared_call = parameterized_call.prepare_call()
            prepared_call(obj)

    @classmethod
    def build_config(cls, config: ReadOnlyDict) -> ReadOnlyDict:
        """
        A function that creates a config object that can be used with
        EMODTask.from_defaults().

        Args:
            config(ReadOnlyDict): the config object that will be modified. It has the following structure:
                config.parameters.<parameter_name> , with <parameter_name> being an attribute.
        Returns:
            a config object
        """
        config = cls.initialize_config(schema_path=config["schema_path"])
        cls._execute_parameterized_calls_on(obj=config, parameterized_calls=cls.get_config_parameterized_calls(config=config))
        return config


    @classmethod
    def build_demographics(cls) -> HIVDemographics:
        """
        A function that configures the demographics for EMOD and can be used with
        EMODTask.from_defaults().

        Returns:
            a demographics object
        """
        demographics = cls.initialize_demographics()
        cls._execute_parameterized_calls_on(obj=demographics,
                                            parameterized_calls=cls.get_demographics_parameterized_calls(demographics=demographics))
        return demographics

    @classmethod
    def build_campaign(cls, campaign: emod_api.campaign) -> emod_api.campaign:
        """
        A method to pass into EMODTask to build campaign events for Emod.

        Args:
            campaign(emod_api.campaign): The emod_api campaign object to be modified.
        Returns:
            a campaign object
        """
        campaign = cls.initialize_campaign(schema_path=campaign.schema_path)
        calls = cls.get_campaign_parameterized_calls(campaign=campaign)
        cls._execute_parameterized_calls_on(obj=campaign, parameterized_calls=calls)
        return campaign

    #
    # common functions used for building campaign ParameterizedCalls below
    #


    @staticmethod
    def load_nchooser_distribution_data(file_path: str) -> dict:
        """
        Load target distribution data into a dataframe format that works for Nchooser and group by node_id.
        Args:
            file_path: path to the csv file that contains the data

        Returns:
            dict: a dictionary that has node_id as the key and a dataframe as the value. The dataframe contains the
            distribution data for Nchooser.

        """
        data = pd.read_csv(file_path)
        data_dict = defaultdict(pd.DataFrame)
        for node_id in pd.unique(data['node_set']):
            node_data = data[data['node_set'] == node_id]
            node_dict = {'year': [], 'min_age': [], 'max_age': [], 'n_circumcisions': []}
            for year in pd.unique(node_data['year']):
                year_data = node_data[node_data['year'] == year]
                for _, row in year_data.iterrows():
                    node_dict['year'].append(year)
                    node_dict['min_age'].append(float(row['age_bin'].split(':')[0].replace('[', '')))
                    node_dict['max_age'].append(float(row['age_bin'].split(':')[1].replace(')', '')) - 0.00001)
                    node_dict['n_circumcisions'].append(int(row['n_circumcisions']))
            data_dict[int(node_id)] = pd.DataFrame(node_dict)
        return data_dict

    @classmethod
    def add_historical_vmmc_nchooser(cls,
                                     campaign: emod_api.campaign,
                                     historical_vmmc_data_filepath: str,
                                     historical_vmmc_reduced_acquire: float = 0.6):
        # Load historical vmmc data into data frame
        historical_vmmc_data = cls.load_nchooser_distribution_data(historical_vmmc_data_filepath)
        for node_id in historical_vmmc_data:
            coc.add_historical_vmmc_nchooser(campaign=campaign,
                                             historical_vmmc_distributions_by_time=historical_vmmc_data[node_id],
                                             historical_vmmc_reduced_acquire=historical_vmmc_reduced_acquire,
                                             historical_vmmc_property_restrictions=None,
                                             historical_vmmc_node_ids=[node_id],
                                             has_intervention_name_exclusion=coc.ANY_MC,
                                             event_name=f"NChooser to produce specified number of program VMMCs in node"
                                                        f" {node_id}, {cls.country_name}")

    @classmethod
    def add_traditional_male_circumcision(cls,
                                          campaign: emod_api.campaign,
                                          traditional_male_circumcision_coverage: float = 0.5,  # TODO: what is a meaningful default?
                                          traditional_male_circumcision_reduced_acquire: float = 0.6,
                                          node_ids: Union[List[int], None] = None):
        randomchoice_start_year = 1975
        traditional_male_circumcision_start_year = 1961
        coc.add_traditional_male_circumcision(campaign=campaign,
                                              traditional_male_circumcision_start_year=traditional_male_circumcision_start_year,
                                              randomchoice_start_year=randomchoice_start_year,
                                              traditional_male_circumcision_coverage=traditional_male_circumcision_coverage,
                                              traditional_male_circumcision_reduced_acquire=traditional_male_circumcision_reduced_acquire,
                                              traditional_male_circumcision_node_ids=node_ids)

    @classmethod
    def add_vmmc_reference_tracking(cls, 
                                    campaign: emod_api.campaign, 
                                    tracking_vmmc_reduced_acquire: float = 0.6):
        vmmc_time_value_map = {
            "Times": [2015.9999, 2016, 2021],
            "Values": [0, 0.54, 0.9]  # Zambia values
        }
        coc.add_vmmc_reference_tracking(campaign=campaign,
                                        vmmc_time_value_map=vmmc_time_value_map,
                                        vmmc_reduced_acquire=tracking_vmmc_reduced_acquire,
                                        vmmc_target_min_age=15,
                                        vmmc_target_max_age=15.09,
                                        vmmc_start_year=2015,
                                        vmmc_node_ids=None,  # all nodes
                                        update_period=30.4166666666667)

    @classmethod
    def seed_infections(cls,
                        campaign: emod_api.campaign,
                        node_ids: Union[List[int], None] = None,
                        seeding_start_year: float=1982,
                        seeding_coverage: float = 0.2,
                        seeding_target_min_age: float = 0,
                        seeding_target_max_age: float = 200,
                        seeding_target_gender: TargetGender = TargetGender.ALL):
        # add outbreak individual interventions with coverage 0.1 to all nodes with Risk:HIGH
        coc.seed_infections(campaign=campaign,
                            seeding_node_ids=node_ids,
                            seeding_start_year=seeding_start_year,
                            seeding_coverage=seeding_coverage,
                            seeding_target_min_age=seeding_target_min_age,
                            seeding_target_max_age=seeding_target_max_age,
                            seeding_target_gender=seeding_target_gender,
                            seeding_target_property_restrictions=["Risk:HIGH"])

    @classmethod
    def add_csw(cls,
                campaign: emod_api.campaign,
                csw_male_uptake_coverage: float = 0.1,
                csw_female_uptake_coverage: float = 0.1,  # TODO: meaningful default values?
                node_ids: Union[List[int], None] = None):
        coc.add_csw(campaign=campaign,
                    node_ids=node_ids,
                    male_uptake_coverage=csw_male_uptake_coverage,
                    female_uptake_coverage=csw_female_uptake_coverage)

    @classmethod
    def add_post_debut_coinfection(cls,
                                   campaign: emod_api.campaign,
                                   coinfection_coverage_HIGH: float = 0.3,
                                   coinfection_coverage_MEDIUM: float = 0.3,
                                   coinfection_coverage_LOW: float = 0.1,
                                   node_ids: Union[List[int], None] = None):
        coinfection_risk_to_coverage = {
            'HIGH': coinfection_coverage_HIGH,
            'MEDIUM': coinfection_coverage_MEDIUM,
            'LOW': coinfection_coverage_LOW
        }
        for risk, coverage in coinfection_risk_to_coverage.items():
            coc.add_post_debut_coinfection(campaign=campaign,
                                           coinfection_coverage=coverage,
                                           coinfection_gender=TargetGender.ALL,
                                           coinfection_IP=f'Risk:{risk}',
                                           coinfection_node_ids=node_ids)

    @classmethod
    def add_pmtct(cls, campaign: emod_api.campaign, node_ids: Union[List[int], None] = None):
        cls.add_state_TestingOnANC(campaign, node_ids=node_ids)
        # Testing of children at 6 weeks of age
        cls.add_state_TestingOnChild6w(campaign, node_ids=node_ids)

    @classmethod
    def add_health_care_testing(cls,
                                campaign: emod_api.campaign,
                                hct_delay_to_next_test: List[float],
                                hct_delay_to_next_test_node_ids: List[List[int]],
                                hct_delay_to_next_test_node_names: List[str],
                                hct_start_year: float = 1990,
                                node_ids: Union[List[int], None] = None):

        cls.add_state_HCTUptakeAtDebut(campaign=campaign, start_year=hct_start_year, node_ids=node_ids)

        cls.add_state_HCTUptakePostDebut(campaign=campaign, start_year=hct_start_year, node_ids=node_ids)

        cls.add_state_HCTTestingLoop(campaign=campaign,
                                     hct_delay_to_next_test=hct_delay_to_next_test,
                                     hct_delay_to_next_test_node_ids=hct_delay_to_next_test_node_ids,
                                     hct_delay_to_next_test_node_names=hct_delay_to_next_test_node_names,
                                     start_year=hct_start_year,
                                     node_ids=node_ids)

    @classmethod
    def add_ART_cascade(cls,
                        campaign: emod_api.campaign,
                        art_cascade_start_year: float = 1990,
                        cd4_retention_rate: float = 1,
                        linking_to_pre_art_sigmoid_min: float = 0.7572242198,
                        linking_to_pre_art_sigmoid_max: float = 0.9591484679,
                        linking_to_pre_art_sigmoid_midyear: float = 2006.8336631523,
                        linking_to_pre_art_sigmoid_rate: float = 1.0,
                        pre_staging_retention: float = 0.85,
                        pre_art_retention: float = 0.75,
                        linking_to_art_sigmoid_min: float = 0.0,
                        linking_to_art_sigmoid_max: float = 0.8507390283,
                        linking_to_art_sigmoid_midyear: float = 1997.4462231708,
                        linking_to_art_sigmoid_rate: float = 1.0,
                        art_reenrollment_willingness: float = 0.9,
                        immediate_art_rate: float = 0.1,
                        node_ids: Union[List[int], None] = None):

        cls.add_state_TestingOnSymptomatic(campaign=campaign, start_year=art_cascade_start_year, node_ids=node_ids)

        #
        # ---- BEGIN ART STAGING SECTION ----
        #
        cls.add_state_ARTStagingDiagnosticTest(campaign=campaign, start_year=art_cascade_start_year, node_ids=node_ids)

        cls.add_state_ARTStaging(campaign=campaign, start_year=art_cascade_start_year,
                                 cd4_retention_rate=cd4_retention_rate,
                                 pre_staging_retention=pre_staging_retention,
                                 node_ids=node_ids)
        #
        # ---- BEGIN PRE-ART ----
        #
        # chance of linking to pre-ART
        cls.add_state_LinkingToPreART(campaign=campaign,
                                      start_year=art_cascade_start_year,
                                      sigmoid_min=linking_to_pre_art_sigmoid_min,
                                      sigmoid_max=linking_to_pre_art_sigmoid_max,
                                      sigmoid_midyear=linking_to_pre_art_sigmoid_midyear,
                                      sigmoid_rate=linking_to_pre_art_sigmoid_rate,
                                      node_ids=node_ids)

        # ensuring each agent continues this cascade once per timestep
        cls.add_state_OnPreART(campaign=campaign, start_year=art_cascade_start_year, pre_art_retention=pre_art_retention,
                               node_ids=node_ids)
        #
        # ---- BEGIN ART LINKING ----
        #
        cls.add_state_LinkingToART(campaign=campaign,
                                   start_year=art_cascade_start_year,
                                   sigmoid_min=linking_to_art_sigmoid_min,
                                   sigmoid_max=linking_to_art_sigmoid_max,
                                   sigmoid_midyear=linking_to_art_sigmoid_midyear,
                                   sigmoid_rate=linking_to_art_sigmoid_rate,
                                   node_ids=node_ids)

        # decide to initiate ART now or later
        cls.add_state_OnART(campaign=campaign, start_year=art_cascade_start_year,
                            art_reenrollment_willingness=art_reenrollment_willingness,
                            immediate_art_rate=immediate_art_rate,
                            node_ids=node_ids)
        #
        cls.add_state_LostForever(campaign=campaign, start_year=art_cascade_start_year, node_ids=node_ids)

    @classmethod
    def add_state_TestingOnANC(cls, campaign: emod_api.campaign, node_ids: Union[List[int], None] = None):
        start_year = 1990
        coverage = 1.0
        sigmoid_min = 0
        sigmoid_max = 0.975
        sigmoid_midyear = 2005.87
        sigmoid_rate = 0.7136
        link_to_ART_rate = 0.8
        treatment_a_efficacy = 0.9
        treatment_b_efficacy = 0.96667
        sdNVP_efficacy = 0.66
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING,
                                    coc.CascadeState.TESTING_ON_SYMPTOMATIC]
        property_restrictions = 'Accessibility:Yes'

        coc.add_state_TestingOnANC(campaign=campaign,
                                   disqualifying_properties=disqualifying_properties,
                                   coverage=coverage,
                                   link_to_ART_rate=link_to_ART_rate,
                                   node_ids=node_ids,
                                   sigmoid_min=sigmoid_min,
                                   sigmoid_max=sigmoid_max,
                                   sigmoid_midyear=sigmoid_midyear,
                                   sigmoid_rate=sigmoid_rate,
                                   treatment_a_efficacy=treatment_a_efficacy,
                                   treatment_b_efficacy=treatment_b_efficacy,
                                   sdNVP_efficacy=sdNVP_efficacy,
                                   start_year=start_year,
                                   property_restrictions=property_restrictions)

    @classmethod
    def add_state_TestingOnChild6w(cls, campaign: emod_api.campaign, node_ids: Union[List[int], None] = None):
        child_testing_start_year = 2004
        child_testing_time_value_map = {"Times": [2004, 2005, 2006, 2008, 2009],  # TODO: move to Zambia?
                                        "Values": [0, 0.03, 0.1, 0.2, 0.3365]}
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING,
                                    coc.CascadeState.TESTING_ON_SYMPTOMATIC]
        property_restrictions = 'Accessibility:Yes'
        coc.add_state_TestingOnChild6w(campaign=campaign,
                                       disqualifying_properties=disqualifying_properties,
                                       time_value_map=child_testing_time_value_map,
                                       node_ids=node_ids,
                                       property_restrictions=property_restrictions,
                                       start_year=child_testing_start_year)

    @classmethod
    def add_state_HCTUptakeAtDebut(cls, 
                                   campaign: emod_api.campaign, 
                                   start_year: float,
                                   node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING]
        coc.add_state_HCTUptakeAtDebut(campaign=campaign,
                                       disqualifying_properties=disqualifying_properties,
                                       node_ids=node_ids,
                                       start_year=start_year)

    @classmethod
    def add_state_HCTUptakePostDebut(cls, 
                                     campaign: emod_api.campaign,
                                     start_year: float,
                                     node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING]
        coc.add_state_HCTUptakePostDebut(campaign=campaign,
                                         disqualifying_properties=disqualifying_properties,
                                         node_ids=node_ids,
                                         hct_reentry_rate=1,
                                         start_year=start_year,
                                         tvmap_test_for_enter_HCT_testing_loop=coc.all_negative_time_value_map)

    @classmethod
    def add_state_HCTTestingLoop(cls, campaign: emod_api.campaign,
                                 start_year: float,
                                 hct_delay_to_next_test: List[float],
                                 hct_delay_to_next_test_node_ids: List[List[int]],
                                 hct_delay_to_next_test_node_names: List[str],
                                 node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING]
        coc.add_state_HCTTestingLoop(campaign=campaign,
                                     disqualifying_properties=disqualifying_properties,
                                     start_year=start_year,
                                     hct_retention_rate=0.95,
                                     tvmap_consider_immediate_ART=coc.all_negative_time_value_map,
                                     hct_delay_to_next_test=hct_delay_to_next_test,
                                     hct_delay_to_next_test_node_ids=hct_delay_to_next_test_node_ids,
                                     hct_delay_to_next_test_node_names=hct_delay_to_next_test_node_names,
                                     node_ids=node_ids)

    @classmethod
    def add_state_TestingOnSymptomatic(cls, 
                                       campaign: emod_api.campaign, 
                                       start_year: float,
                                       node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING]
        coc.add_state_TestingOnSymptomatic(campaign=campaign,
                                           disqualifying_properties=disqualifying_properties,
                                           start_year=start_year,
                                           node_ids=node_ids,
                                           tvmap_increased_symptomatic_presentation=coc.all_negative_time_value_map)

    @classmethod
    def add_state_ARTStagingDiagnosticTest(cls,
                                           campaign: emod_api.campaign,
                                           start_year: float,
                                           node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART]
        coc.add_state_ARTStagingDiagnosticTest(campaign=campaign,
                                               disqualifying_properties=disqualifying_properties,
                                               start_year=start_year,
                                               node_ids=node_ids)

    @classmethod
    def add_state_ARTStaging(cls,
                             campaign: emod_api.campaign,
                             start_year: float,
                             cd4_retention_rate: float = 1,
                             pre_staging_retention: float = 0.85,
                             node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART]
        coc.add_state_ARTStaging(campaign=campaign,
                                 disqualifying_properties=disqualifying_properties,
                                 start_year=start_year,
                                 node_ids=node_ids,
                                 pre_staging_retention=pre_staging_retention,
                                 cd4_retention_rate=cd4_retention_rate)

    @classmethod
    def add_state_LinkingToPreART(cls, 
                                  campaign: emod_api.campaign, 
                                  start_year: float,
                                  sigmoid_min: float = 0.7572242198,
                                  sigmoid_max: float = 0.9591484679,
                                  sigmoid_midyear: float = 2006.8336631523,
                                  sigmoid_rate: float = 1.0,
                                  node_ids: Union[List[int], None] = None):
        disqualifying_properties_pre_art_linking = [coc.CascadeState.LOST_FOREVER,
                                                    coc.CascadeState.ON_ART,
                                                    coc.CascadeState.LINKING_TO_ART,
                                                    coc.CascadeState.ON_PRE_ART]
        coc.add_state_LinkingToPreART(campaign=campaign,
                                      disqualifying_properties=disqualifying_properties_pre_art_linking,
                                      start_year=start_year,
                                      sigmoid_min=sigmoid_min,
                                      sigmoid_max=sigmoid_max,
                                      sigmoid_midyear=sigmoid_midyear,
                                      sigmoid_rate=sigmoid_rate,
                                      node_ids=node_ids)

    @classmethod
    def add_state_OnPreART(cls,
                           campaign: emod_api.campaign,
                           start_year: float,
                           pre_art_retention: float = 0.75,
                           node_ids: Union[List[int], None] = None):
        disqualifying_properties_pre_art = [coc.CascadeState.LOST_FOREVER,
                                            coc.CascadeState.ON_ART,
                                            coc.CascadeState.LINKING_TO_ART]
        coc.add_state_OnPreART(campaign=campaign,
                               node_ids=node_ids,
                               pre_art_retention=pre_art_retention,
                               disqualifying_properties=disqualifying_properties_pre_art,
                               start_year=start_year)

    @classmethod
    def add_state_LinkingToART(cls, 
                               campaign: emod_api.campaign, 
                               start_year: float,
                               sigmoid_min: float = 0.0,
                               sigmoid_max: float = 0.8507390283,
                               sigmoid_midyear: float = 1997.4462231708,
                               sigmoid_rate: float = 1.0,
                               node_ids: Union[List[int], None] = None):
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER, coc.CascadeState.ON_ART]
        coc.add_state_LinkingToART(campaign=campaign,
                                   node_ids=node_ids,
                                   disqualifying_properties=disqualifying_properties,
                                   start_year=start_year,
                                   sigmoid_min=sigmoid_min,
                                   sigmoid_max=sigmoid_max,
                                   sigmoid_midyear=sigmoid_midyear,
                                   sigmoid_rate=sigmoid_rate)

    @classmethod
    def add_state_OnART(cls,
                        campaign: emod_api.campaign,
                        start_year: float,
                        art_reenrollment_willingness: float = 0.9,
                        immediate_art_rate: float = 0.1,
                        node_ids: Union[List[int], None] = None):
        tvmap_immediate_ART_restart = coc.all_negative_time_value_map
        tvmap_reconsider_lost_forever = coc.all_negative_time_value_map
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER]
        coc.add_state_OnART(campaign=campaign,
                            art_reenrollment_willingness=art_reenrollment_willingness,
                            immediate_art_rate=immediate_art_rate,
                            node_ids=node_ids,
                            disqualifying_properties=disqualifying_properties,
                            start_year=start_year,
                            tvmap_immediate_ART_restart=tvmap_immediate_ART_restart,
                            tvmap_reconsider_lost_forever=tvmap_reconsider_lost_forever)

    @classmethod
    def add_state_LostForever(cls, 
                              campaign: emod_api.campaign, 
                              start_year: float,
                              node_ids: Union[List[int], None] = None):
        coc.add_state_LostForever(campaign=campaign,
                                  node_ids=node_ids,
                                  start_year=start_year)

