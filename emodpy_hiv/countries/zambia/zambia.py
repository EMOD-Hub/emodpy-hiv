from importlib import resources
from pathlib import Path
from typing import List, Union
import copy

import pandas as pd

import emod_api
from emod_api.schema_to_class import ReadOnlyDict

import emodpy_hiv.countries.zambia as zambia_data
from emodpy_hiv.country_model import Country

import emodpy_hiv.demographics.infer_natural_mortality as infer

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.demographics.relationship_types import RelationshipTypes
from emodpy_hiv.demographics.risk_groups import RiskGroups
from emodpy_hiv.parameterized_call import ParameterizedCall
from emodpy_hiv.reporters.reporters import (Reporters, ReportFilter, ReportHIVInfection, ReportHIVART,
                                            ReportHIVMortality, ReportHIVByAgeAndGender,
                                            ReportTransmission, ReportRelationshipStart, InsetChart)

COMMERCIAL = RelationshipTypes.commercial.value
TRANSITORY = RelationshipTypes.transitory.value
INFORMAL   = RelationshipTypes.informal.value   # noqa: E221
MARITAL    = RelationshipTypes.marital.value    # noqa: E221

LOW    = RiskGroups.low.value    # noqa: E221
MEDIUM = RiskGroups.medium.value
HIGH   = RiskGroups.high.value   # noqa: E221

# The nodes for the country with names and initial population.
# NOTE: In the future, please add information about there this initial population data comes from.
NODE_DATA = [
    {"node_id":  1, "name": "Central",      "population": 304498},  # noqa: E241
    {"node_id":  2, "name": "Copperbelt",   "population": 459461},  # noqa: E241
    {"node_id":  3, "name": "Eastern",      "population": 371018},  # noqa: E241
    {"node_id":  4, "name": "Luapula",      "population": 231074},  # noqa: E241
    {"node_id":  5, "name": "Lusaka",       "population": 510456},  # noqa: E241
    {"node_id":  6, "name": "Muchinga",     "population": 165784},  # noqa: E241
    {"node_id":  7, "name": "Northwestern", "population": 169368},  # noqa: E241
    {"node_id":  8, "name": "Northern",     "population": 257607},  # noqa: E241
    {"node_id":  9, "name": "Southern",     "population": 370381},  # noqa: E241
    {"node_id": 10, "name": "Western",      "population": 210352}   # noqa: E241
]

# Convert the data above so that we can use the country name
# when creating labels for parameters.
NODE_ID_TO_NODE_NAME = {node_dict["node_id"]: node_dict["name"] for node_dict in NODE_DATA}


class Zambia(Country):
    """
    Zambia country model class. This class is a subclass of the Country class and implements the build_campaign method
    to build campaign object to be used with EMODTask.

    Example:
        >>> from emodpy_hiv.countries.zambia import Zambia
        >>> from emodpy.emod_task import EMODTask
        >>> import manifest
        >>> from functools import partial
        >>> # Define a campaign_builder function to pass in the required arguments for the Zambia.build_campaign() method.
        >>> def campaign_builder():
        >>>     return Zambia.build_campaign(schema_path=manifest.schema_file, base_year=Zambia.base_year)
        >>> # Alternatively, you can use the partial function to pass in the required arguments for the
        >>> # Zambia.build_campaign() method. For example:
        >>> # campaign_builder = partial(Zambia.build_campaign, schema_path=manifest.schema_file, base_year=Zambia.base_year)
        >>> # Create an EMODTask object using the campaign_builder function
        >>> task = EMODTask.from_defaults(config_path="config.json",
        >>>                               eradication_path=manifest.eradication_path,
        >>>                               campaign_builder=campaign_builder, ...)
    """

    country_name = "Zambia"
    _historical_vmmc_data_file = resources.files(zambia_data).joinpath("historical_vmmc_data.csv")
    _inital_demog_cache = None

    @classmethod
    def initialize_config(cls, schema_path: Union[str, Path]) -> ReadOnlyDict:
        config = super().initialize_config(schema_path=schema_path)

        config.parameters.Simulation_Type = "HIV_SIM"
        config.parameters.Simulation_Duration = 99.5 * 365
        config.parameters.Simulation_Timestep = 30.4166666666667

        # Reduce the initial population so tutorial can double it
        config.parameters.x_Base_Population = 0.002  # 0.005

        config.parameters.Start_Time = 0
        config.parameters.AIDS_Duration_In_Months = 9
        config.parameters.AIDS_Stage_Infectivity_Multiplier = 4.5
        config.parameters.Acute_Duration_In_Months = 2.9
        config.parameters.Acute_Stage_Infectivity_Multiplier = 26
        config.parameters.Age_Initialization_Distribution_Type = "DISTRIBUTION_COMPLEX"
        config.parameters.Base_Individual_Sample_Rate = 1
        config.parameters.Base_Infectivity = 0.00065805
        config.parameters.Base_Year = 1960.5
        config.parameters.Birth_Rate_Dependence = "INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR"
        config.parameters.Birth_Rate_Time_Dependence = "NONE"
        config.parameters.CD4_At_Death_LogLogistic_Heterogeneity = 0.7
        config.parameters.CD4_At_Death_LogLogistic_Scale = 2.96
        config.parameters.CD4_Post_Infection_Weibull_Heterogeneity = 0.2756
        config.parameters.CD4_Post_Infection_Weibull_Scale = 560.43
        config.parameters.Coital_Dilution_Factor_2_Partners = 0.75
        config.parameters.Coital_Dilution_Factor_3_Partners = 0.6
        config.parameters.Coital_Dilution_Factor_4_Plus_Partners = 0.45
        config.parameters.Condom_Transmission_Blocking_Probability = 0.8
        config.parameters.Days_Between_Symptomatic_And_Death_Weibull_Heterogeneity = 0.5
        config.parameters.Days_Between_Symptomatic_And_Death_Weibull_Scale = 618.341625
        config.parameters.Death_Rate_Dependence = "NONDISEASE_MORTALITY_BY_YEAR_AND_AGE_FOR_EACH_GENDER"
        config.parameters.Enable_Aging = 1
        config.parameters.Enable_Birth = 1
        config.parameters.Enable_Coital_Dilution = 1
        config.parameters.Enable_Demographics_Reporting = 0  # Demographics reporting is on by default, turning it off
        config.parameters.Enable_Demographics_Birth = 0
        config.parameters.Enable_Infectivity_Reservoir = 0
        config.parameters.Enable_Maternal_Protection = 0
        config.parameters.Enable_Natural_Mortality = 1
        config.parameters.HIV_Adult_Survival_Scale_Parameter_Intercept = 21.182
        config.parameters.HIV_Adult_Survival_Scale_Parameter_Slope = -0.2717
        config.parameters.HIV_Adult_Survival_Shape_Parameter = 2
        config.parameters.HIV_Age_Max_for_Adult_Age_Dependent_Survival = 50
        config.parameters.HIV_Age_Max_for_Child_Survival_Function = 15
        config.parameters.HIV_Child_Survival_Rapid_Progressor_Fraction = 0.57
        config.parameters.HIV_Child_Survival_Rapid_Progressor_Rate = 1.52
        config.parameters.HIV_Child_Survival_Slow_Progressor_Scale = 16
        config.parameters.HIV_Child_Survival_Slow_Progressor_Shape = 2.7
        config.parameters.Heterogeneous_Infectiousness_LogNormal_Scale = 0
        config.parameters.Incubation_Period_Constant = 0
        config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
        config.parameters.Individual_Sampling_Type = "FIXED_SAMPLING"
        config.parameters.Infection_Updates_Per_Timestep = 1
        config.parameters.Infectivity_Scale_Type = "CONSTANT_INFECTIVITY"
        config.parameters.Male_To_Female_Relative_Infectivity_Ages = [0, 15, 25]
        config.parameters.Male_To_Female_Relative_Infectivity_Multipliers = [
            2.26154624,
            2.26154624,
            1.112477558
        ]
        config.parameters.Maternal_Infection_Transmission_Probability = 0.3
        config.parameters.Maternal_Transmission_ART_Multiplier = 0.03334
        config.parameters.Migration_Model = "NO_MIGRATION"
        config.parameters.Min_Days_Between_Adding_Relationships = 0
        config.parameters.Node_Grid_Size = 0.009
        config.parameters.PFA_Burnin_Duration_In_Days = 5475
        config.parameters.PFA_Cum_Prob_Selection_Threshold = 0.2
        config.parameters.Population_Density_Infectivity_Correction = "CONSTANT_INFECTIVITY"
        config.parameters.Population_Scale_Type = "FIXED_SCALING"
        config.parameters.Run_Number = 1
        config.parameters.STI_Coinfection_Acquisition_Multiplier = 5.5
        config.parameters.STI_Coinfection_Transmission_Multiplier = 5.5
        config.parameters.Serialized_Population_Reading_Type = "NONE"
        config.parameters.Serialized_Population_Writing_Type = "NONE"
        config.parameters.Sexual_Debut_Age_Setting_Type = "WEIBULL"
        config.parameters.Sexual_Debut_Age_Female_Weibull_Heterogeneity = 0.22108015674142
        config.parameters.Sexual_Debut_Age_Female_Weibull_Scale = 19.9609856656853
        config.parameters.Sexual_Debut_Age_Male_Weibull_Heterogeneity = 0.165108885953777
        config.parameters.Sexual_Debut_Age_Male_Weibull_Scale = 16.8039276633964
        config.parameters.Sexual_Debut_Age_Min = 13

        config.parameters["logLevel_InfectionHIV"] = "ERROR"
        config.parameters["logLevel_Instrumentation"] = "INFO"
        config.parameters["logLevel_Memory"] = "INFO"
        config.parameters["logLevel_OutbreakIndividual"] = "ERROR"
        config.parameters["logLevel_Simulation"] = "INFO"
        config.parameters["logLevel_SusceptibilityHIV"] = "ERROR"
        config.parameters["logLevel_AntiretroviralTherapy"] = "ERROR"
        config.parameters["logLevel_default"] = "WARNING"

        return config

    @classmethod
    def initialize_campaign(cls, schema_path: Union[str, Path]) -> emod_api.campaign:
        campaign = super().initialize_campaign(schema_path=schema_path)
        return campaign

    #
    # Campaign building below
    #

    @classmethod
    def add_male_circumcision_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []

        # ---- Add historical vmmc NChooser events to campaign ----
        non_hp = {'historical_vmmc_data_filepath': cls._historical_vmmc_data_file}
        hp = {'historical_vmmc_reduced_acquire': None}
        pc = ParameterizedCall(func=cls.add_historical_vmmc_nchooser, non_hyperparameters=non_hp, hyperparameters=hp)
        parameterized_calls.append(pc)

        # ---- Add traditional male circumcision to campaign ----
        traditional_male_circumcision_coverage_by_node = {
            1: 0.054978651,
            2: 0.139462861,
            3: 0.028676043,
            4: 0.091349358,
            5: 0.12318707,
            6: 0.039308099,
            7: 0.727917322,
            8: 0.041105263,
            9: 0.044388102,
            10: 0.398239794
        }

        for node_id, coverage in traditional_male_circumcision_coverage_by_node.items():
            hp = {
                'traditional_male_circumcision_coverage': coverage,
                'traditional_male_circumcision_reduced_acquire': None
            }
            pc = ParameterizedCall(func=cls.add_traditional_male_circumcision,
                                   non_hyperparameters={'node_ids': [node_id]},
                                   hyperparameters=hp,
                                   label=NODE_ID_TO_NODE_NAME[node_id])
            parameterized_calls.append(pc)

        # ---- Add (VMMC) reference tracking to campaign ----
        pc = ParameterizedCall(func=cls.add_vmmc_reference_tracking,
                               hyperparameters={'tracking_vmmc_reduced_acquire': None})
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_pmtct_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []

        pc = ParameterizedCall(func=cls.add_pmtct)
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_seed_infections_parameterized_calls(cls) -> List[ParameterizedCall]:
        seeding_data = []
        seeding_data.append({"node_id":  1, "start_year": 1975.073829, "coverage": 0.032635773}) # noqa: E241
        seeding_data.append({"node_id":  2, "start_year": 1978.497227, "coverage": 0.04084491 }) # noqa: E241, E202
        seeding_data.append({"node_id":  3, "start_year": 1985.330191, "coverage": 0.214647592}) # noqa: E241
        seeding_data.append({"node_id":  4, "start_year": 1970,        "coverage": 0.104800623}) # noqa: E241
        seeding_data.append({"node_id":  5, "start_year": 1970,        "coverage": 0.24472244 }) # noqa: E241, E202
        seeding_data.append({"node_id":  6, "start_year": 1970.122473, "coverage": 0.01       }) # noqa: E241, E202
        seeding_data.append({"node_id":  7, "start_year": 1980.368638, "coverage": 0.092125326}) # noqa: E241
        seeding_data.append({"node_id":  8, "start_year": 1978.154478, "coverage": 0.016020197}) # noqa: E241
        seeding_data.append({"node_id":  9, "start_year": 1982.580456, "coverage": 0.113565582}) # noqa: E241
        seeding_data.append({"node_id": 10, "start_year": 1979.359163, "coverage": 0.332609343})

        parameterized_calls = []
        for data in seeding_data:
            hp = {'seeding_start_year': data["start_year"], 'seeding_coverage': data["coverage"]}
            nhp = {'node_ids': [data["node_id"]]}
            pc = ParameterizedCall(func=cls.seed_infections,
                                   non_hyperparameters=nhp,
                                   hyperparameters=hp,
                                   label=NODE_ID_TO_NODE_NAME[data["node_id"]])
            parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_csw_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []

        pc = ParameterizedCall(func=cls.add_csw,
                               non_hyperparameters={'node_ids': [1, 2, 3, 7, 9]},
                               hyperparameters={'csw_male_uptake_coverage': 0.195, 'csw_female_uptake_coverage': 0.125},
                               label='nodeset1')
        parameterized_calls.append(pc)

        pc = ParameterizedCall(func=cls.add_csw,
                               non_hyperparameters={'node_ids': [4, 5, 6, 8, 10]},
                               hyperparameters={'csw_male_uptake_coverage': 0.0781, 'csw_female_uptake_coverage': 0.05},
                               label='nodeset2')
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_post_debut_coinfection_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []

        hp = {'coinfection_coverage_HIGH': None, 'coinfection_coverage_MEDIUM': None, 'coinfection_coverage_LOW': None}
        pc = ParameterizedCall(func=cls.add_post_debut_coinfection, hyperparameters=hp)
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_health_care_testing_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []
        non_hyperparameters = {
            'hct_delay_to_next_test': [730, 365, 1100],
            'hct_delay_to_next_test_node_ids': [[1, 2, 3, 4, 6, 7], [5, 9, 10], [8]],
            'hct_delay_to_next_test_node_names': ['Default', 'Lusaka, Southern, Western', 'Northern']
        }
        pc = ParameterizedCall(func=cls.add_health_care_testing,
                               non_hyperparameters=non_hyperparameters,
                               hyperparameters={'hct_start_year': None})
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_ART_cascade_parameterized_calls(cls) -> List[ParameterizedCall]:
        parameterized_calls = []

        hp = {
            'art_cascade_start_year': None,
            'cd4_retention_rate': None,
            'linking_to_pre_art_sigmoid_min': 0.824382156,
            'linking_to_pre_art_sigmoid_max': 0.959334475,
            'linking_to_pre_art_sigmoid_midyear': 2008.506768,
            'linking_to_pre_art_sigmoid_rate': None,
            'pre_staging_retention': None,
            'pre_art_retention': None,
            'linking_to_art_sigmoid_min': None,
            'linking_to_art_sigmoid_max': 0.90041509,
            'linking_to_art_sigmoid_midyear': 2001.053678,
            'linking_to_art_sigmoid_rate': None,
            'art_reenrollment_willingness': None,
            'immediate_art_rate': None
        }
        pc = ParameterizedCall(func=cls.add_ART_cascade, hyperparameters=hp)
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def get_campaign_parameterized_calls(cls, campaign: emod_api.campaign) -> List[ParameterizedCall]:
        parameterized_calls = super().get_campaign_parameterized_calls(campaign=campaign)

        # ---- Add male circumcision to campaign -----
        # This block contains 3 chunk of events: historical vmmc NChooser, traditional male circumcision and VMMC with
        # reference tracking.
        parameterized_calls.extend(cls.add_male_circumcision_parameterized_calls())
        # ---- Add prevention of mother-to-child transmission (PMTCT) to campaign ----
        # This pmtct block contains 2 Cascade states: TestingOnANC and TestingOnChild6w
        parameterized_calls.extend(cls.add_pmtct_parameterized_calls())
        # ---- Add OutbreakIndividual interventions to campaign ----
        parameterized_calls.extend(cls.add_seed_infections_parameterized_calls())
        # ---- Add commercial sex worker (CSW) uptake and dropout (with delays) for men and women to campaign ----
        parameterized_calls.extend(cls.add_csw_parameterized_calls())
        # ---- Add co-infections post sexual debut to campaign ----
        parameterized_calls.extend(cls.add_post_debut_coinfection_parameterized_calls())
        # ---- Add health care testing loops to campaign ----
        # This health care testing block contains 3 Cascade states: HCTUptakeAtDebut, HCTUptakePostDebut and
        # HCTTestingLoop
        parameterized_calls.extend(cls.add_health_care_testing_parameterized_calls())
        # ---- Add Antiretroviral Therapy (ART) Cascade to campaign ----
        # This ART Cascade block contains 8 Cascade states: TestingOnSymptomatic, ARTStagingDiagnosticTest, ARTStaging
        # LinkingToPreART, OnPreART, LinkingToART, OnART and LostForever
        parameterized_calls.extend(cls.add_ART_cascade_parameterized_calls())

        return parameterized_calls

    #
    # Demographics building below
    #

    @classmethod
    def initialize_demographics(cls) -> HIVDemographics:
        import emodpy_hiv.demographics.un_world_pop as unwp

        # ------------------------------------------------------------------------------------
        # --- The spreadsheets are large and reading/loading them can take many seconds.
        # --- Hence, we cache the initial instance of the demographics so that new versions
        # --- don't have re-read the spreadsheets.
        # ------------------------------------------------------------------------------------
        if cls._inital_demog_cache:
            return copy.deepcopy(cls._inital_demog_cache)

        # -------------------------------------------------------
        # --- Initial population has data for different nodes so
        # --- we can get use data from UN World Pop
        # -------------------------------------------------------
        pop_df = pd.DataFrame(NODE_DATA)

        uwp_country = "Zambia"
        uwp_version = "2015"

        total_pop, age_distribution_yar = unwp.extract_population_by_age_and_distribution(country =uwp_country, # noqa: E221, E251
                                                                                          version =uwp_version, # noqa: E221, E251
                                                                                          year    =1960)        # noqa: E221, E251

        fertility_yar        = unwp.extract_fertility(country=uwp_country, version=uwp_version)                  # noqa: E241, E221
        male_mortality_yar   = unwp.extract_mortality(country=uwp_country, version=uwp_version, gender="male"  ) # noqa: E241, E221
        female_mortality_yar = unwp.extract_mortality(country=uwp_country, version=uwp_version, gender="female")

        # -----------------------------------------------------------------------------------------
        # --- Need a longer fitting interval to flatten natural deaths under the peak in HIV deaths
        # -----------------------------------------------------------------------------------------
        male_mortality_yar   = infer.infer_natural_mortality(male_mortality_yar,   interval_fit=(1950, 1975)) # noqa: E241, E221
        female_mortality_yar = infer.infer_natural_mortality(female_mortality_yar, interval_fit=(1950, 1975))

        demog = HIVDemographics.from_year_age_rate_data(pop_df               = pop_df,               # noqa: E251, E221
                                                        age_distribution_yar = age_distribution_yar, # noqa: E251
                                                        fertility_yar        = fertility_yar,        # noqa: E251, E221
                                                        male_mortality_yar   = male_mortality_yar,   # noqa: E251, E221
                                                        female_mortality_yar = female_mortality_yar, # noqa: E251
                                                        society              = None)                 # noqa: E251, E221, E202

        cls._inital_demog_cache = copy.deepcopy(demog)

        return demog

    @classmethod
    def _get_concurrency_parameterized_calls(cls,
                                             relationship_type: str,
                                             risk_group: str,
                                             max_simul_rels_male: float,
                                             max_simul_rels_female: float,
                                             prob_xtra_rel_male: float,
                                             prob_xtra_rel_female: float,
                                             node_ids: Union[List[int], None] = None,
                                             label: str = None) -> List[ParameterizedCall]:
        from emodpy_hiv.demographics.library import set_concurrency_parameters

        parameterized_calls = []
        nhp = {'relationship_type': relationship_type, 'risk_group': risk_group, 'node_ids': node_ids}
        hp = {'max_simul_rels_male': max_simul_rels_male, 'max_simul_rels_female': max_simul_rels_female,
              'prob_xtra_rel_male': prob_xtra_rel_male, 'prob_xtra_rel_female': prob_xtra_rel_female}
        if label is None:
            label = cls.generate_label(relationship_type=relationship_type, risk_group=risk_group, node_ids=node_ids)
        pc = ParameterizedCall(func=set_concurrency_parameters, non_hyperparameters=nhp,
                               hyperparameters=hp,
                               label=label)
        parameterized_calls.append(pc)
        return parameterized_calls

    @classmethod
    def _get_pair_formation_parameterized_calls(cls,
                                                relationship_type: str,
                                                risk_assortivity: float,
                                                formation_rate: float,
                                                node_ids: Union[List[int], None] = None,
                                                label: str = None) -> List[ParameterizedCall]:
        from emodpy_hiv.demographics.library import set_pair_formation_parameters

        parameterized_calls = []
        nhp = {'relationship_type': relationship_type, 'node_ids': node_ids}
        hp = {'risk_assortivity': risk_assortivity, 'formation_rate': formation_rate}
        if label is None:
            label = cls.generate_label(relationship_type=relationship_type, node_ids=node_ids)
        pc = ParameterizedCall(func=set_pair_formation_parameters,
                               non_hyperparameters=nhp,
                               hyperparameters=hp,
                               label=label)
        parameterized_calls.append(pc)
        return parameterized_calls

    @classmethod
    def _get_relationship_parameterized_calls(cls, relationship_type: str,
                                              coital_act_rate: float = None,
                                              condom_usage_min: float = None,
                                              condom_usage_mid: float = None,
                                              condom_usage_max: float = None,
                                              condom_usage_rate: float = None,
                                              duration_scale: float = None,
                                              duration_heterogeneity: float = None,
                                              node_ids: Union[List[int], None] = None,
                                              label: str = None) -> List[ParameterizedCall]:
        from emodpy_hiv.demographics.library import set_relationship_parameters
        parameterized_calls = []
        nhp = {'relationship_type': relationship_type, 'node_ids': node_ids}
        hp = {
            'coital_act_rate': coital_act_rate,
            'condom_usage_min': condom_usage_min,
            'condom_usage_mid': condom_usage_mid,
            'condom_usage_max': condom_usage_max,
            'condom_usage_rate': condom_usage_rate,
            'duration_scale': duration_scale,
            'duration_heterogeneity': duration_heterogeneity
        }

        if label is None:
            label = cls.generate_label(relationship_type=relationship_type, node_ids=node_ids)
        pc = ParameterizedCall(func=set_relationship_parameters,
                               non_hyperparameters=nhp,
                               hyperparameters=hp,
                               label=label)
        parameterized_calls.append(pc)
        return parameterized_calls

    @classmethod
    def _get_individual_property_parameterized_calls(cls) -> List[ParameterizedCall]:
        from emodpy_hiv.demographics.library import set_initial_cascade_state_distribution, \
            set_initial_health_care_accessibility_distribution, set_initial_risk_distribution

        risk_data = []
        risk_data.append({"node_id":  1, "low": 0.255498673 }) # noqa: E202, E241
        risk_data.append({"node_id":  2, "low": 0.330078204 }) # noqa: E202, E241
        risk_data.append({"node_id":  3, "low": 0.121868492 }) # noqa: E202, E241
        risk_data.append({"node_id":  4, "low": 0.221650376 }) # noqa: E202, E241
        risk_data.append({"node_id":  5, "low": 0.395151764 }) # noqa: E202, E241
        risk_data.append({"node_id":  6, "low": 0.095060159 }) # noqa: E202, E241
        risk_data.append({"node_id":  7, "low": 0.288686141 }) # noqa: E202, E241
        risk_data.append({"node_id":  8, "low": 0.446287507 }) # noqa: E202, E241
        risk_data.append({"node_id":  9, "low": 0.378176731 }) # noqa: E202, E241
        risk_data.append({"node_id": 10, "low": 0.283319058 }) # noqa: E202

        parameterized_calls = []
        for data in risk_data:
            hp = {'initial_risk_distribution_low': data["low"]}
            nhp = {'node_ids': [data["node_id"]]}
            pc = ParameterizedCall(func=set_initial_risk_distribution,
                                   non_hyperparameters=nhp,
                                   hyperparameters=hp,
                                   label=NODE_ID_TO_NODE_NAME[data["node_id"]])
            parameterized_calls.append(pc)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Since we need to set separate Risk distributions per node, the following
        # is working around a JSON overlay challene where the list of IP's in a node
        # overrides the the list of IPs in Defaults. EMOD does not allow you to override
        # specific IPs.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        distribution = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        pc = ParameterizedCall(set_initial_cascade_state_distribution,
                               non_hyperparameters={
                                   'cascade_state_distribution': distribution,
                                   'node_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                               })
        parameterized_calls.append(pc)

        pc = ParameterizedCall(set_initial_health_care_accessibility_distribution,
                               hyperparameters={'initial_accessibility': 0.8},
                               non_hyperparameters={'node_ids': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
        parameterized_calls.append(pc)
        return parameterized_calls

    @classmethod
    def get_demographics_parameterized_calls(cls, demographics: HIVDemographics) -> List[ParameterizedCall]:
        parameterized_calls = super().get_demographics_parameterized_calls(demographics=demographics)

        concurrency_parameters = {
            COMMERCIAL: {
                LOW:    {'max_simul_rels_male':  0, 'max_simul_rels_female':  0,     # noqa: E241
                         'prob_xtra_rel_male':   1, 'prob_xtra_rel_female':   1},    # noqa: E241
                MEDIUM: {'max_simul_rels_male':  0, 'max_simul_rels_female':  0,     # noqa: E241
                         'prob_xtra_rel_male':   1, 'prob_xtra_rel_female':   1},    # noqa: E241
                HIGH:   {'max_simul_rels_male': 59, 'max_simul_rels_female': 59,     # noqa: E241
                         'prob_xtra_rel_male':   1, 'prob_xtra_rel_female':   1},    # noqa: E241
            },
            TRANSITORY: {
                LOW:    {'max_simul_rels_male': 1.861181867682,    'max_simul_rels_female': 1.95751180447129,      # noqa: E241
                         'prob_xtra_rel_male':  0.184386490919862, 'prob_xtra_rel_female':  0.0608225887738051},   # noqa: E241
                MEDIUM: {'max_simul_rels_male': 2.48697611966592,  'max_simul_rels_female': 2.38937717475767,      # noqa: E241
                         'prob_xtra_rel_male':  0.287814625075045, 'prob_xtra_rel_female':  0.3116864843045},      # noqa: E241
                HIGH:   {'max_simul_rels_male': 1,                 'max_simul_rels_female': 1,                     # noqa: E241
                         'prob_xtra_rel_male':  1,                 'prob_xtra_rel_female':  1},                    # noqa: E241
            },
            INFORMAL: {
                LOW:    {'max_simul_rels_male': 1.34356628685348,  'max_simul_rels_female': 1.21853602956715,     # noqa: E241
                         'prob_xtra_rel_male':  0.286213622743763, 'prob_xtra_rel_female':  0.289761028337281},   # noqa: E241
                MEDIUM: {'max_simul_rels_male': 2.70230847725607,  'max_simul_rels_female': 2.76579821196633,     # noqa: E241
                         'prob_xtra_rel_male':  0.396354197417793, 'prob_xtra_rel_female':  0.404566634121599},   # noqa: E241
                HIGH:   {'max_simul_rels_male': 1,                 'max_simul_rels_female': 1,                    # noqa: E241
                         'prob_xtra_rel_male':  1,                 'prob_xtra_rel_female':  1},                   # noqa: E241
            },
            MARITAL: {
                LOW:    {'max_simul_rels_male': 1,                'max_simul_rels_female': 1,                # noqa: E241
                         'prob_xtra_rel_male':  0,                'prob_xtra_rel_female':  0},               # noqa: E241
                MEDIUM: {'max_simul_rels_male': 1.86152532283732, 'max_simul_rels_female': 1.7602276432905,  # noqa: E241
                         'prob_xtra_rel_male':  1,                'prob_xtra_rel_female':  1},               # noqa: E241
                HIGH:   {'max_simul_rels_male': 1,                'max_simul_rels_female': 1,                # noqa: E241
                         'prob_xtra_rel_male':  1,                'prob_xtra_rel_female':  1},               # noqa: E241
            },
        }
        for relationship_type, by_risk_group in concurrency_parameters.items():
            for risk_group, parameters in by_risk_group.items():
                pcs = cls._get_concurrency_parameterized_calls(relationship_type=relationship_type,
                                                               risk_group=risk_group,
                                                               **parameters)
                parameterized_calls.extend(pcs)

        pair_formation = {
            # assortivity -1 means a matrix of all 1s
            COMMERCIAL: {'risk_assortivity': -1,                 'formation_rate': 0.15                }, # noqa: E241, E202
            TRANSITORY: {'risk_assortivity': 0.159566721712443, 'formation_rate': 0.00135026850353989 }, # noqa: E241, E202
            INFORMAL:   {'risk_assortivity': 0.159566721712443, 'formation_rate': 0.00032670785736624 }, # noqa: E241, E202
            MARITAL:    {'risk_assortivity': 0.159566721712443, 'formation_rate': 0.000151940868159564}, # noqa: E241
        }
        for relationship_type, parameters in pair_formation.items():
            pcs = cls._get_pair_formation_parameterized_calls(relationship_type=relationship_type, **parameters)
            parameterized_calls.extend(pcs)

        # This value is by relationship type and node
        condom_usage_max_by_rel_type_by_node = {
             1: {TRANSITORY: 0.768125525501553,  INFORMAL: 0.00000000000000,   MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241, E126- Central
             2: {TRANSITORY: 0.0465318600828683, INFORMAL: 0.00000000000000,   MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Copperbelt
             3: {TRANSITORY: 1.000000000000000,  INFORMAL: 1.0000000000000000, MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Eastern
             4: {TRANSITORY: 0.729385699413249,  INFORMAL: 0.914462979184887,  MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Luapula
             5: {TRANSITORY: 0.140581131843158,  INFORMAL: 0.142047989631679,  MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Lusaka
             6: {TRANSITORY: 0.994397435542292,  INFORMAL: 0.872714880116124,  MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Muchinga
             7: {TRANSITORY: 0.670742512452915,  INFORMAL: 0.369039487928584,  MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Northwestern
             8: {TRANSITORY: 0.0351968246341627, INFORMAL: 0.887947627893753,  MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Northern
             9: {TRANSITORY: 0.652901388440937,  INFORMAL: 0.0673164100373441, MARITAL: 0.247035322003042, COMMERCIAL: 0.85}, # noqa: E241      - Southern
            10: {TRANSITORY: 0.156039574962396,  INFORMAL: 0.0304155588276527, MARITAL: 0.247035322003042, COMMERCIAL: 0.85}  # noqa: E241, E131- Western
        }

        # Other relationship parameters are only by relationship type
        relationship_parameters = {
            TRANSITORY: {'coital_act_rate': 0.33, 'condom_usage_min': 0, 'condom_usage_mid': 2001.29656235789,
                         'condom_usage_rate': 2.36008597080353, 'duration_scale': 0.956774771214,
                         'duration_heterogeneity': 0.833333333},
            INFORMAL:   {'coital_act_rate': 0.33, 'condom_usage_min': 0, 'condom_usage_mid': 2002.789368, # noqa: E241
                         'condom_usage_rate': 0.288440457896589, 'duration_scale': 2.03104913138,
                         'duration_heterogeneity': 0.75},
            MARITAL:    {'coital_act_rate': 0.33, 'condom_usage_min': 0, 'condom_usage_mid': 1994.323885, # noqa: E241
                         'condom_usage_rate': 1.66784081403387, 'duration_scale': 22.154455184937,
                         'duration_heterogeneity': 0.666666667},
            COMMERCIAL: {'coital_act_rate': 0.0027397260273972603, 'condom_usage_min': 0.5, 'condom_usage_mid': 1999.5,
                         'condom_usage_rate': 1, 'duration_scale': 0.01917808219,
                         'duration_heterogeneity': 1}
        }
        # NOTE: The all-node versions of hyperparameters defined here override the per-node-id versions. The reason is
        #  that the all-node hyperparameters are added to the returned list LAST (last defined hyperparameter setting
        #  wins in parameterized call application when >1 hyperparameter affects the same model setting).
        # NOTE: due to how demographics sub-objects are built, if we set 1+ items on e.g. relationship parameters,
        #  we need to set them all to prevent bad things. So we apply all-node values directly to individual nodes,
        #  making the parameters all-node by using an across-node-shared label (multi-use, shared parameters)
        for node_id, condom_usage_max_by_rel_type in condom_usage_max_by_rel_type_by_node.items():
            for relationship_type, condom_usage_max in condom_usage_max_by_rel_type.items():
                node_label = cls.generate_label(relationship_type=relationship_type,
                                                node_name=NODE_ID_TO_NODE_NAME[node_id])
                pcs = cls._get_relationship_parameterized_calls(relationship_type=relationship_type,
                                                                condom_usage_max=condom_usage_max,
                                                                node_ids=[node_id],
                                                                label=node_label)
                parameterized_calls.extend(pcs)

                parameters = relationship_parameters[relationship_type]
                all_nodes_label = cls.generate_label(relationship_type=relationship_type)
                pcs = cls._get_relationship_parameterized_calls(relationship_type=relationship_type,
                                                                **parameters,
                                                                node_ids=[node_id],
                                                                label=all_nodes_label)
                parameterized_calls.extend(pcs)

        # setting initial properties
        pcs = cls._get_individual_property_parameterized_calls()
        parameterized_calls.extend(pcs)

        return parameterized_calls

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
        reporters = super().build_reports(reporters=reporters)

        reporters.add(ReportHIVART(reporters_object=reporters))
        reporters.add(ReportHIVInfection(reporters_object=reporters,
                                         report_filter=ReportFilter(start_year=1980,
                                                                    end_year=2050)))
        reporters.add(ReportHIVMortality(reporters_object=reporters))
        reporters.add(ReportTransmission(reporters_object=reporters))
        reporters.add(ReportRelationshipStart(reporters_object=reporters,
                                              include_hiv_disease_statistics=True,         # default
                                              include_other_relationship_statistics=True,  # default
                                              individual_properties=None,                  # default
                                              report_filter=ReportFilter(start_year=1980,
                                                                         end_year=2050,
                                                                         node_ids=None,                # default
                                                                         min_age_years=None,           # default
                                                                         max_age_years=None,           # default
                                                                         must_have_ip_key_value="",    # default
                                                                         must_have_intervention="")))  # default
        reporters.add(InsetChart(reporters_object=reporters,
                                 has_ip=None,  # default
                                 has_interventions=None,      # default
                                 include_pregnancies=False,   # default
                                 include_coital_acts=True,    # default
                                 event_channels_list=["NewInfectionEvent"]))
        # reporting_period of 182.5 is required for calibration because this will cause EMOD to output a mid-year
        # data timepoint. This reported data is INSTANTANEOUS (current state). It is the current-best-approximation to
        # the year-averaged real-world reference data provided used for calibration (in calibration, we compare the
        # instantaneous, mid-year model output to annual-averaged reference data).
        reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                              collect_gender_data=True,
                                              collect_age_bins_data=[15, 20, 25, 30, 35, 40, 45, 50],
                                              collect_circumcision_data=True,
                                              collect_hiv_data=True,
                                              collect_hiv_stage_data=False,         # default
                                              collect_on_art_data=True,
                                              collect_ip_data=None,                 # default
                                              collect_intervention_data=["Traditional_MC"],
                                              collect_targeting_config_data=None,   # default
                                              add_transmitters=False,               # default
                                              stratify_infected_by_cd4=False,       # default
                                              event_counter_list=["NewInfectionEvent"],
                                              add_relationships=True,
                                              add_concordant_relationships=False,   # default
                                              reporting_period=182.5,
                                              report_filter=ReportFilter(start_year=1980,
                                                                         end_year=2050)))

        return reporters
