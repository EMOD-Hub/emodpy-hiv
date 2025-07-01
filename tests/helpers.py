import os
import shutil
from pathlib import Path

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.campaign.individual_intervention import CommonInterventionParameters, SimpleVaccine, \
    AntiretroviralTherapy
from emodpy_hiv.campaign.distributor import add_intervention_triggered, add_intervention_scheduled
from emodpy_hiv.reporters.reporters import ReportEventCounter, ReportFilter, ReportEventRecorder
import emodpy_hiv.campaign.waning_config as waning_config
from emodpy_hiv.utils.emod_enum import VaccineType
from emodpy_hiv.utils.targeting_config import HasIntervention

def delete_existing_file(file):
    if os.path.isfile(file):
        os.remove(file)

def is_dir_path_empty(directory_path):
    path = Path(directory_path)
    if not path.is_dir():
        # Handle cases where the path is not a directory or doesn't exist
        return False
    return not any(path.iterdir())

def delete_existing_folder(path, must_be_empty=False):
    if os.path.isdir(path):
        if not must_be_empty or (must_be_empty and is_dir_path_empty(path)):
            shutil.rmtree(path)


def close_idmtools_logger(logger):
    """
    Forcefully close all file handlers in the logger.
    the logger is part of emod_task and does not let you delete the generated files when the test is done running
    because the logger is still open. This function closes the logger so that the folder with generated files
    can be deleted.
    """
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)


def create_failed_tests_folder():
    """
    Create a folder for failed tests if it doesn't exist.
    """
    import manifest
    if not os.path.exists(manifest.failed_tests):
        os.makedirs(manifest.failed_tests)


# ----------------------------------------
# need to add hiv-specific stuff to these
# ----------------------------------------
def config_builder(config):
    """
        this is taken directly from emodpy_hiv/countries/zambia
        when that gets updated, we should take things directly from there
        currently there's an extra "create default config" function and idk how it will work with
        from_defaults
    """
    config.parameters.Simulation_Type = "HIV_SIM"
    config.parameters.Simulation_Duration = 30.4166666666667 * 12
    config.parameters.Simulation_Timestep = 30.4166666666667

    # Reduce the initial population so tutorial can double it
    config.parameters.x_Base_Population = 1  # 0.005
    config.parameters.Start_Time = 0
    config.parameters.Age_Initialization_Distribution_Type = "DISTRIBUTION_SIMPLE"
    config.parameters.AIDS_Duration_In_Months = 9
    config.parameters.AIDS_Stage_Infectivity_Multiplier = 4.5
    config.parameters.Acute_Duration_In_Months = 2.9
    config.parameters.Acute_Stage_Infectivity_Multiplier = 26
    config.parameters.Base_Individual_Sample_Rate = 1
    config.parameters.Base_Infectivity = 0.00031382269992254885
    config.parameters.Base_Year = 1960.5
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
    config.parameters.Enable_Aging = 1
    config.parameters.Enable_Birth = 1
    config.parameters.Enable_Coital_Dilution = 1
    config.parameters.Enable_Demographics_Birth = 0
    config.parameters.Enable_Infectivity_Reservoir = 0
    config.parameters.Enable_Maternal_Protection = 0
    config.parameters.Enable_Natural_Mortality = 0
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
    config.parameters.Male_To_Female_Relative_Infectivity_Multipliers = [2.9976868182763963,
                                                                         2.9976868182763963,
                                                                         2.936393464131044]
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
    config.parameters.Sexual_Debut_Age_Setting_Type = "WEIBULL"
    config.parameters.Sexual_Debut_Age_Female_Weibull_Heterogeneity = 0.22002507694706103
    config.parameters.Sexual_Debut_Age_Female_Weibull_Scale = 15.092122890359025
    config.parameters.Sexual_Debut_Age_Male_Weibull_Heterogeneity = 0.1268087803455056
    config.parameters.Sexual_Debut_Age_Male_Weibull_Scale = 15.582384534190258
    config.parameters.Sexual_Debut_Age_Min = 13

    return config


def demographics_builder():
    """
        needs to add something hiv-specific
    """
    demographics_object = HIVDemographics.from_template_node(lat=0, lon=0, pop=1000, name="1", forced_id=1,
                                                             default_society_template="PFA-Southern-Africa")
    # demographics_object.SetDefaultNodeAttributes()
    demographics_object.AddIndividualPropertyAndHINT(Property="Aliens", Values=["Bajoran", "Vulcan", "Andorian"],
                                                     InitialDistribution=[0.3, 0.3, 0.4])

    return demographics_object


def campaign_builder(campaign):
    """
        needs to add something hiv-specific
    """
    this_waning_config = waning_config.BoxExponential(box_duration=25, decay_time_constant=60, initial_effect=0.89)
    common_intervention_parameters = CommonInterventionParameters(cost=0.5,
                                                                  dont_allow_duplicates=True,
                                                                  intervention_name="Vaccine")
    vaccine = SimpleVaccine(campaign,
                            waning_config=this_waning_config,
                            vaccine_take=0.94,
                            vaccine_type=VaccineType.TransmissionBlocking,
                            common_intervention_parameters=common_intervention_parameters)
    art = AntiretroviralTherapy(campaign,
                                common_intervention_parameters=CommonInterventionParameters(intervention_name="ART"))
    art2 = AntiretroviralTherapy(campaign, days_to_achieve_viral_suppression=50,
                                 common_intervention_parameters=CommonInterventionParameters(intervention_name="ART2"))
    add_intervention_triggered(campaign, triggers_list=["HappyBirthday"], intervention_list=[vaccine, art], start_day=35)
    add_intervention_scheduled(campaign, intervention_list=[art2], start_day=100,
                               targeting_config=HasIntervention(intervention_name="ART"))
    add_intervention_scheduled(campaign, intervention_list=[art2], start_day=300,
                               targeting_config=HasIntervention(intervention_name="ART"))
    return campaign


def reports_builder(reporters):
    reporters.add(ReportEventRecorder(reporters_object=reporters,
                                      event_list=["HappyBirthday", "NewInfectionEvent"],
                                      report_filter=ReportFilter(start_day=1, end_day=6)))

    reporters.add(ReportEventCounter(reporters_object=reporters,
                                     event_list=["HappyBirthday", "NewInfectionEvent"],
                                     report_filter=ReportFilter(filename_suffix="testing")))
    return reporters
