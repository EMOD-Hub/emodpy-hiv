# QUESTION: verify dead-labeled code is dead
import pandas as pd
import decimal

from emodpy_hiv.campaign.individual_intervention import (OutbreakIndividual, HIVSigmoidByYearAndSexDiagnostic,
                                                         HIVRandomChoice, HIVPiecewiseByYearAndSexDiagnostic,
                                                         HIVRapidHIVDiagnostic, ModifyStiCoInfectionStatus, PMTCT,
                                                         MaleCircumcision, STIIsPostDebut, HIVMuxer,
                                                         PropertyValueChanger, BroadcastEvent, HIVDrawBlood,
                                                         HIVARTStagingCD4AgnosticDiagnostic,
                                                         HIVARTStagingByCD4Diagnostic, Sigmoid, AntiretroviralTherapy,
                                                         ARTDropout, MultiInterventionDistributor)


from emodpy_hiv.campaign.common import (TargetDemographicsConfig, TargetGender, PropertyRestrictions, ValueMap,
                                        CommonInterventionParameters)
from emodpy_hiv.campaign.distributor import (add_intervention_scheduled, add_intervention_triggered,
                                             add_intervention_nchooser_df, add_intervention_reference_tracking)
from emodpy_hiv.utils.distributions import (UniformDistribution, ExponentialDistribution, ConstantDistribution,
                                            WeibullDistribution)
from emodpy_hiv.utils.emod_enum import TargetDiseaseState
from emodpy_hiv.utils.targeting_config import (IsHivPositive, IsOnART, HasBeenOnArtMoreOrLessThanNumMonths, MoreOrLess,
                                               HasIntervention)
import emod_api.campaign

from typing import List, Tuple, Dict, Union


class CustomEvent:  # consider moving this to a separate file or make it a private class.
    ART_STAGING = 'ARTStaging'
    ART_STAGING_0 = 'ARTStaging0'  # immediate ART staging, rename this to ImmediateARTStaging?
    ART_STAGING_1 = 'ARTStaging1'  # ART staging diagnostic test, rename this to ARTStagingDiagnosticTest?
    ART_STAGING_2 = 'ARTStaging2'
    ART_STAGING_3 = 'ARTStaging3'
    ART_STAGING_4 = 'ARTStaging4'
    ART_STAGING_5 = 'ARTStaging5'
    ART_STAGING_6 = 'ARTStaging6'
    # ART_STAGING_7 = 'ARTStaging7' # not used
    ART_STAGING_8 = 'ARTStaging8'
    ART_STAGING_9 = 'ARTStaging9'

    STI_DEBUT = "STIDebut"
    COMMERCIAL_UPTAKE = "Commercial_Uptake"
    COMMERCIAL_DROPOUT = "Commercial_Dropout"
    COMMERCIAL_DELAY_FROM_DEBUT_UPTAKE = "Commercial_DelayFromDebutToUptake"

    HCT_TESTING_LOOP = 'HCTTestingLoop'
    HCT_TESTING_LOOP_0 = 'HCTTestingLoop0'
    HCT_TESTING_LOOP_1 = 'HCTTestingLoop1'
    HCT_TESTING_LOOP_2 = 'HCTTestingLoop2'

    HCT_UPTAKE_POST_DEBUT_0 = 'HCTUptakePostDebut0'
    HCT_UPTAKE_POST_DEBUT_1 = 'HCTUptakePostDebut1'
    HCT_UPTAKE_POST_DEBUT_2 = 'HCTUptakePostDebut2'
    HCT_UPTAKE_POST_DEBUT_3 = 'HCTUptakePostDebut3'
    # HCT_UPTAKE_POST_DEBUT_4 = 'HCTUptakePostDebut4'  # not used
    # HCT_UPTAKE_POST_DEBUT_5 = 'HCTUptakePostDebut5'  # not used
    # HCT_UPTAKE_POST_DEBUT_6 = 'HCTUptakePostDebut6'  # not used
    HCT_UPTAKE_POST_DEBUT_7 = 'HCTUptakePostDebut7'
    HCT_UPTAKE_POST_DEBUT_8 = 'HCTUptakePostDebut8'
    HCT_UPTAKE_POST_DEBUT_9 = 'HCTUptakePostDebut9'

    LINKING_TO_ART_0 = 'LinkingToART0'
    LINKING_TO_PRE_ART_0 = 'LinkingToPreART0'

    LOST_FOREVER_0 = "LostForever0"
    LOST_FOREVER_9 = "LostForever9"

    ON_ART_0 = 'OnART0'
    ON_ART_1 = 'OnART1'

    ON_PRE_ART = 'OnPreART'
    ON_PRE_ART_0 = 'OnPreART0'
    ON_PRE_ART_1 = 'OnPreART1'
    ON_PRE_ART_2 = 'OnPreART2'
    ON_PRE_ART_3 = 'OnPreART3'
    ON_PRE_ART_4 = 'OnPreART4'


BIRTH = 'Births'
HIV_NEGATIVE = TargetDiseaseState.HIV_NEGATIVE
NEWLY_SYMPTOMATIC = 'NewlySymptomatic'  # 'HIVSymptomatic' is replaced by 'NewlySymptomatic'
SIX_WEEKS_OLD = 'SixWeeksOld'
TWELVE_WEEKS_PREGNANT = 'TwelveWeeksPregnant'
NOT_HAVE_INTERVENTION = TargetDiseaseState.NOT_HAVE_INTERVENTION
MALE = TargetGender.MALE
FEMALE = TargetGender.FEMALE
EPSILON = 1e-3
ANY_MC = 'Any_MC'
PROGRAM_VMMC = 'Program_VMMC'


# These are the Event triggers for the Cascade states.
HCT_UPTAKE_POST_DEBUT_TRIGGER_1 = CustomEvent.HCT_UPTAKE_POST_DEBUT_1  # directly go to HIVMuxer delay in HCTUptakePostDebut state without going through STIIsPostDebut
HCT_UPTAKE_POST_DEBUT_TRIGGER_2 = CustomEvent.HCT_UPTAKE_POST_DEBUT_3
HCT_UPTAKE_POST_DEBUT_TRIGGER_3 = CustomEvent.HCT_UPTAKE_POST_DEBUT_9  # lost to follow-up
HCT_TESTING_LOOP_TRIGGER = CustomEvent.HCT_TESTING_LOOP_0
LINKING_TO_PRE_ART_TRIGGER = CustomEvent.LINKING_TO_PRE_ART_0
ON_PRE_ART_TRIGGER = CustomEvent.ON_PRE_ART_0
ON_ART_TRIGGER_1 = CustomEvent.ON_ART_0  # go to randomchoice with choices to a HIVMuxer delay or ON_ART_TRIGGER_2 in OnART stage
ON_ART_TRIGGER_2 = CustomEvent.ON_ART_1  # directly go to ARTBasic in OnART stage without going through randomchoice
LINKING_TO_ART_TRIGGER = CustomEvent.LINKING_TO_ART_0
ART_STAGING_DIAGNOSTIC_TEST_TRIGGER = CustomEvent.ART_STAGING_0
ART_STAGING_TRIGGER_1 = CustomEvent.ART_STAGING_1    # go to randomchoice in ARTStaging
ART_STAGING_TRIGGER_2 = CustomEvent.ART_STAGING_2    # directly go to hivmuxer in ARTStaging without going through randomchoice
DUMMY_TRIGGER = 'DummyTrigger'  # a DoNothingTrigger
LOST_FOREVER_TRIGGER = CustomEvent.LOST_FOREVER_0


class CascadeState:
    LOST_FOREVER = "CascadeState:LostForever"
    ON_ART = "CascadeState:OnART"
    LINKING_TO_ART = "CascadeState:LinkingToART"
    ON_PRE_ART = "CascadeState:OnPreART"
    LINKING_TO_PRE_ART = "CascadeState:LinkingToPreART"
    ART_STAGING = "CascadeState:ARTStaging"
    ART_STAGING_DIAGNOSTIC_TEST = 'CascadeState:ARTStagingDiagnosticTest'
    TESTING_ON_SYMPTOMATIC = "CascadeState:TestingOnSymptomatic"
    TESTING_ON_ANC = "CascadeState:TestingOnANC"
    TESTING_ON_CHILD_6W = "CascadeState:TestingOnChild6w"
    HCT_TESTING_LOOP = "CascadeState:HCTTestingLoop"
    HCT_UPTAKE_AT_DEBUT = "CascadeState:HCTUptakeAtDebut"
    HCT_UPTAKE_POST_DEBUT = "CascadeState:HCTUptakePostDebut"


def timestep_from_year(year: Union[float, int], base_year: Union[float, int]) -> int:
    """
    Converts a year into a timestep based on a base year.

    Args:
        year (Union[float, int]): The year to be converted.
        base_year (Union[float, int]): The base year for the conversion.

    Returns:
        int: The timestep corresponding to the given year.
    """
    return int((year - base_year) * 365)


def convert_time_value_map(time_value_map) -> dict:
    """
    Converts a time-value map into a dictionary where each time is a key and its corresponding value is the value. This
    is the expected format for the TVMap in the current emodpy-hiv interventions code, ex. yearandsexdiag.new_diagnostic
    function.

    Args:
        time_value_map (dict): A dictionary containing two lists, "Times" and "Values".
                               "Times" is a list of times (years) and "Values" is a list of corresponding values.

    Returns:
        dict: A dictionary where each time from "Times" is a key and its corresponding value from "Values" is the value.

    Example:
        >>> time_value_map = {"Times": [2002, 2010.5, 2013.95], "Values": [200, 350, 500]}
        >>> convert_time_value_map(time_value_map)
        {2002: 200, 2010.5: 350, 2013.95: 500}
    """
    time_value_map_convert = {}
    for time, value in zip(time_value_map["Times"], time_value_map["Values"]):
        time_value_map_convert[time] = value
    return time_value_map_convert


# This is the time value map that used in multiple HIVPiecewiseByYearAndSexDiagnostic interventions in the Zambia model
# which we used as the default time value map for convenience. Please note that the Values in this time value map are
# all 0s, which means the intervention will return all negative result(zero possibility of positive test results).
all_negative_time_value_map = convert_time_value_map({"Times": [1990, 2016], "Values": [0, 0]})


def seed_infections(campaign: emod_api.campaign,
                    seeding_node_ids: Union[List[int], None] = None,
                    seeding_start_year: float = 1982,
                    seeding_coverage: float = 0.075,
                    seeding_target_min_age: float = 0,
                    seeding_target_max_age: float = 200,
                    seeding_target_gender: TargetGender = TargetGender.ALL,
                    seeding_target_property_restrictions: list = None) -> None:
    """
    Add a OutbreakIndividual intervention with StandardEventCoordinator to the campaign object.
    Args:
        campaign: emod_api.campaign object
        seeding_node_ids: List of node IDs to seed infections in. Defaults to None, which seeds infections in all nodes.
        seeding_start_year: The year to start seeding infections. Defaults to 1982.
        seeding_coverage: The coverage of the seeding infections. Defaults to 0.075.
        seeding_target_min_age: The minimum age of the target population. Defaults to 0.
        seeding_target_max_age: The maximum age of the target population. Defaults to 200.
        seeding_target_gender: The TargetGender object which defines the gender of the target population. Defaults to TargetGender.ALL. Options are TargetGender.MALE, TargetGender.FEMALE, TargetGender.ALL.
        seeding_target_property_restrictions: List of property restrictions. Defaults to None.

    Returns:
        None

    """
    event_name = f"Epidemic seeding in node(s) {str(seeding_node_ids)}"
    intervention = OutbreakIndividual(campaign, incubation_period_override=0)
    target_demographics_config = TargetDemographicsConfig(demographic_coverage=seeding_coverage,
                                                          target_age_min=seeding_target_min_age,
                                                          target_age_max=seeding_target_max_age,
                                                          target_gender=seeding_target_gender)
    property_restrictions = PropertyRestrictions(individual_property_restrictions=[seeding_target_property_restrictions])
    add_intervention_scheduled(campaign,
                               intervention_list=[intervention],
                               start_year=seeding_start_year,
                               event_name=event_name,
                               node_ids=seeding_node_ids,
                               target_demographics_config=target_demographics_config,
                               property_restrictions=property_restrictions)


# property restrictions/disqualifying properties/new property values checked
def add_csw(campaign: emod_api.campaign,
            node_ids: Union[List[int], None] = None,
            male_uptake_coverage: float = 0.03,
            female_uptake_coverage: float = 0.03):
    """
    Manages commercial sex worker (CSW) uptake and dropout (with delays) for men and women.

    Setting a few women to Risk=HIGH and significantly more men to Risk=HIGH makes the women the sex workers and the
    men the sex clients. Supply and demand cause the females to have lots of relationships with the men that are also
    Risk=HIGH. The women have lots of relationships because so many men want them, but the scarcity of the women allow
    the men to have only a few.

    Args:
        campaign (emod_api.campaign): The campaign to which the CSW management is to be added.
        node_ids (List[int], optional): A list of node IDs where the CSW management is to be applied.
                                            Defaults to None, which applies to all nodes.
        male_uptake_coverage (float, optional): The coverage of CSW uptake among males. Defaults to 0.03.
        female_uptake_coverage (float, optional): The coverage of CSW uptake among females. Defaults to 0.03.

    Returns:
        None

    Example:
        >>> add_csw(campaign, node_ids=[1, 2, 3], male_uptake_coverage=0.05, female_uptake_coverage=0.04)
    """
    # manages commercial sex worker uptake and dropout (with delays) for men and women
    initial_trigger = CustomEvent.STI_DEBUT
    uptake_event = CustomEvent.COMMERCIAL_UPTAKE  # also serves as the dropout_delay_event
    dropout_event = CustomEvent.COMMERCIAL_DROPOUT
    uptake_delay_event = CustomEvent.COMMERCIAL_DELAY_FROM_DEBUT_UPTAKE

    # determine if women will become sex FSW
    will_become_FSW = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                         time_value_map=ValueMap(times=[campaign.base_year],
                                                                                 values=[female_uptake_coverage]),
                                                         positive_diagnosis_event=uptake_delay_event,
                                                         negative_diagnosis_event=None,
                                                         linear_interpolation=True,
                                                         common_intervention_parameters=CommonInterventionParameters(cost=0)
                                                         )
    add_intervention_triggered(campaign,
                               intervention_list=[will_become_FSW],
                               triggers_list=[initial_trigger],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.FEMALE),
                               node_ids=node_ids,
                               event_name=f"Female: Will ever become FSW in node(s) {str(node_ids)}")

    # Female delay to uptake
    female_delay_to_uptake = BroadcastEvent(campaign, broadcast_event=uptake_event)
    add_intervention_triggered(campaign,
                               intervention_list=[female_delay_to_uptake],
                               triggers_list=[uptake_delay_event],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.FEMALE),
                               delay_distribution=UniformDistribution(uniform_min=0, uniform_max=1825),
                               node_ids=node_ids,
                               event_name=f"Commercial Sex (Female): Delay to Uptake in node(s) {str(node_ids)}")

    # Female delay to dropout
    # QUESTION: campaign json indicates this is a different distribution from men (and from men/women uptake). Ok?
    female_delay_to_dropout = BroadcastEvent(campaign, broadcast_event=dropout_event)
    add_intervention_triggered(campaign,
                               intervention_list=[female_delay_to_dropout],
                               triggers_list=[uptake_event],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.FEMALE),
                               delay_distribution=WeibullDistribution(weibull_lambda=2215, weibull_kappa=3.312),
                               node_ids=node_ids,
                               event_name=f"Commercial Sex (Female): Delay to Dropout in node(s) {str(node_ids)}")

    # determine if men will become FSW clients
    # Use start_year + 0.5 to make sure it happens after setting Risk=HIGH
    will_become_FSW_client = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                                positive_diagnosis_event=uptake_delay_event,
                                                                negative_diagnosis_event=None,
                                                                time_value_map=ValueMap(times=[campaign.base_year + 0.5],
                                                                                        values=[male_uptake_coverage]),
                                                                linear_interpolation=True,
                                                                common_intervention_parameters=CommonInterventionParameters(cost=0))
    add_intervention_triggered(campaign,
                               intervention_list=[will_become_FSW_client],
                               triggers_list=[initial_trigger],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.MALE),
                               node_ids=node_ids,
                               event_name=f"Male: Will ever become FSW client in node(s) {str(node_ids)}")

    # Male delay to uptake
    male_delay_to_uptake = BroadcastEvent(campaign, broadcast_event=uptake_event)
    add_intervention_triggered(campaign,
                               intervention_list=[male_delay_to_uptake],
                               triggers_list=[uptake_delay_event],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.MALE),
                               delay_distribution=UniformDistribution(uniform_min=0, uniform_max=3650),
                               node_ids=node_ids,
                               event_name=f"Commercial Sex (Male): Delay to Uptake in node(s) {str(node_ids)}")

    # Male delay to dropout
    male_delay_to_dropout = BroadcastEvent(campaign, broadcast_event=dropout_event)
    add_intervention_triggered(campaign,
                               intervention_list=[male_delay_to_dropout],
                               triggers_list=[uptake_event],
                               start_year=campaign.base_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.MALE),
                               delay_distribution=UniformDistribution(uniform_min=730, uniform_max=10950),
                               node_ids=node_ids,
                               event_name=f"Commercial Sex (Male): Delay to Dropout in node(s) {str(node_ids)}")

    # commercial uptake, all genders
    risk_to_high = PropertyValueChanger(campaign,
                                        target_property_key='Risk', target_property_value='HIGH')
    add_intervention_triggered(campaign,
                               intervention_list=[risk_to_high],
                               triggers_list=[uptake_event],
                               start_year=campaign.base_year,
                               node_ids=node_ids,
                               event_name=f"Commercial Sex: Uptake in node(s) {str(node_ids)}")

    # commercial dropout, all genders
    risk_to_medium = PropertyValueChanger(campaign,
                                          target_property_key='Risk', target_property_value='MEDIUM')
    add_intervention_triggered(campaign,
                               intervention_list=[risk_to_medium],
                               triggers_list=[dropout_event],
                               start_year=campaign.base_year,
                               node_ids=node_ids,
                               event_name=f"Commercial Sex: Dropout in node(s) {str(node_ids)}")


# property restrictions/disqualifying properties/new property values checked
def add_post_debut_coinfection(campaign: emod_api.campaign,
                               coinfection_node_ids: List[int] = None,
                               coinfection_coverage: float = 0.3,
                               coinfection_gender: TargetGender = TargetGender.ALL,
                               coinfection_IP: Union[List[str], str] = "Risk:HIGH"):
    """
    Manages the addition of co-infections post sexual debut in the campaign.

    Args:
        campaign (emod_api.campaign): The campaign to which the co-infection management is to be added.
        coinfection_node_ids (List[int], optional): A list of node IDs where the co-infection management is to be applied.
                                                    Defaults to None, which applies to all nodes.
        coinfection_coverage (float, optional): The coverage of co-infection among the population. Defaults to 0.3.
        coinfection_gender (str, optional): A TargetGender object which define the gender to which the co-infection
         management is to be applied. Please see emodpy.campaign.common.TargetGender for details. Default to TargetGender.ALL.
        coinfection_IP (Union[List[str], str], optional): The individual properties to which the co-infection management is to be applied.
                                                          Defaults to "Risk:HIGH".

    Returns:
        None

    Example:
        >>> add_post_debut_coinfection(campaign, coinfection_node_ids=[1, 2, 3], coinfection_coverage=0.4, coinfection_gender='Male', coinfection_IP="Risk:MEDIUM")
    """
    post_debut_trigger = 'initial_coinfection_post_debut'
    at_debut_trigger = CustomEvent.STI_DEBUT

    if not isinstance(coinfection_IP, list):
        coinfection_IP = [coinfection_IP]
    coinfection_IP = PropertyRestrictions(individual_property_restrictions=[coinfection_IP])

    # intervention object setup
    modify_coinfection_status_iv = ModifyStiCoInfectionStatus(campaign, new_sti_coinfection_status=True)
    is_post_debut_check = STIIsPostDebut(campaign,
                                         positive_diagnosis_event=post_debut_trigger,
                                         negative_diagnosis_event=None,
                                         common_intervention_parameters=CommonInterventionParameters(cost=0))

    # seed co-infections in the initial target post-debut population
    add_intervention_scheduled(campaign,
                               intervention_list=[is_post_debut_check],
                               target_demographics_config=TargetDemographicsConfig(target_gender=coinfection_gender),
                               property_restrictions=coinfection_IP,
                               node_ids=coinfection_node_ids,
                               start_year=campaign.base_year + EPSILON,
                               event_name=f"Identifying initial {coinfection_IP.individual_property_restrictions} post-debut population to target for coinfections"
                               )  # this must start AFTER the distribution event to distribute properly
    # distribute co-infections at sexual debut, ongoing
    add_intervention_triggered(campaign,
                               intervention_list=[modify_coinfection_status_iv],
                               triggers_list=[post_debut_trigger, at_debut_trigger],
                               target_demographics_config=TargetDemographicsConfig(
                                   demographic_coverage=coinfection_coverage,
                                   target_gender=coinfection_gender),
                               property_restrictions=coinfection_IP,
                               node_ids=coinfection_node_ids,
                               start_year=campaign.base_year,
                               event_name=f"Distributing coinfections to {coinfection_IP.individual_property_restrictions} population at sexual debut and post debut."
                               )


# property restrictions/disqualifying properties/new property values checked
def add_pmtct(campaign: emod_api.campaign,
              child_testing_time_value_map: dict,
              child_testing_start_year: float = 2004,
              node_ids: Union[List[int], None] = None,
              coverage: float = 1.0,
              start_year: float = 1990,
              sigmoid_min: float = 0,
              sigmoid_max: float = 0.975,
              sigmoid_midyear: float = 2005.87,
              sigmoid_rate: float = 0.7136,
              link_to_ART_rate: float = 0.8,
              treatment_a_efficacy: float = 0.9,
              treatment_b_efficacy: float = 0.96667,
              sdNVP_efficacy: float = 0.66):
    """
    Manages the addition of prevention of mother-to-child transmission (PMTCT) in the campaign.

    Args:
        campaign (emod_api.campaign): The campaign to which the PMTCT management is to be added.
        child_testing_time_value_map (dict): A dictionary containing time-value map for child testing.
        child_testing_start_year (float, optional): The start year for child testing. Defaults to 2004.
        node_ids (List[int], optional): A list of node IDs where the PMTCT management is to be applied.
                                               Defaults to None, which applies to all nodes.
        coverage (float, optional): The coverage of PMTCT among the population. Defaults to 1.0.
        start_year (float, optional): The start year for PMTCT. Defaults to 1990.
        sigmoid_min (float, optional): The minimum value for the sigmoid ramp. Defaults to 0.
        sigmoid_max (float, optional): The maximum value for the sigmoid ramp. Defaults to 0.975.
        sigmoid_midyear (float, optional): The midyear for the sigmoid ramp. Defaults to 2005.87.
        sigmoid_rate (float, optional): The rate for the sigmoid ramp. Defaults to 0.7136.
        link_to_ART_rate (float, optional): The rate for linking to ART. Defaults to 0.8.
        treatment_a_efficacy (float, optional): The efficacy of treatment A. Defaults to 0.9.
        treatment_b_efficacy (float, optional): The efficacy of treatment B. Defaults to 0.96667.
        sdNVP_efficacy (float, optional): The efficacy of Single-Dose Nevirapine (sdNVP). Defaults to 0.66.

    Returns:
        None

    Example:
        >>> add_pmtct(campaign,
        >>>           child_testing_time_value_map={"Times": [2002, 2010.5, 2013.95], "Values": [200, 350, 500]},
        >>>           node_ids=[1, 2, 3],
        >>>           coverage=0.8,
        >>>           start_year=1995,
        >>>           sigmoid_min=0.1,
        >>>           sigmoid_max=0.9,
        >>>           sigmoid_midyear=2005,
        >>>           sigmoid_rate=0.7,
        >>>           link_to_ART_rate=0.85,
        >>>           treatment_a_efficacy=0.92,
        >>>           treatment_b_efficacy=0.96,
        >>>           sdNVP_efficacy=0.7)
    """

    disqualifying_properties = [CascadeState.LOST_FOREVER,
                                CascadeState.ON_ART,
                                CascadeState.LINKING_TO_ART,
                                CascadeState.ON_PRE_ART,
                                CascadeState.LINKING_TO_PRE_ART,
                                CascadeState.ART_STAGING,
                                CascadeState.TESTING_ON_SYMPTOMATIC]
    property_restrictions = 'Accessibility:Yes'

    add_state_TestingOnANC(campaign=campaign,
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

    # Testing of children at 6 weeks of age
    add_state_TestingOnChild6w(campaign=campaign,
                               start_year=child_testing_start_year,
                               disqualifying_properties=disqualifying_properties,
                               time_value_map=child_testing_time_value_map,
                               node_ids=node_ids,
                               property_restrictions=property_restrictions)


# TODO from Clark: when doing A-B testing, translate Any_MC in existing json to MaleCircumcision (the new, default name used)??
# ToDo from Ye: the VMMC_Zambia.json file has different traditional_male_circumcision_coverage for HIVRandomChoice for different
#  nodes but one MaleCircumcision for all node since the traditional_male_circumcision_reduced_acquire is the same for
#  all nodes. This is not supported in the current implementation. Should we consider updating this method to support?
def add_traditional_male_circumcision(campaign: emod_api.campaign,
                                      traditional_male_circumcision_start_year: float = 1961,
                                      randomchoice_start_year: float = 1975,
                                      traditional_male_circumcision_coverage: float = 0.054978651,
                                      traditional_male_circumcision_reduced_acquire: float = 0.6,
                                      traditional_male_circumcision_node_ids: Union[List[int], None] = None):
    """
    Manages the addition of traditional male circumcision in the campaign.

    Args:
        campaign (emod_api.campaign): The campaign to which the traditional male_circumcision management is to be added.
        traditional_male_circumcision_start_year (float, optional): The start year for traditional male_circumcision interventions. Defaults to 1961.
        randomchoice_start_year (float, optional): The start year for randomchoice_start_year interventions. Defaults to 1975.
        traditional_male_circumcision_coverage (float, optional): The coverage of traditional male_circumcision among the male population. Defaults to 0.054978651.
        traditional_male_circumcision_reduced_acquire (float, optional): The reduced acquire rate for traditional male_circumcision. Defaults to 0.6.
        traditional_male_circumcision_node_ids (List[int], optional): A list of node IDs where the traditional male_circumcision management is to be applied.
                                                         Defaults to None, which applies to all nodes.

    Returns:
        None

    Example:
        >>> add_traditional_male_circumcision(campaign, traditional_male_circumcision_coverage=0.06, traditional_male_circumcision_reduced_acquire=0.5, traditional_male_circumcision_node_ids=[1, 2, 3])
    """
    # start time is arbitrary; just needs to be pre-epidemic
    will_circumcise = 'WillReceiveTraditionalMaleCircumcision'

    # set up circumcision coverage selection
    decimal_places = decimal.Decimal(str(traditional_male_circumcision_coverage)).as_tuple().exponent
    choices = {will_circumcise: traditional_male_circumcision_coverage,
               DUMMY_TRIGGER: round(1 - traditional_male_circumcision_coverage, -decimal_places)}  # to get rid of floating point decimal issues
    decide_traditional_male_circumcision = HIVRandomChoice(campaign,
                                                           choice_names=list(choices.keys()),
                                                           choice_probabilities=list(choices.values()),
                                                           common_intervention_parameters=CommonInterventionParameters(cost=0))

    # Initializing historical traditional male circumcision in the population
    target_male = TargetDemographicsConfig(target_gender=TargetGender.MALE)
    add_intervention_scheduled(campaign,
                               intervention_list=[decide_traditional_male_circumcision],
                               start_year=randomchoice_start_year + EPSILON,
                               target_demographics_config=target_male,
                               node_ids=traditional_male_circumcision_node_ids,
                               event_name=f"Traditional male circumcision initialization in node(s) "
                                             f"{str(traditional_male_circumcision_node_ids)}")

    # traditional male circumcision at birth, ongoing
    add_intervention_triggered(campaign,
                               intervention_list=[decide_traditional_male_circumcision],
                               triggers_list=[BIRTH],
                               start_year=randomchoice_start_year + EPSILON,
                               target_demographics_config=target_male,
                               node_ids=traditional_male_circumcision_node_ids,
                               event_name=f"Traditional male circumcision at birth in node(s) "
                                             f"{str(traditional_male_circumcision_node_ids)}")

    # NOTE: this creates per-node-set events, which is more 'wasteful' if non-all-nodes are specified. But should work
    # just as well and prevent the user from calling a separate, second TMC function
    # actual traditional male circumcision event
    malecirc_intervention_name = ANY_MC
    # this is different from the start_day above, we need to make sure it's before the previous events
    if traditional_male_circumcision_start_year > randomchoice_start_year:
        raise ValueError(f"The start year for traditional male circumcision ({traditional_male_circumcision_start_year})"
                         f" should be before the start year for random choice ({randomchoice_start_year}).")
    distribute_circumcision = MaleCircumcision(campaign,
                                               circumcision_reduced_acquire=traditional_male_circumcision_reduced_acquire,
                                               distributed_event_trigger='Non_Program_MC',
                                               common_intervention_parameters=CommonInterventionParameters(intervention_name=malecirc_intervention_name))
    add_intervention_triggered(campaign,
                               intervention_list=[distribute_circumcision],
                               triggers_list=[will_circumcise],
                               start_year=traditional_male_circumcision_start_year,
                               node_ids=traditional_male_circumcision_node_ids,
                               target_demographics_config=target_male,
                               event_name=f"Apply traditional male circumcision intervention in node(s)"
                                             f" {str(traditional_male_circumcision_node_ids)}"
                               )
    return malecirc_intervention_name


def add_vmmc_reference_tracking(campaign: emod_api.campaign,
                                vmmc_time_value_map: dict,
                                vmmc_reduced_acquire: float = 0.6,
                                vmmc_target_min_age: float = 15,
                                vmmc_target_max_age: float = 29.999999,
                                vmmc_start_year: float = 2015,
                                vmmc_node_ids: Union[List[int], None] = None,
                                update_period: float = 30.4166666666667,
                                distributed_event_trigger: str = PROGRAM_VMMC):
    """
    Manages the addition of voluntary male medical circumcision (VMMC) reference tracking in the campaign.

    Args:
        campaign (emod_api.campaign): The campaign to which the VMMC reference tracking is to be added.
        vmmc_time_value_map (dict): A dictionary containing time-value map for VMMC.
        vmmc_reduced_acquire (float, optional): The reduced acquire rate for VMMC. Defaults to 0.6.
        vmmc_target_min_age (float, optional): The minimum age for VMMC target. Defaults to 15.
        vmmc_target_max_age (float, optional): The maximum age for VMMC target. Defaults to 29.999999.
        vmmc_start_year (float, optional): The start year for VMMC. Defaults to 2015.
        vmmc_node_ids (List[int], optional): A list of node IDs where the VMMC reference tracking is to be applied.
                                             Defaults to None, which applies to all nodes.
        update_period (float, optional): The update period for VMMC reference tracking. Defaults to 30.4166666666667.
        distributed_event_trigger (str, optional): The trigger for distributed event. Defaults to PROGRAM_VMMC.
        target_disease_state (str, optional): The target disease state for VMMC reference tracking. Defaults to HIV_NEGATIVE.

    Returns:
        str: The intervention name for male circumcision.

    Example:
        >>> add_vmmc_reference_tracking(campaign, vmmc_time_value_map={"Times": [2002, 2010.5, 2013.95], "Values": [200, 350, 500]}, vmmc_node_ids=[1, 2, 3], vmmc_reduced_acquire=0.5, vmmc_target_min_age=10, vmmc_target_max_age=30, vmmc_start_year=2010, update_period=30, distributed_event_trigger=PROGRAM_VMMC, target_disease_state=HIV_NEGATIVE)
    """
    malecirc_intervention_name = ANY_MC
    distribute_circumcision = MaleCircumcision(campaign,
                                               circumcision_reduced_acquire=vmmc_reduced_acquire,
                                               distributed_event_trigger=distributed_event_trigger,
                                               common_intervention_parameters=CommonInterventionParameters(
                                                   intervention_name=malecirc_intervention_name))
    targeting_config = ~IsHivPositive()
    tracking_config = HasIntervention(intervention_name=malecirc_intervention_name)
    add_intervention_reference_tracking(campaign,
                                        intervention_list=[distribute_circumcision],
                                        time_value_map=ValueMap(times=vmmc_time_value_map["Times"],
                                                                values=vmmc_time_value_map["Values"]),
                                        tracking_config=tracking_config,
                                        start_year=vmmc_start_year,
                                        update_period=update_period,
                                        target_demographics_config=TargetDemographicsConfig(target_age_max=vmmc_target_max_age,
                                                                                            target_age_min=vmmc_target_min_age,
                                                                                            target_gender=TargetGender.MALE,
                                                                                            demographic_coverage=None),
                                        targeting_config=targeting_config,
                                        event_name='Reference tracking of VMMC',
                                        node_ids=vmmc_node_ids)

    return malecirc_intervention_name


def add_historical_vmmc_nchooser(campaign: emod_api.campaign,
                                 historical_vmmc_distributions_by_time: pd.DataFrame,
                                 historical_vmmc_reduced_acquire: float = 0.6,
                                 historical_vmmc_property_restrictions: List[str] = None,
                                 historical_vmmc_node_ids: Union[List[int], None] = None,
                                 has_intervention_name_exclusion: str = ANY_MC,
                                 event_name='nchooser of VMMC'):
    """
    Adds voluntary male medical circumcision (VMMC) with NChooser coordinator to the campaign.
    This is used to add historical VMMC events to the campaign.

    Args:
        campaign (emod_api.campaign): The campaign to which the historical VMMC management is to be added.
        historical_vmmc_distributions_by_time (pd.DataFrame): A DataFrame containing the distributions of historical VMMC by time.
        historical_vmmc_reduced_acquire (float, optional): The reduced acquire rate for historical VMMC. Defaults to 0.6.
        historical_vmmc_property_restrictions (List[str], optional): A list of property restrictions for historical VMMC. Defaults to None.
        historical_vmmc_node_ids (List[int], optional): A list of node IDs where the historical VMMC management is to be applied.
                                                         Defaults to None, which applies to all nodes.
        has_intervention_name_exclusion (str, optional): The name of the intervention to look for in an individual when
                                                         targeting specific disease states. It's also the
                                                         Intervention_Name of the MaleCircumcision intervention. Defaults to ANY_MC,
                                                         to match the intervention name in add_traditional_vmmc() and add_vmmc_reference_tracking().
        event_name (str, optional): The name of the event. Defaults to 'nchooser of VMMC'.

    Returns:
        None

    Example:
        >>> data = {'year': [2010, 2010, 2011, 2011],
        >>>         'min_age': [1, 15, 1, 15],
        >>>         'max_age': [14.999, 49.999, 14.999, 49.999],
        >>>         'n_circumcisions': [200, 1300, 290, 1490]}
        >>> historical_vmmc_distributions_by_time = pd.DataFrame.from_dict(data)
        >>> add_historical_vmmc_nchooser(campaign,
        >>>                              historical_vmmc_distributions_by_time=historical_vmmc_distributions_by_time,
        >>>                              historical_vmmc_reduced_acquire=0.5,
        >>>                              historical_vmmc_property_restrictions=None,
        >>>                              historical_vmmc_node_ids=[1, 2, 3],
        >>>                              has_intervention_name_exclusion=ANY_MC)
    """

    if historical_vmmc_property_restrictions is not None:
        historical_vmmc_property_restrictions = PropertyRestrictions(individual_property_restrictions=[historical_vmmc_property_restrictions])

    historical_vmmc_distributions_by_time['num_targeted_male'] = historical_vmmc_distributions_by_time['n_circumcisions']
    mc_intervention = MaleCircumcision(campaign,
                                       circumcision_reduced_acquire=historical_vmmc_reduced_acquire,
                                       distributed_event_trigger=PROGRAM_VMMC,
                                       common_intervention_parameters=CommonInterventionParameters(
                                           intervention_name=has_intervention_name_exclusion))
    add_intervention_nchooser_df(
        campaign,
        intervention_list=[mc_intervention],
        distribution_df=historical_vmmc_distributions_by_time,
        target_disease_state=[[HIV_NEGATIVE, NOT_HAVE_INTERVENTION]],
        target_disease_state_has_intervention_name=has_intervention_name_exclusion,
        property_restrictions=historical_vmmc_property_restrictions,
        event_name=event_name,
        node_ids=historical_vmmc_node_ids
    )

def add_health_care_testing(campaign: emod_api.campaign,
                            hct_node_ids: Union[List[int], None] = None,
                            hct_start_year: float = 1990,
                            hct_reentry_rate: float = 1,
                            hct_retention_rate: float = 0.95,
                            hct_delay_to_next_test: Union[int, List[int]] = None,
                            hct_delay_to_next_test_node_ids: Union[List[int], None] = None,
                            hct_delay_to_next_test_node_names: Union[List[str], None] = None,
                            tvmap_test_for_enter_HCT_testing_loop: dict = all_negative_time_value_map,
                            tvmap_consider_immediate_ART: dict = all_negative_time_value_map):
    """
    Manages the addition of health care testing in the campaign.

    Args:
      campaign (emod_api.campaign): The campaign to which the health care testing is to be added.
      hct_node_ids (List[int], optional): A list of node IDs where the health care testing is to be applied.
                                           Defaults to None, which applies to all nodes.
      hct_start_year (float, optional): The start year for health care testing. Defaults to 1990.
      hct_reentry_rate (float, optional): The reentry rate for health care testing. Defaults to 1.
      hct_retention_rate (float, optional): The retention rate for health care testing. Defaults to 0.95.
      hct_delay_to_next_test (Union[int, List[int]], optional): The delay to the next test in days. If it's a list, it
        will add different delays(using HIVMuxer) for different node sets which are defined in
        hct_delay_to_next_test_node_ids. If it's a single value, it will apply the same delay to all nodes in
        hct_node_ids. Defaults to None, which will apply the Zambia model default values: [730, 365, 1100].
      hct_delay_to_next_test_node_ids (List[int], optional): A list of node sets where the different delays will be
        applied. It's used when hct_delay_to_next_test is a list. Defaults to None, which will apply the Zambia
        model default values: [[1, 2, 3, 4, 6, 7], [5, 9, 10], [8]].
      hct_delay_to_next_test_node_names (List[str], optional): A list of node set names where the different delays will be
        applied. It's used when hct_delay_to_next_test is a list. Defaults to None, which will apply the Zambia
        model default values: ['Default', 'Lusaka, Southern, Western', 'Northern'].
      tvmap_test_for_enter_HCT_testing_loop (dict, optional): A dictionary containing time-value map for testing for
        entering HCT testing loop in HCTUptakePostDebut state. Defaults to all_negative_time_value_map.
      tvmap_consider_immediate_ART (dict, optional): A dictionary containing time-value map for considering immediate ART
        in HCTTestingLoop state. Defaults to all_negative_time_value_map.

    Returns:
      None

    Example:
        >>> add_health_care_testing(
        >>>     campaign,
        >>>     hct_node_ids=[1, 2, 3],
        >>>     hct_start_year=1995,
        >>>     hct_reentry_rate=0.9,
        >>>     hct_retention_rate=0.85,
        >>>     hct_delay_to_next_test=365
        >>> )
    """
    disqualifying_properties = [CascadeState.LOST_FOREVER,
                                CascadeState.ON_ART,
                                CascadeState.LINKING_TO_ART,
                                CascadeState.ON_PRE_ART,
                                CascadeState.LINKING_TO_PRE_ART,
                                CascadeState.ART_STAGING]

    # Add interventions for HCTUptakeAtDebut
    add_state_HCTUptakeAtDebut(campaign=campaign,
                               disqualifying_properties=disqualifying_properties,
                               node_ids=hct_node_ids,
                               start_year=hct_start_year)

    # Add interventions for HCTUptakePostDebut
    add_state_HCTUptakePostDebut(campaign=campaign,
                                 disqualifying_properties=disqualifying_properties,
                                 node_ids=hct_node_ids,
                                 hct_reentry_rate=hct_reentry_rate,
                                 start_year=hct_start_year,
                                 tvmap_test_for_enter_HCT_testing_loop=tvmap_test_for_enter_HCT_testing_loop)

    if hct_delay_to_next_test is None:
        hct_delay_to_next_test = [730, 365, 1100]  # Default values for Zambia model
    if hct_delay_to_next_test_node_ids is None:
        hct_delay_to_next_test_node_ids = [[1, 2, 3, 4, 6, 7], [5, 9, 10], [8]]  # Default values for Zambia model
    if hct_delay_to_next_test_node_names is None:
        hct_delay_to_next_test_node_names = ['Default', 'Lusaka, Southern, Western', 'Northern']  # Default values for Zambia model

    # Add interventions for HCTTestingLoop
    add_state_HCTTestingLoop(campaign=campaign,
                             disqualifying_properties=disqualifying_properties,
                             node_ids=hct_node_ids,
                             hct_retention_rate=hct_retention_rate,
                             start_year=hct_start_year,
                             tvmap_consider_immediate_ART=tvmap_consider_immediate_ART,
                             hct_delay_to_next_test=hct_delay_to_next_test,
                             hct_delay_to_next_test_node_ids=hct_delay_to_next_test_node_ids,
                             hct_delay_to_next_test_node_names=hct_delay_to_next_test_node_names)


def add_ART_cascade(campaign: emod_api.campaign,
                    art_cascade_node_ids: Union[List[int], None] = None,
                    art_cascade_start_year: float = 1990,
                    art_cascade_pre_staging_retention: float = 0.85,
                    art_cascade_cd4_retention_rate: float = 1,
                    art_cascade_pre_art_retention: float = 0.75,
                    art_cascade_immediate_art_rate: float = 0.1,
                    art_cascade_art_reenrollment_willingness: float = 0.9,
                    tvmap_increased_symptomatic_presentation: dict = all_negative_time_value_map,
                    tvmap_immediate_ART_restart: dict = all_negative_time_value_map,
                    tvmap_reconsider_lost_forever: dict = all_negative_time_value_map):
    """
    Manages the addition of Antiretroviral Therapy (ART) cascade in the campaign.

    Args:
       campaign (emod_api.campaign): The campaign to which the ART cascade is to be added.
       art_cascade_node_ids (List[int], optional): A list of node IDs where the ART cascade is to be applied.
                                                   If None, the ART cascade applies to all nodes. Defaults to None.
       art_cascade_start_year (float, optional): The start year for the ART cascade. Defaults to 1990.
       art_cascade_pre_staging_retention (float, optional): The retention rate before ART staging. Defaults to 0.85.
       art_cascade_cd4_retention_rate (float, optional): The retention rate for CD4 count. Defaults to 1.
       art_cascade_pre_art_retention (float, optional): The retention rate before ART. Defaults to 0.75.
       art_cascade_immediate_art_rate (float, optional): The rate for immediate ART. Defaults to 0.1.
       art_cascade_art_reenrollment_willingness (float, optional): The willingness rate for ART reenrollment. Defaults to 0.9.
       tvmap_increased_symptomatic_presentation (dict, optional): A dictionary containing time-value map for increased
         symptomatic presentation in TestingOnSymptomatic state. Defaults to all_negative_time_value_map.
       tvmap_immediate_ART_restart (dict, optional): A dictionary containing time-value map for immediate ART restart in
         OnART state. Defaults to all_negative_time_value_map.
       tvmap_reconsider_lost_forever (dict, optional): A dictionary containing time-value map for reconsidering lost
         forever in LostForever state. Defaults to all_negative_time_value_map.

    Returns:
       None

    Example:
       >>> add_ART_cascade(campaign, art_cascade_node_ids=[1, 2, 3], art_cascade_start_year=1995, art_cascade_pre_staging_retention=0.8, art_cascade_cd4_retention_rate=0.9, art_cascade_pre_art_retention=0.7, art_cascade_immediate_art_rate=0.15, art_cascade_art_reenrollment_willingness=0.85)
    """
    disqualifying_properties = [CascadeState.LOST_FOREVER,
                                CascadeState.ON_ART,
                                CascadeState.LINKING_TO_ART,
                                CascadeState.ON_PRE_ART,
                                CascadeState.LINKING_TO_PRE_ART]

    disqualifying_properties_plus_art_staging = disqualifying_properties + [CascadeState.ART_STAGING]

    # Add interventions for TestingOnSymptomatic
    add_state_TestingOnSymptomatic(campaign=campaign,
                                   node_ids=art_cascade_node_ids,
                                   disqualifying_properties=disqualifying_properties_plus_art_staging,
                                   start_year=art_cascade_start_year,
                                   tvmap_increased_symptomatic_presentation=tvmap_increased_symptomatic_presentation)

    #
    # BEGIN ART STAGING SECTION
    #

    # Add interventions for ARTStagingDiagnosticTest
    add_state_ARTStagingDiagnosticTest(campaign=campaign,
                                       node_ids=art_cascade_node_ids,
                                       disqualifying_properties=disqualifying_properties,
                                       start_year=art_cascade_start_year)

    # Add interventions for ARTStaging
    add_state_ARTStaging(campaign=campaign,
                         cd4_retention_rate=art_cascade_cd4_retention_rate,
                         pre_staging_retention=art_cascade_pre_staging_retention,
                         node_ids=art_cascade_node_ids,
                         disqualifying_properties=disqualifying_properties,
                         start_year=art_cascade_start_year)

    #
    # END ART STAGING SECTION
    #

    #
    # BEGIN PRE-ART
    #

    # chance of linking to pre-ART
    # QUESTION: should we exclude CascadeState:LinkingToPreART, too?
    disqualifying_properties_pre_art_linking = [CascadeState.LOST_FOREVER,
                                                CascadeState.ON_ART,
                                                CascadeState.LINKING_TO_ART,
                                                CascadeState.ON_PRE_ART]

    # Add interventions for LinkingToPreART
    add_state_LinkingToPreART(campaign=campaign,
                              node_ids=art_cascade_node_ids,
                              disqualifying_properties=disqualifying_properties_pre_art_linking,
                              start_year=art_cascade_start_year)

    # ensuring each agent continues this cascade once per timestep
    disqualifying_properties_pre_art = [CascadeState.LOST_FOREVER,
                                        CascadeState.ON_ART,
                                        CascadeState.LINKING_TO_ART]

    # Add interventions for OnPreART
    add_state_OnPreART(campaign=campaign,
                       node_ids=art_cascade_node_ids,
                       pre_art_retention=art_cascade_pre_art_retention,
                       disqualifying_properties=disqualifying_properties_pre_art,
                       start_year=art_cascade_start_year)

    #
    # END PRE-ART
    #

    #
    # BEGIN ART LINKING
    #

    art_linking_disqualifying_properties = [CascadeState.LOST_FOREVER, CascadeState.ON_ART]

    # Add interventions for LinkingToART
    add_state_LinkingToART(campaign=campaign,
                           node_ids=art_cascade_node_ids,
                           disqualifying_properties=art_linking_disqualifying_properties,
                           start_year=art_cascade_start_year)

    # decide to initiate ART now or later
    disqualifying_properties_art = [CascadeState.LOST_FOREVER]

    # Add interventions for OnART
    add_state_OnART(campaign=campaign,
                    art_reenrollment_willingness=art_cascade_art_reenrollment_willingness,
                    immediate_art_rate=art_cascade_immediate_art_rate,
                    node_ids=art_cascade_node_ids,
                    disqualifying_properties=disqualifying_properties_art,
                    start_year=art_cascade_start_year,
                    tvmap_immediate_ART_restart=tvmap_immediate_ART_restart,
                    tvmap_reconsider_lost_forever=tvmap_reconsider_lost_forever)

    # Add interventions for LostForever
    add_state_LostForever(campaign=campaign, node_ids=art_cascade_node_ids, start_year=art_cascade_start_year)


def add_state_TestingOnANC(campaign: emod_api.campaign,
                           disqualifying_properties: List[str],
                           coverage: float,
                           link_to_ART_rate: float,
                           node_ids: Union[List[int], None],
                           sigmoid_min: float,
                           sigmoid_max: float,
                           sigmoid_midyear: float,
                           sigmoid_rate: float,
                           treatment_a_efficacy: float,
                           treatment_b_efficacy: float,
                           sdNVP_efficacy: float,
                           start_year: float,
                           property_restrictions: Union[List[str], str] = 'Accessibility:Yes') -> str:
    """

    Manages the addition of Testing on Antenatal Care (ANC) in the campaign.

    This state is triggered when an individual reaches 'TwelveWeeksPregnant'. At some point in this state, it initiates
    the ARTStaging state. The transition to the ARTStaging state is governed by an event, identified as
    ART_STAGING_TRIGGER_1. The occurrence of this event is determined by a random choice mechanism with a rate equal to
    link_to_ART_rate.

    Args:
        campaign (emod_api.campaign): The campaign object to which the Testing on ANC state is to be added.
        disqualifying_properties (List[str]): A list of disqualifying properties for the Testing on ANC state.
        coverage (float): The coverage of Testing on ANC among the population.
        link_to_ART_rate (float): The rate for linking to ART. This is used to determine the transition to the
            ARTStaging state.
        node_ids (Union[List[int], None]): A list of node IDs where the Testing on ANC state is to be applied. If
            None, the Testing on ANC state applies to all nodes.
        sigmoid_min (float): The left asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_max (float): The right asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_midyear (float): The time of the infection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_rate (float): The slope of the inflection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention. A Rate of 1 sets the slope to a 25% change in probability
            per year.
        treatment_a_efficacy (float): The efficacy of treatment A.
        treatment_b_efficacy (float): The efficacy of treatment B.
        sdNVP_efficacy (float): The efficacy of Single-Dose Nevirapine (sdNVP).
        start_year (float): The start year for the Testing on ANC state.
        property_restrictions (Union[List[str], str], optional): The property restrictions for the Testing on ANC state.
            Defaults to 'Accessibility:Yes'.

    Returns:
        str: The trigger event name for the ARTStaging state.

    """
    initial_trigger = TWELVE_WEEKS_PREGNANT
    if not isinstance(property_restrictions, list):
        property_restrictions = [property_restrictions]
    testing_on_ANC_pv = CascadeState.TESTING_ON_ANC
    # PMTCT HIV diagnostic test availability by time
    need_pmtct_disgnostic_test_event = 'Needs_PMTCT_Diagnostic_Test'
    diagnostic_availability = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                               year_sigmoid=Sigmoid(min=sigmoid_min,
                                                                                    max=sigmoid_max,
                                                                                    mid=sigmoid_midyear,
                                                                                    rate=sigmoid_rate),
                                                               positive_diagnosis_event=need_pmtct_disgnostic_test_event,
                                                               negative_diagnosis_event=None,
                                                               common_intervention_parameters=CommonInterventionParameters(new_property_value=testing_on_ANC_pv,
                                                                                                                           disqualifying_properties=disqualifying_properties))
    add_intervention_triggered(campaign,
                               intervention_list=[diagnostic_availability],
                               triggers_list=[initial_trigger],
                               start_year=start_year,
                               target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.FEMALE,
                                                                                   demographic_coverage=coverage),
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[property_restrictions]),
                               node_ids=node_ids,
                               event_name='Availability of PMTCT diagnostic test')

    # distributing PMTCT HIV diagnostic test
    hiv_positive_at_anc_event = 'HIV_Positive_at_ANC'
    
    pmtct_hiv_test = HIVRapidHIVDiagnostic(campaign,
                                           positive_diagnosis_event=hiv_positive_at_anc_event,
                                           negative_diagnosis_event=None,
                                           base_sensitivity=1,
                                           common_intervention_parameters=CommonInterventionParameters(new_property_value=testing_on_ANC_pv,
                                                                                                       disqualifying_properties=disqualifying_properties))
    add_intervention_triggered(campaign,
                               intervention_list=[pmtct_hiv_test],
                               triggers_list=[need_pmtct_disgnostic_test_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='PMTCT diagnostic test')

    # Chance to enter ART post-positive result during ANC
    # QUESTION: should we send the signal ARTStaging2 instead? We already have a 0.8/0.2 dropout from PMTCT test here. Why double the chance to drop?
    choices = {ART_STAGING_TRIGGER_1: link_to_ART_rate,
               DUMMY_TRIGGER: round(1 - link_to_ART_rate, 7)}  # to get rid of floating point decimal issues
    
    link_to_ART_decision = HIVRandomChoice(campaign,
                                           choice_names=list(choices.keys()),
                                           choice_probabilities=list(choices.values()),
                                           common_intervention_parameters=CommonInterventionParameters(new_property_value=testing_on_ANC_pv,
                                                                                                       disqualifying_properties=disqualifying_properties))
    add_intervention_triggered(campaign,
                               intervention_list=[link_to_ART_decision],
                               triggers_list=[hiv_positive_at_anc_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Linking from PMTCT positive result to ART')

    # PMTCT treatment selection based on time
    needs_sdnvp_pmtct_event = 'Needs_sdNVP_PMTCT'
    needs_combination_pmtct_event = 'Needs_Combination_PMTCT'

    treatment_selection = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                           year_sigmoid=Sigmoid(min=0,
                                                                                max=1,
                                                                                mid=2008.4,
                                                                                rate=-1),
                                                          positive_diagnosis_event=needs_sdnvp_pmtct_event,
                                                          negative_diagnosis_event=needs_combination_pmtct_event,
                                                          common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                      new_property_value=testing_on_ANC_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[treatment_selection],
                               triggers_list=[hiv_positive_at_anc_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='ANC/PMTCT: Choose Single-Dose Nevirapine (sdNVP) or Combination (Option A/B)')

    # PMTCT treatment with sdNVP
    sdNVP_treatment = PMTCT(campaign,
                            efficacy=sdNVP_efficacy,
                            common_intervention_parameters=CommonInterventionParameters(intervention_name="PMTCT_sdNVP"))
    add_intervention_triggered(campaign,
                               intervention_list=[sdNVP_treatment],
                               triggers_list=[needs_sdnvp_pmtct_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='ANC/PMTCT: Less Effective PMTCT (sdNVP)')

    # PMTCT combination treatment selection
    time_value_map = {"Times": [2013.249], "Values": [1]}
    needs_option_a_event = 'Needs_Option_A'
    needs_option_b_event = 'Needs_Option_B'

    combination_treatment_selection = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                                         time_value_map=ValueMap(times=time_value_map["Times"],
                                                                                                 values=time_value_map["Values"]),
                                                                         positive_diagnosis_event=needs_option_b_event,
                                                                         negative_diagnosis_event=needs_option_a_event,
                                                                         common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                                     new_property_value=testing_on_ANC_pv))

    add_intervention_triggered(campaign,
                               intervention_list=[combination_treatment_selection],
                               triggers_list=[needs_combination_pmtct_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='ANC/PMTCT: Combination Option A or B?')

    # PMTCT treatment with combination A
    pmtct_combination_treatment_A = PMTCT(campaign,
                                          efficacy=treatment_a_efficacy,
                                          common_intervention_parameters=CommonInterventionParameters(intervention_name="PMTCT_Option_A"))
    add_intervention_triggered(campaign,
                               intervention_list=[pmtct_combination_treatment_A],
                               triggers_list=[needs_option_a_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='ANC/PMTCT (Option A)')

    # PMTCT treatment with combination B
    pmtct_combination_treatment_B = PMTCT(campaign,
                                          efficacy=treatment_b_efficacy,
                                          common_intervention_parameters=CommonInterventionParameters(intervention_name="PMTCT_Option_B"))
    add_intervention_triggered(campaign,
                               intervention_list=[pmtct_combination_treatment_B],
                               triggers_list=[needs_option_b_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='ANC/PMTCT (Option B)')

    return ART_STAGING_TRIGGER_1  # return the trigger for the ARTStaging state


def add_state_TestingOnChild6w(campaign: emod_api.campaign,
                               start_year: float,
                               disqualifying_properties: List[str],
                               time_value_map: Union[Dict[float, float], Dict[str, List[float]]],
                               node_ids: Union[List[int], None],
                               property_restrictions: Union[List[str], str] = 'Accessibility:Yes'):

    """
    This function adds a state for testing on children at 6 weeks old in the campaign.

    When an individual broadcast the 'SixWeeksOld' event, this state is triggered. If the test result is positive, it
    will then trigger the ARTStagingDiagnosticTest state using the event identified as ART_STAGING_DIAGNOSTIC_TEST_TRIGGER.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        start_year (float): The start year for the state.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        time_value_map (Union[Dict[float, float], Dict[str, List[float]]]): A map of times to values for the
            HIVPiecewiseByYearAndSexDiagnostic intervention.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        property_restrictions (Union[List[str], str], optional): The property restrictions for the state. Defaults to
            'Accessibility:Yes'.

    Returns:
        str: The trigger event name for the ARTStagingDiagnosticTest state.
    """
    initial_trigger = SIX_WEEKS_OLD
    if not isinstance(property_restrictions, list):
        property_restrictions = [property_restrictions]
    testing_child_pv = CascadeState.TESTING_ON_CHILD_6W
    if 'Times' in time_value_map:
        time_value_map = convert_time_value_map(time_value_map)

    child_hiv_test = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                        time_value_map=ValueMap(times=list(time_value_map.keys()), 
                                                                                values=list(time_value_map.values())),
                                                        positive_diagnosis_event=ART_STAGING_DIAGNOSTIC_TEST_TRIGGER,
                                                        negative_diagnosis_event=None,
                                                        linear_interpolation=True,
                                                        common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                    new_property_value=testing_child_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[child_hiv_test],
                               triggers_list=[initial_trigger],
                               start_year=start_year,
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[property_restrictions]),
                               node_ids=node_ids,
                               event_name='CHILD 6W TESTING')
    return ART_STAGING_DIAGNOSTIC_TEST_TRIGGER  # return the trigger for the ARTStagingDiagnosticTest state


def add_state_HCTUptakeAtDebut(campaign: emod_api.campaign,
                               disqualifying_properties: List[str],
                               node_ids: Union[List[int], None],
                               start_year: float,
                               female_multiplier: float = 1) -> Tuple[str, str]:
    """
    This function manages the addition of Health Care Testing (HCT) uptake at sexual debut in the campaign.

    When an individual receives the 'STIDebut' event, this state is activated. If the test result is positive, it
    triggers the HCTTestingLoop state using the event identified as HCT_TESTING_LOOP_TRIGGER. If the test result is
    negative, it immediately triggers the HCTUpdatePostDebut state using the event identified as
    HCT_UPTAKE_POST_DEBUT_TRIGGER_1.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        start_year (float): The start year for the state.
        female_multiplier (float, optional): The multiplier for female individuals in the
            HIVSigmoidByYearAndSexDiagnostic intervention. Defaults to 1.

    Returns:
        Tuple[str, str]: The trigger events for the HCTTestingLoop and HCTUpdatePostDebut states.
    """

    initial_trigger = CustomEvent.STI_DEBUT
    hct_upate_at_debut_pv = CascadeState.HCT_UPTAKE_AT_DEBUT
    
    # set up health care testing uptake at sexual debut by time
    uptake_choice = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                     year_sigmoid=Sigmoid(min=-0.005,
                                                                          max=0.05,
                                                                          mid=2005,
                                                                          rate=1),
                                                     positive_diagnosis_event=HCT_TESTING_LOOP_TRIGGER,
                                                     negative_diagnosis_event=HCT_UPTAKE_POST_DEBUT_TRIGGER_1,
                                                     female_multiplier=female_multiplier,
                                                     common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                 new_property_value=hct_upate_at_debut_pv,
                                                                                                                 cost=0))
    add_intervention_triggered(campaign,
                               intervention_list=[uptake_choice],
                               triggers_list=[initial_trigger],
                               start_year=start_year,
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[['Accessibility:Yes']]),
                               node_ids=node_ids,
                               event_name='HCTUptakeAtDebut: state 0 (decision, sigmoid by year and sex)')

    return (HCT_TESTING_LOOP_TRIGGER,  # return the trigger for the HCTTestingLoop state
            HCT_UPTAKE_POST_DEBUT_TRIGGER_1)  # return the trigger for the HCTUpdatePostDebut state


def add_state_HCTUptakePostDebut(campaign: emod_api.campaign,
                                 disqualifying_properties: List[str],
                                 node_ids: Union[List[int], None],
                                 hct_reentry_rate: float,
                                 start_year: float,
                                 tvmap_test_for_enter_HCT_testing_loop: dict = all_negative_time_value_map) -> str:
    """
    This function manages the addition of Health Care Testing (HCT) uptake post sexual debut in the campaign.

    This state is activated by the events HCT_UPTAKE_POST_DEBUT_TRIGGER_1, HCT_UPTAKE_POST_DEBUT_TRIGGER_2, and
    HCT_UPTAKE_POST_DEBUT_TRIGGER_3. If the test result is positive, it triggers the HCTTestingLoop state using the
    event identified as HCT_TESTING_LOOP_TRIGGER. If the test result is negative, it reverts back to this state using
    the event identified as HCT_UPTAKE_POST_DEBUT_TRIGGER_1.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        hct_reentry_rate (float): The rate at which individuals reenter the HCT uptake post sexual debut state.
        start_year (float): The start year for the state.
        tvmap_test_for_enter_HCT_testing_loop (dict, optional): Time value map for HIVPiecewiseByYearAndSexDiagnostic
            intervention. Defaults to all_negative_time_value_map which will always trigger the Negative event.

    Returns:
        str: The trigger for the HCTTestingLoop state.

    """
    hct_uptake_post_debut_pv = CascadeState.HCT_UPTAKE_POST_DEBUT
    # These are the initial trigger of this state:
    hivmuxer_trigger = HCT_UPTAKE_POST_DEBUT_TRIGGER_1
    random_choice_trigger = [HCT_UPTAKE_POST_DEBUT_TRIGGER_2, HCT_UPTAKE_POST_DEBUT_TRIGGER_3]

    # used in this state only
    is_post_debut_trigger = CustomEvent.HCT_UPTAKE_POST_DEBUT_0

    # initialization of health care testing (hct) at specified starting year
    
    initialize_hct = BroadcastEvent(campaign, broadcast_event=is_post_debut_trigger,
                                    common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                new_property_value=hct_uptake_post_debut_pv))
    add_intervention_scheduled(campaign,
                               intervention_list=[initialize_hct],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='HCTUptakePostDebut: HCT Uptake Initialization')

    # reentry into uptake loop from lost-to-followup and ART dropout
    # QUESTION: ask... should this be HCTUptakePostDebut1 **1** ?? (can someone be non-debut and artdropout or ltfu? (maybe exposed children??)
    
    choices = {is_post_debut_trigger: hct_reentry_rate, DUMMY_TRIGGER: round(1 - hct_reentry_rate, 7)} # to get rid of floating point decimal issues
    reentry_decision = HIVRandomChoice(campaign,
                                       choice_names=list(choices.keys()),
                                       choice_probabilities=list(choices.values()),
                                       common_intervention_parameters=CommonInterventionParameters(new_property_value=hct_uptake_post_debut_pv, cost=0)
                                       )
    add_intervention_triggered(campaign,
                               intervention_list=[reentry_decision],
                               triggers_list=random_choice_trigger,
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='HCTUptakePostDebut: state 3 (From LTFU or ART dropout back into HCT uptake loop)')

    # ensure that everyone who is entering the health care testing system is post-debut (this is a filter: must be
    # post-debut to proceed)
    is_post_debut_check = STIIsPostDebut(campaign,
                                         positive_diagnosis_event=hivmuxer_trigger,
                                         negative_diagnosis_event=None)
    add_intervention_triggered(campaign,
                               intervention_list=[is_post_debut_check],
                               triggers_list=[is_post_debut_trigger],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Ensure HCTUptakePostDebut0 agents are post-debut')
    # Up-to 1-year delay before an agent makes further decisions on making further hct uptake decisions
    # used in this state only
    sigmoiddiag_trigger = CustomEvent.HCT_UPTAKE_POST_DEBUT_2
    disqualifying_properties_plus_hct_loop = disqualifying_properties + [CascadeState.HCT_TESTING_LOOP]
    delay_to_uptake_decision = HIVMuxer(campaign,
                                        muxer_name='HCTUptakePostDebut',
                                        delay_period_distribution=ExponentialDistribution(mean=365),
                                        broadcast_delay_complete_event=sigmoiddiag_trigger,
                                        common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties_plus_hct_loop,
                                                                                                    new_property_value=hct_uptake_post_debut_pv))

    add_intervention_triggered(campaign,
                               intervention_list=[delay_to_uptake_decision],
                               triggers_list=[hivmuxer_trigger],
                               start_year=start_year,
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[['Accessibility:Yes']]),
                               node_ids=node_ids,
                               event_name=f'{hivmuxer_trigger}: state 1 (1-year delay, reachable)')

    # decision on hct uptake
    # used in this state only
    consider_enter_HCT_testing_loop_trigger = CustomEvent.HCT_UPTAKE_POST_DEBUT_7
    uptake_decision = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                       positive_diagnosis_event=HCT_TESTING_LOOP_TRIGGER,
                                                       negative_diagnosis_event=consider_enter_HCT_testing_loop_trigger,
                                                       year_sigmoid=Sigmoid(min=-0.01,
                                                                            max=0.15,
                                                                            mid=2006,
                                                                            rate=1),
                                                       common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties_plus_hct_loop,
                                                                                                                   new_property_value=hct_uptake_post_debut_pv))

    add_intervention_triggered(campaign,
                               intervention_list=[uptake_decision],
                               triggers_list=[sigmoiddiag_trigger],
                               start_year=start_year,
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[['Accessibility:Yes']]),
                               node_ids=node_ids,
                               event_name='HCTUptakePostDebut: state 2 (Decision to uptake HCT)')

    # if test negative in previous step, get an HIVPiecewiseByYearAndSexDiagnostic test and consider entering the hct
    # testing loop if test positive, if test negative, trigger hivmuxer again.
    consider_enter_HCT_testing_loop = HIVPiecewiseByYearAndSexDiagnostic(
        campaign,
        time_value_map=ValueMap(times=list(tvmap_test_for_enter_HCT_testing_loop.keys()), 
                                values=list(tvmap_test_for_enter_HCT_testing_loop.values())),
        positive_diagnosis_event=HCT_TESTING_LOOP_TRIGGER,
        negative_diagnosis_event=hivmuxer_trigger,
        common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties_plus_hct_loop,
                                                                    new_property_value=hct_uptake_post_debut_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[consider_enter_HCT_testing_loop],
                               triggers_list=[consider_enter_HCT_testing_loop_trigger],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Consider enter HCT testing loop if test positive post debut, if test negative, trigger hivmuxer again.')
    return HCT_TESTING_LOOP_TRIGGER  # return the trigger for the HCTTestingLoop state


def add_state_HCTTestingLoop(campaign: emod_api.campaign,
                             disqualifying_properties: List[str],
                             node_ids: Union[List[int], None],
                             hct_retention_rate: float,
                             start_year: float,
                             hct_delay_to_next_test: Union[float, List[float]],
                             hct_delay_to_next_test_node_ids: Union[List[List[int]], None] = None,
                             hct_delay_to_next_test_node_names: Union[List[str], None] = None,
                             tvmap_consider_immediate_ART: dict = all_negative_time_value_map) -> (str, str, str):
    """
    This function manages the addition of Health Care Testing (HCT) testing loop in the campaign.

    This state is triggered by the HCT_TESTING_LOOP_TRIGGER event. Initially, it goes through a hivmuxer intervention
    with an exponential delay, the mean of which equals hct_delay_to_next_test. Subsequently, a rapid HIV test is
    conducted. If the test result is positive, a 'consider_immediate_ART' test is triggered. If the test result is
    negative, a random choice intervention is triggered to decide whether the individual should remain in the loop
    (with rate = hct_retention_rate) or drop out and transition to the HCTUptakePostDebut state using the
    HCT_UPTAKE_POST_DEBUT_TRIGGER_1 event. If the 'consider_immediate_ART' test is positive, it triggers the transition
    to the OnART state using the ON_ART_TRIGGER_2 event. If the 'consider_immediate_ART' test is negative, it triggers
    the transition to the ARTStaging state using the ART_STAGING_TRIGGER_1 event.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.

        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        hct_retention_rate (float): The rate at which individuals remain in the HCT testing loop in the random choice
            intervention.
        start_year (float): The start year for the state.
        hct_delay_to_next_test (Union[float, List[float]]): The mean delay for the hivmuxer intervention in the HCT testing
            loop. Can be a single value or a list of values for different nodes.
        hct_delay_to_next_test_node_ids (Union[List[List[int]], None], optional): A 2D list specifying the node IDs for
            each delay period in the hivmuxer intervention. This argument must be provided if hct_delay_to_next_test is
            a list and should have the same length as hct_delay_to_next_test. If None, the node IDs will be the same as
            the previous node_ids argument. Defaults to None.
        hct_delay_to_next_test_node_names (Union[List[str], None], optional): A list of node names for each delay period
            in the hivmuxer intervention. This argument must be provided if hct_delay_to_next_test is a list and should
            have the same length as hct_delay_to_next_test. If None, the node names will be 'Default'. Defaults to None.
        tvmap_consider_immediate_ART (dict, optional): Time value map for considering immediate ART. Defaults to
            all_negative_time_value_map which will always trigger the Negative event and transition to ARTStaging state.

    Returns:
        Tuple[str, str, str]: The triggers for the HCTUptakePostDebut, OnART, and ARTStaging states.

    Examples:
        This example demonstrates how to add the HCTTestingLoop state to the campaign with different delay periods for each
        region/node

        >>> disqualifying_properties = [CascadeState.LOST_FOREVER,
        >>>                             CascadeState.ON_ART,
        >>>                             CascadeState.LINKING_TO_ART,
        >>>                             CascadeState.ON_PRE_ART,
        >>>                             CascadeState.LINKING_TO_PRE_ART,
        >>>                             CascadeState.ART_STAGING]
        >>> hct_retention_rate = 0.95
        >>> hct_delay_to_next_test = [730, 365, 1100]
        >>> hct_delay_to_next_test_node_ids = [[1, 2, 3, 4, 6, 7], [5, 9, 10], [8]]
        >>> hct_delay_to_next_test_node_names = ['Default', 'Lusaka, Southern, Western', 'Northern']
        >>> art_cascade_start_year = 1995
        >>> add_state_HCTTestingLoop(campaign=camp,
        >>>                          disqualifying_properties=disqualifying_properties,
        >>>                          hct_delay_to_next_test=hct_delay_to_next_test,
        >>>                          node_ids=None,
        >>>                          hct_retention_rate=hct_retention_rate,
        >>>                          start_year=art_cascade_start_year,
        >>>                          tvmap_consider_immediate_ART=all_negative_time_value_map,
        >>>                          hct_delay_to_next_test_node_ids=hct_delay_to_next_test_node_ids,
        >>>                          hct_delay_to_next_test_node_names=hct_delay_to_next_test_node_names))

        This example demonstrates how to add the HCTTestingLoop state to the campaign with a single delay period for all
        regions/nodes.
        >>> disqualifying_properties = [CascadeState.LOST_FOREVER,
        >>>                             CascadeState.ON_ART,
        >>>                             CascadeState.LINKING_TO_ART,
        >>>                             CascadeState.ON_PRE_ART,
        >>>                             CascadeState.LINKING_TO_PRE_ART,
        >>>                             CascadeState.ART_STAGING]
        >>> hct_retention_rate = 0.95
        >>> hct_delay_to_next_test = 365
        >>> art_cascade_start_year = 1995
        >>> add_state_HCTTestingLoop(campaign=camp,
        >>>                          disqualifying_properties=disqualifying_properties,
        >>>                          hct_delay_to_next_test=hct_delay_to_next_test,
        >>>                          node_ids=None,
        >>>                          hct_retention_rate=hct_retention_rate,
        >>>                          start_year=art_cascade_start_year,
        >>>                          tvmap_consider_immediate_ART=all_negative_time_value_map)
    """
    hct_testing_loop_pv = CascadeState.HCT_TESTING_LOOP

    initial_trigger = HCT_TESTING_LOOP_TRIGGER
    # testing loop -- delay until next test, please note that this is an exponential delay distribution
    diagnostic_trigger = CustomEvent.HCT_TESTING_LOOP_1
    if isinstance(hct_delay_to_next_test, int):
        hct_delay_to_next_test = [hct_delay_to_next_test]
        if hct_delay_to_next_test_node_ids is None:
            hct_delay_to_next_test_node_ids = [node_ids]
        if hct_delay_to_next_test_node_names is None:
            hct_delay_to_next_test_node_names = ['Default']
    elif isinstance(hct_delay_to_next_test, list):
        if (not isinstance(hct_delay_to_next_test_node_ids,   list) or # noqa: W504, E241
            not isinstance(hct_delay_to_next_test_node_names, list)):  # noqa: E129
            raise ValueError("hct_delay_to_next_test_node_ids and hct_delay_to_next_test_node_names must be provided "
                             "if hct_delay_to_next_test is a list.")
        elif (len(hct_delay_to_next_test) != len(hct_delay_to_next_test_node_ids  ) or # noqa: W504
              len(hct_delay_to_next_test) != len(hct_delay_to_next_test_node_names)):
            raise ValueError("hct_delay_to_next_test, hct_delay_to_next_test_node_ids, and "
                             "hct_delay_to_next_test_node_names must have the same length.")
    else:
        raise ValueError("hct_delay_to_next_test must be an int or a list of int.")
    for delay_period, delay_node_ids, node_name in zip(hct_delay_to_next_test, hct_delay_to_next_test_node_ids,
                                                       hct_delay_to_next_test_node_names):
        delay_to_next_hct = HIVMuxer(campaign,
                                     muxer_name='HCTTestingLoop',
                                     delay_period_distribution=ExponentialDistribution(mean=delay_period),
                                     broadcast_delay_complete_event=diagnostic_trigger,
                                     common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                 new_property_value=hct_testing_loop_pv))
        add_intervention_triggered(campaign, intervention_list=[delay_to_next_hct],
                                   triggers_list=[initial_trigger], start_year=start_year,
                                   node_ids=delay_node_ids,
                                   event_name=f'HCTTestingLoop: state 0 (delay to next HCT): {node_name}')

    # testing loop -- hct hiv test
    randomchoice_trigger = CustomEvent.HCT_TESTING_LOOP_2
    yearandsexdiag_trigger = CustomEvent.ART_STAGING_9
    hiv_test = HIVRapidHIVDiagnostic(campaign,
                                     positive_diagnosis_event=yearandsexdiag_trigger,
                                     negative_diagnosis_event=randomchoice_trigger,
                                     base_sensitivity=1,
                                     common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                 new_property_value=hct_testing_loop_pv))
    add_intervention_triggered(campaign, intervention_list=[hiv_test],
                               triggers_list=[diagnostic_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='HCTTestingLoop: state 1 (HIV rapid diagnostic)')

    # testing loop -- hct retention -- stay in loop or dropout
    choices = {initial_trigger: hct_retention_rate, HCT_UPTAKE_POST_DEBUT_TRIGGER_1: round(1 - hct_retention_rate, 7)} # to get rid of floating point decimal issues
    retention_decision = HIVRandomChoice(campaign,
                                         choice_names=list(choices.keys()),
                                         choice_probabilities=list(choices.values()),
                                         common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                     new_property_value=hct_testing_loop_pv))
    add_intervention_triggered(campaign, intervention_list=[retention_decision],
                               triggers_list=[randomchoice_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='HCTTestingLoop: state 2 (HCT Testing retention/dropout)')

    # Consider immediate ART in HCT loop, no further testing for eligibility or potential waiting. Or go to ART staging.
    consider_immediate_ART = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                                positive_diagnosis_event=ON_ART_TRIGGER_2,
                                                                negative_diagnosis_event=ART_STAGING_TRIGGER_1,
                                                                time_value_map=ValueMap(times=list(tvmap_consider_immediate_ART.keys()),
                                                                                        values=list(tvmap_consider_immediate_ART.values())),
                                                                common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                            new_property_value=hct_testing_loop_pv))

    add_intervention_triggered(campaign, intervention_list=[consider_immediate_ART],
                               triggers_list=[yearandsexdiag_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='Consider immediate ART (after 2016?)')

    return (HCT_UPTAKE_POST_DEBUT_TRIGGER_1,  # return the trigger for the HCTUptakePostDebut state
            ON_ART_TRIGGER_2,  # return the trigger for the OnART state
            ART_STAGING_TRIGGER_1)  # return the trigger for the ARTStaging state


def add_state_TestingOnSymptomatic(campaign: emod_api.campaign,
                                   node_ids: Union[List[int], None],
                                   disqualifying_properties: List[str],
                                   start_year: float,
                                   tvmap_increased_symptomatic_presentation: dict = all_negative_time_value_map) -> (
        Tuple[str, str]):
    """
    This function manages the addition of Testing on Symptomatic individuals in the campaign.

    This state is triggered when an individual becomes 'NewlySymptomatic'. A HIVSigmoidByYearAndSexDiagnostic
    intervention is then applied.
    If the test result is positive, it triggers the ARTStagingDiagnosticTest state using the
    ART_STAGING_DIAGNOSTIC_TEST_TRIGGER event.
    If the test is negative, it triggers a HIVPiecewiseByYearAndSexDiagnostic test. If the result of this test is
    positive, it initiates the ARTStaging state through the ART_STAGING_TRIGGER_2 event. If the test result is negative,
    it does not trigger any further events.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        start_year (float): The start year for the state.
        tvmap_increased_symptomatic_presentation (dict, optional): Time value map for increased symptomatic presentation
            which is used in the HIVPiecewiseByYearAndSexDiagnostic intervention. Defaults to
            all_negative_time_value_map which will always trigger the Negative event('None').

    Returns:
        Tuple[str, str]: The triggers for the ARTStagingDiagnosticTest and ARTStaging states.
    """
    """
    When the 'NewlySymptomatic' event occurs, this state is initiated. The sigmoiddiag intervention is then applied. If
    the test result is positive, it triggers the ARTStagingDiagnosticTest state via the
    ART_STAGING_DIAGNOSTIC_TEST_TRIGGER event. However, if the sigmoiddiag test is negative, it triggers a
    yearandsexdiag test and if the result is positive, it initiates the ARTStaging state through the ART_STAGING_TRIGGER_2 event.
    """
    # presentation of symptoms leading to HIV testing
    testing_on_symptomatic_pv = CascadeState.TESTING_ON_SYMPTOMATIC
    initial_trigger = NEWLY_SYMPTOMATIC
    yearandsexdiag_trigger = CustomEvent.ART_STAGING_8
    probability_of_symptoms = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                               positive_diagnosis_event=ART_STAGING_DIAGNOSTIC_TEST_TRIGGER,
                                                               negative_diagnosis_event=yearandsexdiag_trigger,
                                                               year_sigmoid=Sigmoid(min=0.25,
                                                                                    max=0.9,
                                                                                    mid=2002,
                                                                                    rate=0.5),
                                                               common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                           new_property_value=testing_on_symptomatic_pv))
    add_intervention_triggered(campaign, intervention_list=[probability_of_symptoms],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='TestingOnSymptomatic: state 0 (Presentation probability)')

    # Consider increased symptomatic presentation at some point
    #  Note: the following yearandsexdiag has 0 values in TVMap in Zambia model, which means the 'ARTStaging8'
    #  that triggers this test which will always return negative. Right now the Negative_event is 'None', which means
    #  it goes nowhere.
    increased_symptomatic_presentation = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                                            positive_diagnosis_event=ART_STAGING_TRIGGER_2,
                                                                            negative_diagnosis_event=None,
                                                                            time_value_map=ValueMap(times=list(tvmap_increased_symptomatic_presentation.keys()),
                                                                                                    values=list(tvmap_increased_symptomatic_presentation.values())),
                                                                            common_intervention_parameters=CommonInterventionParameters(disqualifying_properties=disqualifying_properties,
                                                                                                                                        new_property_value=testing_on_symptomatic_pv))
    add_intervention_triggered(campaign, intervention_list=[increased_symptomatic_presentation],
                               triggers_list=[yearandsexdiag_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='Consider increased symptomatic presentation (after 2016?)')
    return (ART_STAGING_DIAGNOSTIC_TEST_TRIGGER,  # return the trigger for the ARTStagingDiagnosticTest state
            ART_STAGING_TRIGGER_2)  # return the trigger for the ARTStaging state


def add_state_ARTStagingDiagnosticTest(campaign,
                                       node_ids: Union[List[int], None],
                                       disqualifying_properties: List[str],
                                       start_year: float) -> str:
    """
    This function manages the addition of ART Staging Diagnostic Test in the campaign.

    This state is triggered by the ART_STAGING_DIAGNOSTIC_TEST_TRIGGER event. Upon activation, it conducts an HIV
    rapid diagnostic test on individuals who present with symptoms. If the test result is positive, it triggers the
    transition to the ARTStaging state using the ART_STAGING_TRIGGER_1 event.

    Args:
        campaign: The campaign to which the state is added.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        start_year (float): The start year for the state.

    Returns:
        str: The trigger for the ARTStaging state.
    """
    # HIV testing of those who present with symptoms
    art_staging_diagnostic_test_pv = CascadeState.ART_STAGING_DIAGNOSTIC_TEST

    initial_trigger = ART_STAGING_DIAGNOSTIC_TEST_TRIGGER
    
    hiv_test = HIVRapidHIVDiagnostic(campaign,
                                     positive_diagnosis_event=ART_STAGING_TRIGGER_1,
                                     negative_diagnosis_event=None,
                                     base_sensitivity=1,
                                     common_intervention_parameters=CommonInterventionParameters(
                                         disqualifying_properties=disqualifying_properties,
                                         new_property_value=art_staging_diagnostic_test_pv))
    add_intervention_triggered(campaign, intervention_list=[hiv_test],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ART Staging: state 0 (HIV rapid diagnostic)')
    return ART_STAGING_TRIGGER_1  # return the trigger for the ARTStaging state


def add_state_ARTStaging(campaign: emod_api.campaign,
                         cd4_retention_rate: float,
                         pre_staging_retention: float,
                         node_ids: Union[List[int], None],
                         disqualifying_properties: List[str],
                         start_year: float):
    """
    This function manages the addition of the ART Staging state in the campaign.

    This state is initially triggered by the ART_STAGING_TRIGGER_1 and ART_STAGING_TRIGGER_2 events. Upon activation,
    it conducts a series of interventions and diagnostics, including blood draw, ART eligibility check, and CD4 count
    check. Depending on the results of these checks, the function can trigger transitions to several different states.

    Args:
        campaign (emod_api.campaign): The campaign to which the state is added.
        cd4_retention_rate (float): The retention rate for CD4.
        pre_staging_retention (float): The retention rate before staging.
        node_ids (Union[List[int], None]): A list of node IDs where the state is to be applied. If None, the state is
            applied to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from the state.
        start_year (float): The start year for the state.

    Returns:
        Tuple[str, str, str, str]: The triggers for the LinkingToART, LinkingToPreART, HCTUptakePostDebut states for
        individuals who are not eligible for ART from the randomchoice, and HCTUptakePostDebut state for individuals
        who are lost to follow-up (LTFU).
    """
    art_staging_pv = CascadeState.ART_STAGING

    initial_trigger = ART_STAGING_TRIGGER_1  # 'ARTStaging1'
    hivmuxer_trigger = ART_STAGING_TRIGGER_2  # 'ARTStaging2'

    # these events are used within this function, but not returned
    drawblood_trigger    = CustomEvent.ART_STAGING_3 # noqa: E221
    cd4diag_trigger      = CustomEvent.ART_STAGING_4 # noqa: E221
    randomchoice_trigger = CustomEvent.ART_STAGING_5
    cd4_retention_choice = CustomEvent.ART_STAGING_6

    # chance to return for blood draw
    choices = {hivmuxer_trigger: pre_staging_retention,
               HCT_UPTAKE_POST_DEBUT_TRIGGER_2: round(1 - pre_staging_retention, 7)}  # hct_update_post_debut_choice # to get rid of floating point decimal issues
    prestaging_retention = HIVRandomChoice(campaign,
                                           choice_names=list(choices.keys()),
                                           choice_probabilities=list(choices.values()),
                                           common_intervention_parameters=CommonInterventionParameters(
                                               disqualifying_properties=disqualifying_properties,
                                               new_property_value=art_staging_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[prestaging_retention],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 1 (random choice: linking from positive diagnostic test)')
    # ensuring each agent continues testing in this cascade once per timestep
    muxer = HIVMuxer(campaign,
                     muxer_name='ARTStaging',
                     delay_period_distribution=ConstantDistribution(value=1),
                     broadcast_delay_complete_event=drawblood_trigger,
                     common_intervention_parameters=CommonInterventionParameters(
                         disqualifying_properties=disqualifying_properties,
                         new_property_value=art_staging_pv))
    add_intervention_triggered(campaign, intervention_list=[muxer],
                               triggers_list=[hivmuxer_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 2 (Muxer to make sure only one entry per DT)')
    # perform blood draw
    draw_blood = HIVDrawBlood(campaign,
                              positive_diagnosis_event=cd4diag_trigger,
                              common_intervention_parameters=CommonInterventionParameters(
                                  disqualifying_properties=disqualifying_properties,
                                  new_property_value=art_staging_pv))
    add_intervention_triggered(campaign, intervention_list=[draw_blood],
                               triggers_list=[drawblood_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 3 (draw blood)')
    # TODO from Clark: move this into an input data file and read?
    # CD4 agnostic ART eligibility check
    adult_by_pregnant = ValueMap(times=[2002, 2013.95], values=[0, 1])
    adult_by_TB = ValueMap(times=[2002], values=[1])
    adult_by_WHO_stage = ValueMap(times=[2002, 2007.45, 2016], values=[4, 3, 0])
    child_treat_under_age_in_years_threshold = ValueMap(times=[2002, 2013.95], values=[5, 15])
    child_by_TB = ValueMap(times=[2002, 2010.5], values=[0, 1])
    child_by_WHO_stage = ValueMap(times=[2002, 2007.45, 2016], values=[4, 3, 0])
    art_eligibility = HIVARTStagingCD4AgnosticDiagnostic(campaign,
                                                         positive_diagnosis_event=LINKING_TO_ART_TRIGGER,
                                                         negative_diagnosis_event=randomchoice_trigger,
                                                         adult_by_pregnant=adult_by_pregnant,
                                                         adult_by_tb=adult_by_TB,
                                                         adult_by_who_stage=adult_by_WHO_stage,
                                                         child_treat_under_age_in_years_threshold=child_treat_under_age_in_years_threshold,
                                                         child_by_tb=child_by_TB,
                                                         child_by_who_stage=child_by_WHO_stage,
                                                         common_intervention_parameters=CommonInterventionParameters(
                                                             disqualifying_properties=disqualifying_properties,
                                                             new_property_value=art_staging_pv))
    add_intervention_triggered(campaign, intervention_list=[art_eligibility],
                               triggers_list=[cd4diag_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 4 (check eligibility for ART, CD4 agnostic)')
    # if NOT eligible for ART without checking CD4, decide to return for CD4 test or lost-to-followup (LTFU)
    choices = {cd4_retention_choice: cd4_retention_rate,
               HCT_UPTAKE_POST_DEBUT_TRIGGER_3: round(1 - cd4_retention_rate, 7)}  # lost_to_followup (LTFU) # to get rid of floating point decimal issues
    cd4_retention = HIVRandomChoice(campaign,
                                    choice_names=list(choices.keys()),
                                    choice_probabilities=list(choices.values()),
                                    common_intervention_parameters=CommonInterventionParameters(
                                        disqualifying_properties=disqualifying_properties,
                                        new_property_value=art_staging_pv))
    add_intervention_triggered(campaign, intervention_list=[cd4_retention],
                               triggers_list=[randomchoice_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 5 (random choice: Return for CD4 or LTFU)')
    # determine if eligible for ART given CD4 counts
    # TODO from Clark: move this into an input data file and read?
    cd4_threshold = ValueMap(times=[2002, 2010.5, 2013.95], values=[200, 350, 500])
    pregnant_cd4_threshold = ValueMap(times=[2002, 2010.5, 2013.95], values=[200, 350, 2000])
    active_TB_cd4_threshold = ValueMap(times=[2002, 2010.5], values=[200, 2000])
    art_eligibility_by_cd4 = HIVARTStagingByCD4Diagnostic(campaign,
                                                          positive_diagnosis_event=LINKING_TO_ART_TRIGGER,
                                                          negative_diagnosis_event=LINKING_TO_PRE_ART_TRIGGER,
                                                          cd4_threshold=cd4_threshold,
                                                          if_pregnant=pregnant_cd4_threshold,
                                                          if_active_tb=active_TB_cd4_threshold,
                                                          common_intervention_parameters=CommonInterventionParameters(
                                                              disqualifying_properties=disqualifying_properties,
                                                              new_property_value=art_staging_pv))
    add_intervention_triggered(campaign, intervention_list=[art_eligibility_by_cd4],
                               triggers_list=[cd4_retention_choice],
                               node_ids=node_ids, start_year=start_year,
                               event_name='ARTStaging: state 6 (check eligibility for ART by CD4)')

    return (LINKING_TO_ART_TRIGGER,  # return the trigger for the LinkingToART state
            LINKING_TO_PRE_ART_TRIGGER,  # return the trigger for the LinkingToPreART state
            HCT_UPTAKE_POST_DEBUT_TRIGGER_2,  # return the trigger for the HCTUptakePostDebut state from peolpe who are not eligible for ART from the randomchoice
            HCT_UPTAKE_POST_DEBUT_TRIGGER_3)  # return the trigger for the HCTUptakePostDebut state from lost-to-followup (LTFU)


def add_state_LinkingToPreART(campaign: emod_api.campaign,
                              node_ids: Union[List[int], None],
                              disqualifying_properties: List[str],
                              start_year: float,
                              sigmoid_min: float = 0.7572242198,
                              sigmoid_max: float = 0.9591484679,
                              sigmoid_midyear: float = 2006.8336631523,
                              sigmoid_rate: float = 1.0) -> Tuple[str, str]:
    """
    This function manages the addition of the LinkingToPreART state in the campaign.

    The function is initially triggered by the LINKING_TO_PRE_ART_TRIGGER event. Upon activation, it conducts a
    HIVSigmoidByYearAndSexDiagnostic test. If the test result is positive, it triggers ON_PRE_ART_TRIGGER which will
    transition to the OnPreART state. If the test result is negative, it triggers HCT_UPTAKE_POST_DEBUT_TRIGGER_3 which
    will transition to the HCTUptakePostDebut state.

    Args:
        campaign (emod_api.campaign): The campaign object to which the state is added.
        node_ids (Union[List[int], None]): A list of node IDs for which the state is applicable. If None, the state is
            applicable to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from being in this
            state.
        start_year (float): The year on which the state starts.
        sigmoid_min (float): The left asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_max (float): The right asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_midyear (float): The time of the infection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_rate (float): The slope of the inflection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention. A Rate of 1 sets the slope to a 25% change in probability
            per year.

    Returns:
        Tuple[str, str]: The triggers for the OnPreART and HCTUptakePostDebut states.

    """
    linking_to_pre_art_pv = CascadeState.LINKING_TO_PRE_ART
    initial_trigger = LINKING_TO_PRE_ART_TRIGGER

    link_decision = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                     positive_diagnosis_event=ON_PRE_ART_TRIGGER,
                                                     negative_diagnosis_event=HCT_UPTAKE_POST_DEBUT_TRIGGER_3,
                                                     year_sigmoid=Sigmoid(min=sigmoid_min,
                                                                          max=sigmoid_max,
                                                                          mid=sigmoid_midyear,
                                                                          rate=sigmoid_rate),
                                                     female_multiplier=1.5,
                                                     common_intervention_parameters=CommonInterventionParameters(
                                                         disqualifying_properties=disqualifying_properties,
                                                         new_property_value=linking_to_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[link_decision],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='LinkingToPreART: state 0 (Linking probability)')
    return (ON_PRE_ART_TRIGGER,  # return the trigger for the OnPreART state
            HCT_UPTAKE_POST_DEBUT_TRIGGER_3)  # return the trigger for the HCTUptakePostDebut state from people who are not eligible for ART


def add_state_OnPreART(campaign: emod_api.campaign,
                       node_ids: Union[List[int], None],
                       pre_art_retention: float,
                       disqualifying_properties: List[str],
                       start_year: float) -> Tuple[str, str]:
    """
    This function manages the addition of the OnPreART state in the campaign.

    The function is initially triggered by the ON_PRE_ART_TRIGGER event. Upon activation, it conducts a series of
    interventions and diagnostics, including a HIVMuxer with a delay period, a random choice for pre-ART retention or
    lost to follow-up, a CD4 agnostic pre-ART eligibility check, a blood draw, and a determination of ART eligibility
    given CD4 counts. Depending on the results of these checks, the function can transit to two different states.
    It could trigger the OnART state if the individual is eligible for ART with ON_ART_TRIGGER_1 event. It could also
    trigger the HCTUptakePostDebut state if the individual is not retained in the pre-ART state with
    HCT_UPTAKE_POST_DEBUT_TRIGGER_3 event.

    Args:
        campaign (emod_api.campaign): The campaign object to which the state is added.
        node_ids (Union[List[int], None]): A list of node IDs for which the state is applicable. If None, the state is
            applicable to all nodes.
        pre_art_retention (float): The retention rate in the pre-ART state.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from being in this
            state.
        start_year (float): The float on which the state starts.

    Returns:
        Tuple[str, str]: The triggers for the OnART and HCTUptakePostDebut states.


    """
    on_pre_art_pv = CascadeState.ON_PRE_ART

    initial_trigger = ON_PRE_ART_TRIGGER

    # these events are used within this function, but not returned
    randomchoice_trigger         = CustomEvent.ON_PRE_ART_1 # noqa: E221
    art_staging_cd4_diag_trigger = CustomEvent.ON_PRE_ART_2
    drawblood_trigger            = CustomEvent.ON_PRE_ART_3 # noqa: E221
    drawblood_positive           = CustomEvent.ON_PRE_ART_4 # noqa: E221
    muxer = HIVMuxer(campaign,
                     muxer_name='PreART',
                     delay_period_distribution=ConstantDistribution(value=182),
                     broadcast_delay_complete_event=randomchoice_trigger,
                     common_intervention_parameters=CommonInterventionParameters(
                         disqualifying_properties=disqualifying_properties,
                         new_property_value=on_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[muxer],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='OnPreART: state 0 (muxer, 182-day delay)')
    # decision to continue to pre-ART or lost to followup (LTFU)
    choices = {art_staging_cd4_diag_trigger: pre_art_retention,
               HCT_UPTAKE_POST_DEBUT_TRIGGER_3: round(1 - pre_art_retention, 7)}  # to get rid of floating point decimal issues
    pre_ART_retention = HIVRandomChoice(campaign,
                                        choice_names=list(choices.keys()),
                                        choice_probabilities=list(choices.values()),
                                        common_intervention_parameters=CommonInterventionParameters(
                                            disqualifying_properties=disqualifying_properties,
                                            new_property_value=on_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[pre_ART_retention],
                               triggers_list=[randomchoice_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='OnPreART: state 1 (random choice: pre-ART or LTFU)')
    # TODO from Clark: move this into an input data file and read?
    # CD4 agnostic pre-ART eligibility check
    adult_by_pregnant = ValueMap(times=[2002, 2013.95], values=[0, 1])
    adult_by_TB = ValueMap(times=[2002], values=[1])
    adult_by_WHO_stage = ValueMap(times=[2002, 2007.45, 2016], values=[4, 3, 0])
    child_treat_under_age_in_years_threshold = ValueMap(times=[2002, 2013.95], values=[5, 15])
    child_by_TB = ValueMap(times=[2002, 2010.5], values=[0, 1])
    child_by_WHO_stage = ValueMap(times=[2002, 2007.45, 2016], values=[4, 3, 0])
    pre_art_eligibility = HIVARTStagingCD4AgnosticDiagnostic(campaign,
                                                             positive_diagnosis_event=ON_ART_TRIGGER_1,
                                                             negative_diagnosis_event=drawblood_trigger,
                                                             adult_by_pregnant=adult_by_pregnant,
                                                             adult_by_tb=adult_by_TB,
                                                             adult_by_who_stage=adult_by_WHO_stage,
                                                             child_treat_under_age_in_years_threshold=child_treat_under_age_in_years_threshold,
                                                             child_by_tb=child_by_TB,
                                                             child_by_who_stage=child_by_WHO_stage,
                                                             common_intervention_parameters=CommonInterventionParameters(
                                                                 disqualifying_properties=disqualifying_properties,
                                                                 new_property_value=on_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[pre_art_eligibility],
                               triggers_list=[art_staging_cd4_diag_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='OnPreART: state 2 (check eligibility for ART, CD4 agnostic)')
    # perform blood draw, pre-ART
    draw_blood = HIVDrawBlood(campaign,
                              positive_diagnosis_event=drawblood_positive,
                              common_intervention_parameters=CommonInterventionParameters(
                                  disqualifying_properties=disqualifying_properties,
                                  new_property_value=on_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[draw_blood],
                               triggers_list=[drawblood_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='OnPreART: state 3 (draw blood)')
    # TODO from Clark: note that the ART and pre-ART cascades have a different order for retention, is this right?? Explore/verify then ask.
    # determine if eligible for ART given CD4 counts
    # TODO from Clark: move this into an input data file and read?
    cd4_threshold = ValueMap(times=[2002, 2010.5, 2013.95], values=[200, 350, 500])
    pregnant_cd4_threshold = ValueMap(times=[2002, 2010.5, 2013.95], values=[200, 350, 2000])
    active_TB_cd4_threshold = ValueMap(times=[2002, 2010.5], values=[200, 2000])
    art_eligibility_by_cd4 = HIVARTStagingByCD4Diagnostic(campaign,
                                                          positive_diagnosis_event=ON_ART_TRIGGER_1,
                                                          negative_diagnosis_event=initial_trigger,
                                                          cd4_threshold=cd4_threshold,
                                                          if_pregnant=pregnant_cd4_threshold,
                                                          if_active_tb=active_TB_cd4_threshold,
                                                          common_intervention_parameters=CommonInterventionParameters(
                                                              disqualifying_properties=disqualifying_properties,
                                                              new_property_value=on_pre_art_pv))
    add_intervention_triggered(campaign, intervention_list=[art_eligibility_by_cd4],
                               triggers_list=[drawblood_positive],
                               node_ids=node_ids, start_year=start_year,
                               event_name='OnPreART: state 4 (check eligibility for ART by CD4)')

    return (ON_ART_TRIGGER_1,  # return the trigger for the OnART state
            HCT_UPTAKE_POST_DEBUT_TRIGGER_3)  # return the trigger for the HCTUptakePostDebut state


def add_state_LinkingToART(campaign: emod_api.campaign,
                           node_ids: Union[List[int], None],
                           disqualifying_properties: List[str],
                           start_year: float,
                           sigmoid_min: float = 0.0,
                           sigmoid_max: float = 0.8507390283,
                           sigmoid_midyear: float = 1997.4462231708,
                           sigmoid_rate: float = 1.0
                           ):
    """
    This function manages the addition of the LinkingToART state in the campaign.

    The function is initially triggered by the LINKING_TO_ART_TRIGGER event. Upon activation, it conducts a sigmoid
    HIVSigmoidByYearAndSexDiagnostic test. Depending on the result of this test, the function can transit to two
    different states. It could trigger the OnART state if the sigmoid diagnostic test result is positive with
    ON_ART_TRIGGER_1 event. It could also trigger the HCTUptakePostDebut state if the sigmoid diagnostic test result is
    negative with HCT_UPTAKE_POST_DEBUT_TRIGGER_2 event.

    Args:
        campaign (emod_api.campaign): The campaign object to which the state is added.
        node_ids (Union[List[int], None]): A list of node IDs for which the state is applicable. If None, the state is
            applicable to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from being in this
            state.
        start_year (float): The year on which the state starts.
        sigmoid_min (float): The left asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_max (float): The right asymptote for the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_midyear (float): The time of the infection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention.
        sigmoid_rate (float): The slope of the inflection point in the sigmoid trend over time for the
            HIVSigmoidByYearAndSexDiagnostic intervention. A Rate of 1 sets the slope to a 25% change in probability
            per year.

    Returns:
        Tuple[str, str]: The triggers for the OnART and 'HCTUptakePostDebut' states.
    """
    linking_to_art_pv = CascadeState.LINKING_TO_ART

    initial_trigger = LINKING_TO_ART_TRIGGER

    # ART linking probability by time
    art_linking_probability = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                               positive_diagnosis_event=ON_ART_TRIGGER_1,
                                                               negative_diagnosis_event=HCT_UPTAKE_POST_DEBUT_TRIGGER_2,
                                                               year_sigmoid=Sigmoid(min=sigmoid_min,
                                                                                    max=sigmoid_max,
                                                                                    mid=sigmoid_midyear,
                                                                                    rate=sigmoid_rate),
                                                               common_intervention_parameters=CommonInterventionParameters(
                                                                   disqualifying_properties=disqualifying_properties,
                                                                   new_property_value=linking_to_art_pv))
    add_intervention_triggered(campaign, intervention_list=[art_linking_probability],
                               triggers_list=[initial_trigger],
                               node_ids=node_ids, start_year=start_year,
                               event_name='LinkingToART: state 0 (Linking probability)')
    return (ON_ART_TRIGGER_1,  # return the trigger for the OnART state
            HCT_UPTAKE_POST_DEBUT_TRIGGER_2)  # return the trigger for the HCTUptakePostDebut state


def add_state_OnART(campaign: emod_api.campaign,
                    art_reenrollment_willingness: float,
                    immediate_art_rate: float,
                    node_ids: Union[List[int], None],
                    disqualifying_properties: List[str],
                    start_year: float,
                    tvmap_immediate_ART_restart: dict = all_negative_time_value_map,
                    tvmap_reconsider_lost_forever: dict = all_negative_time_value_map):
    """
    This function manages the addition of the OnART state in the campaign.

    The function is initially triggered by the ON_ART_TRIGGER_1 and ON_ART_TRIGGER_2 events. Upon activation, it
    conducts a series of interventions and diagnostics, including a decision(with HIVRandomChoice) on whether to initiate
    ART immediately or delay(with HIVMuxer), initiation of ART, a delay(with HIVMuxer) to dropping off of ART, and a
    decision(with HIVRandomChoice) on willingness to test the eligibility of re-enroll in ART or transit to other states.

    Args:
        campaign (emod_api.campaign): The campaign object to which the state is added.
        art_reenrollment_willingness (float): The willingness of an individual to re-enroll in ART after dropout.
        immediate_art_rate (float): The rate at which ART is initiated immediately, without HIVMuxer delay.
        node_ids (Union[List[int], None]): A list of node IDs for which the state is applicable. If None, the state is
            applicable to all nodes.
        disqualifying_properties (List[str]): A list of properties that disqualify an individual from being in this
            state.
        start_year (float): The year on which the state starts.
        tvmap_immediate_ART_restart (dict): A time value map for HIVPiecewiseByYearAndSexDiagnostic intervention to
            consider restarting ART immediately after HIVMuxer delay. Defaults to all_negative_time_value_map which will
            always trigger the Negative event(HCT_UPTAKE_POST_DEBUT_TRIGGER_2) and transit to HCTUptakePostDebut state.
        tvmap_reconsider_lost_forever (dict): A time value map for the second HIVPiecewiseByYearAndSexDiagnostic
            intervention to reconsider being lost forever to ART care. Defaults to all_negative_time_value_map which
            will always trigger the Negative event(LostForever) and transit to LostForever state.

    Returns:
        Tuple[str, str]: The triggers for the HCTUptakePostDebut and LostForever states.
    """
    on_art_pv = CascadeState.ON_ART

    initial_trigger_randomchoice = ON_ART_TRIGGER_1
    initial_trigger_ART_hivmuxer = ON_ART_TRIGGER_2
    on_art_3_event = 'OnART3'
    art_initiation_delay_event = 'ARTInitiationDelayed'
    choices = {initial_trigger_ART_hivmuxer: immediate_art_rate,
               art_initiation_delay_event: round(1 - immediate_art_rate, 7)}  # to get rid of floating point decimal issues
    when_decision = HIVRandomChoice(campaign,
                                    choice_names=list(choices.keys()),
                                    choice_probabilities=list(choices.values()),
                                    common_intervention_parameters=CommonInterventionParameters(
                                        disqualifying_properties=disqualifying_properties,
                                        new_property_value=on_art_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[when_decision],
                               triggers_list=[initial_trigger_randomchoice],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Delay to ART initiation: decide whether to initiate immediately or delay')

    # delay to ART initiation plus muxer to ensure agents only do it once at a time
    # Up-to 1-year delay before an agent makes further decisions on making further hct uptake decisions
    delay_to_art_initiation = HIVMuxer(campaign,
                                       muxer_name='OnART',
                                       delay_period_distribution=WeibullDistribution(weibull_lambda=63.381, weibull_kappa=0.711),
                                       broadcast_delay_complete_event=initial_trigger_ART_hivmuxer,
                                       common_intervention_parameters=CommonInterventionParameters(
                                           disqualifying_properties=disqualifying_properties,
                                           new_property_value=on_art_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[delay_to_art_initiation],
                               triggers_list=[art_initiation_delay_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='OnART: state 0 (muxer and delay)')

    # initiate ART
    initiate_art = AntiretroviralTherapy(campaign)
    add_intervention_triggered(campaign,
                               intervention_list=[initiate_art],
                               triggers_list=[initial_trigger_ART_hivmuxer],
                               node_ids=node_ids,
                               start_year=start_year,
                               event_name='Initiate ART'
                               )

    # delay to dropping off of ART + muxer to ensure drop-off once per agent/timestep
    art_dropout_delay = HIVMuxer(campaign,
                                 muxer_name='ARTDropoutDelay',
                                 delay_period_distribution=ExponentialDistribution(mean=7300),
                                 broadcast_delay_complete_event=on_art_3_event,
                                 common_intervention_parameters=CommonInterventionParameters(
                                     disqualifying_properties=disqualifying_properties,
                                     new_property_value=on_art_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[art_dropout_delay],
                               triggers_list=[initial_trigger_ART_hivmuxer],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='OnART: state 2 (delay to dropout)')

    # discontinue ART; dropout
    # QUESTION: do we need to change their CascadeState now that they're off ART?
    discontinue_ART = ARTDropout(campaign)
    add_intervention_triggered(campaign,
                               intervention_list=[discontinue_ART],
                               triggers_list=[on_art_3_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='OnART: state 3 (run ARTDropout)')

    # Willingness to re-enroll in ART after dropout
    ART_restart_test_choice = CustomEvent.HCT_UPTAKE_POST_DEBUT_8
    lostfoever_test_choice = CustomEvent.LOST_FOREVER_9
    choices = {ART_restart_test_choice: art_reenrollment_willingness,
               lostfoever_test_choice: round(1 - art_reenrollment_willingness, 7)}  # to get rid of floating point decimal issues
    willing_to_reenroll = HIVRandomChoice(campaign,
                                          choice_names=list(choices.keys()),
                                          choice_probabilities=list(choices.values()),
                                          common_intervention_parameters=CommonInterventionParameters(
                                              disqualifying_properties=disqualifying_properties,
                                              new_property_value=on_art_pv))
    add_intervention_triggered(campaign,
                               intervention_list=[willing_to_reenroll],
                               triggers_list=[on_art_3_event],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='OnART: state 4 (Willing to re-enroll in ART?)')

    # Note: the following 2 yearandsexdiag interventions have TVMap set to all negative values, which will always
    # trigger the Negative events and transit to HCTUptakePostDebut and LostForever states.

    # Consider restarting ART immediately after dropping off ART
    immediate_ART_restart = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                               time_value_map=ValueMap(
                                                                   times=list(tvmap_immediate_ART_restart.keys()),
                                                                   values=list(tvmap_immediate_ART_restart.values())),
                                                               positive_diagnosis_event=initial_trigger_ART_hivmuxer,
                                                               negative_diagnosis_event=HCT_UPTAKE_POST_DEBUT_TRIGGER_2,
                                                               common_intervention_parameters=CommonInterventionParameters(
                                                                   disqualifying_properties=['CascadeState:LostForever'],
                                                                   new_property_value='CascadeState:OnART'))
    add_intervention_triggered(campaign,
                               intervention_list=[immediate_ART_restart],
                               triggers_list=[ART_restart_test_choice],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Consider not dropping (after 2016?)')

    # reconsider being lost forever to ART care
    reconsider_lost_forever = HIVPiecewiseByYearAndSexDiagnostic(campaign,
                                                                 time_value_map=ValueMap(
                                                                     times=list(tvmap_reconsider_lost_forever.keys()),
                                                                     values=list(tvmap_reconsider_lost_forever.values())),
                                                                 positive_diagnosis_event=initial_trigger_ART_hivmuxer,
                                                                 negative_diagnosis_event=LOST_FOREVER_TRIGGER,
                                                                 common_intervention_parameters=CommonInterventionParameters(
                                                                     disqualifying_properties=['CascadeState:LostForever'],
                                                                     new_property_value='CascadeState:OnART'))
    add_intervention_triggered(campaign,
                               intervention_list=[reconsider_lost_forever],
                               triggers_list=[lostfoever_test_choice],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='Consider not lost forever (after 2016?)')
    return (HCT_UPTAKE_POST_DEBUT_TRIGGER_2,  # return the trigger for the HCTUptakePostDebut state
            LOST_FOREVER_TRIGGER)             # return the trigger for the LostForever state


def add_state_LostForever(campaign: emod_api.campaign, node_ids: Union[List[int], None], start_year: float):
    """
    Transition individuals to the 'LostForever' state in the campaign.

    This function is triggered by the LOST_FOREVER_TRIGGER event. Upon activation, it changes the target property
    key to 'CascadeState' and the target property value to 'LostForever', effectively moving individuals to the
    LostForever state in the campaign.

    Args:
        campaign (emod_api.campaign): The campaign object to which the state transition is to be added.
        node_ids (List[int]): A list of node IDs where this transition is applicable.
        start_year (float): The starting year of the campaign when this transition becomes active.

    """
    # Actually lost forever now
    initial_trigger = LOST_FOREVER_TRIGGER
    lost_forever = PropertyValueChanger(campaign,
                                        target_property_key=CascadeState.LOST_FOREVER.split(':')[0],  # 'CascadeState'
                                        target_property_value=CascadeState.LOST_FOREVER.split(':')[1],  # 'LostForever'
                                        )
    add_intervention_triggered(campaign,
                               intervention_list=[lost_forever],
                               triggers_list=[initial_trigger],
                               start_year=start_year,
                               node_ids=node_ids,
                               event_name='LostForever: state 0')


# todo: making this function private for now, as it is not yet implemented
def _add_rtri_testing(campaign: emod_api.campaign,
                      rtri_node_ids: List[int] = None,
                      rtri_start_year: float = 2015,
                      rtri_testing_min_age: float = 15,
                      rtri_followup_rate: float = 1,
                      rtri_consent_rate: float = 1,
                      rtri_retesting_rate: float = 0.01):  # TODO: find a good starting value or just calibrate.
    raise NotImplementedError("This function is not yet implemented.")

    # Chance to follow-up a HIV+ result with an offer of a recency test
    # TODO: set these HIV+ test result triggers properly, they are ... confusing ... and some refactoring of their use may be needed
    # triggers = ['retester_is_HIV+', 'HIV_Positive_at_ANC', 'ARTStaging9', 'ARTStaging1'] # TODO: update project json to have correct triggers, too (including the sending of the triggers, not just consumption). Verify/ask about all these triggers and e.g. double counting of blood draws for some.
    choices = {'RTRI_BEGIN_FOLLOWUP': rtri_followup_rate, 'RTRI_LOST_TO_FOLLOWUP': 1 - rtri_followup_rate}
    rtri_followup = HIVRandomChoice(campaign,
                                    choice_names=list(choices.keys()),
                                    choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_followup],
                               triggers_list=['ARTStaging9'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Received HIV+ test result. Followed up with an RTRI?')

    # Determine if the person being offered a recency test is eligible (as known by person offering the test)
    rtri_eligible = BroadcastEvent(campaign, broadcast_event='RTRI_ELIGIBLE')
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_eligible],
                               triggers_list=['RTRI_BEGIN_FOLLOWUP'],
                               target_demographics_config=TargetDemographicsConfig(target_age_min=rtri_testing_min_age),
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Broadcast RTRI eligibility (eligible)')

    # Determine if the person being offered a recency test is NOT eligible (as known by person offering the test)
    rtri_ineligible = BroadcastEvent(campaign, broadcast_event='RTRI_INELIGIBLE')
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_ineligible],
                               triggers_list=['RTRI_BEGIN_FOLLOWUP'],
                               target_demographics_config=TargetDemographicsConfig(target_age_max=rtri_testing_min_age - EPSILON),
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Broadcast RTRI eligibility (NOT eligible)')

    # Chance to follow-up a HIV+ result with an offer of a recency test
    choices = {'RTRI_CONSENTED': rtri_consent_rate, 'RTRI_REFUSED': 1 - rtri_consent_rate}
    rtri_consent = HIVRandomChoice(campaign,
                                   choice_names=list(choices.keys()),
                                   choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_consent],
                               triggers_list=['RTRI_ELIGIBLE'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Check if person consents to an RTRI')

    # Statistics of RTRI testing depends on whether an agent has been (truly) infected recently AND their ART history
    # Each agent tested qualifies for only one of four mutually exclusive test variations:
    # recently_infected AND has_been_on_ART
    # recently_infected AND NOT has_been_on_ART
    # NOT recently_infected AND has_been_on_ART
    # NOT recently_infected AND NOT has been_on_ART
    # We do not consider any case where an HIV- person is tested.

    target_hiv_positive = IsHIVPositive()
    # RTRI test (1/4): recently_infected AND has_been_on_ART
    # TODO: set these probabilities properly
    choices = {'RTRI_TESTED_RECENT': 0.85, 'RTRI_TESTED_LONGTERM': 0.15}
    rtri_result = HIVRandomChoice(campaign,
                                  choice_names=list(choices.keys()),
                                  choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_result],
                               triggers_list=['RTRI_CONSENTED'],
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[
                                   ["Recently_Infected:true", "Ever_Been_On_ART:true"]]),
                               targeting_config=target_hiv_positive,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Perform RTRI test (HIV+, recent, previous ART usage)')

    # RTRI test (2/4): recently_infected AND NOT has_been_on_ART
    # TODO: set these probabilities properly
    choices = {'RTRI_TESTED_RECENT': 0.8, 'RTRI_TESTED_LONGTERM': 0.2}
    rtri_result = HIVRandomChoice(campaign,
                                  choice_names=list(choices.keys()),
                                  choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_result],
                               triggers_list=['RTRI_CONSENTED'],
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[
                                   ["Recently_Infected:true", "Ever_Been_On_ART:false"]]),
                               targeting_config=target_hiv_positive,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Perform RTRI test (HIV+, recent, NO previous ART usage)')

    # RTRI test (3/4): NOT recently_infected AND has_been_on_ART
    # TODO: set these probabilities properly
    choices = {'RTRI_TESTED_RECENT': 0.75, 'RTRI_TESTED_LONGTERM': 0.25}
    rtri_result = HIVRandomChoice(campaign,
                                  choice_names=list(choices.keys()),
                                  choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_result],
                               triggers_list=['RTRI_CONSENTED'],
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[
                                   ["Recently_Infected:false", "Ever_Been_On_ART:true"]]),
                               targeting_config=target_hiv_positive,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Perform RTRI test (HIV+, longterm, previous ART usage)')

    # RTRI test (4/4): NOT recently_infected AND NOT has been_on_ART
    # TODO: set these probabilities properly
    choices = {'RTRI_TESTED_RECENT': 0.7, 'RTRI_TESTED_LONGTERM': 0.3}
    rtri_result = HIVRandomChoice(campaign,
                                  choice_names=list(choices.keys()),
                                  choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[rtri_result],
                               triggers_list=['RTRI_CONSENTED'],
                               property_restrictions=PropertyRestrictions(individual_property_restrictions=[
                                   ["Recently_Infected:false", "Ever_Been_On_ART:false"]]),
                               targeting_config=target_hiv_positive,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Perform RTRI test (HIV+, longterm, NO previous ART usage)')

    #
    # Individual property management for infection recency, ART history, and (approximate) viral suppression
    #

    # all infections start out as recent
    recency_update = PropertyValueChanger(campaign,
                                          target_property_key='Recently_Infected', target_property_value='true')
    add_intervention_triggered(campaign,
                               intervention_list=[recency_update],
                               triggers_list=['NewInfectionEvent'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Infections start out recent, transitioning to longterm after 12 months')

    # all people starting art are marked as having taking it at least once in their lives
    art_history_update = PropertyValueChanger(campaign,
                                              target_property_key='Ever_Been_On_ART', target_property_value='true')
    add_intervention_triggered(campaign,
                               intervention_list=[art_history_update],
                               triggers_list=['OnART1'],
                               property_restrictions=PropertyRestrictions(
                                   individual_property_restrictions=[['Ever_Been_On_ART:false']]),
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Record a person having been on ART at least once in their lives')

    # all newly infected agents start out as virally unsuppressed
    suppression_update = PropertyValueChanger(campaign,
                                              target_property_key='Virally_Suppressed', target_property_value='false')
    add_intervention_triggered(campaign,
                               intervention_list=[suppression_update],
                               triggers_list=['NewInfectionEvent'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Set viral suppression status to false upon infection (ignoring VL ramp-up time which is on the order of 1-2 months)')

    # agents who are on ART for 6 consecutive months are considered virally suppressed (a simplification)
    # TODO: usage of this needs implementing. When done, update format of this argument being passed
    target_on_ART_long_enough = IsOnART() & HasBeenOnArtMoreOrLessThanNumMonths(more_or_less=MoreOrLess.MORE, num_months=6)

    suppression_update = PropertyValueChanger(campaign,
                                              target_property_key='Virally_Suppressed', target_property_value='true')
    add_intervention_scheduled(campaign,
                               intervention_list=[suppression_update],
                               property_restrictions=PropertyRestrictions(
                                   individual_property_restrictions=[['Virally_Suppressed:false']]),
                               targeting_config=target_on_ART_long_enough,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Set viral suppression status to true after 6 consecutive months on ART')

    # set viral suppression to false upon ART dropout (a simplification)
    suppression_update = PropertyValueChanger(campaign,
                                              target_property_key='Virally_Suppressed', target_property_value='false')
    add_intervention_triggered(campaign,
                               intervention_list=[suppression_update],
                               triggers_list=['OnART3'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Set viral suppression status to false upon ART dropout (ignoring VL ramp-up time which is on the order of 1-2 months)')

    # TODO: transition the existing campaign json (in actual project) to use drawblood instead of broadcast to match.
    # perform viral load testing to follow-up RTRI recent results (to confirm recency) (simply check viral load IP)
    # confirming recent infection
    vl_confirmation = HIVDrawBlood(campaign, positive_diagnosis_event='REPORT_RECENT_INFECTION')
    add_intervention_triggered(campaign,
                               intervention_list=[vl_confirmation],
                               triggers_list=['RTRI_TESTED_RECENT'],
                               property_restrictions=PropertyRestrictions(
                                   individual_property_restrictions=[['Virally_Suppressed:false']]),
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Run VL test along with recent RTRI test result (reporting confirmed recent)')

    # TODO: broadcast_event_immediate OR drawblood for this and the above event. Choose.
    # perform viral load testing to follow-up RTRI recent results (to confirm recency) (simply check viral load IP)
    # reclassify as longterm infection
    vl_confirmation = BroadcastEvent(campaign, broadcast_event='REPORT_LONGTERM_INFECTION')
    add_intervention_triggered(campaign,
                               intervention_list=[vl_confirmation],
                               triggers_list=['RTRI_TESTED_RECENT'],
                               property_restrictions=PropertyRestrictions(
                                   individual_property_restrictions=[['Virally_Suppressed:true']]),
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Run VL test along with recent RTRI test result (reporting longterm)')

    # RTRI longterm results are never reclassified due to VL tests. We ignore RTRI test failure (RTRI-long, VL-unsuppressed).
    # simply report longterm infection
    vl_confirmation = BroadcastEvent(campaign, broadcast_event='REPORT_LONGTERM_INFECTION')
    add_intervention_triggered(campaign,
                               intervention_list=[vl_confirmation],
                               triggers_list=['RTRI_TESTED_LONGTERM'],
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='Run VL test along with longterm RTRI test result (reporting longterm)')

    # HIV/RTRI testing noise -- people don't always tell health care providers that they know they are HIV+, e.g., they
    # switch to a different health facility after moving and think they need a new HIV+ result to get a refill on their
    # ART medications. This event ensures there is a tunable fraction of the ART-history population HIV/RTRI testing
    # each timestep.
    # TODO: when should retesting start? probably before RTRI testing timeframe? Maybe once ART starts up?
      
    target_on_ART = IsHivPositive() & IsOnART()
    retest_signal = BroadcastEvent(campaign, broadcast_event='HCTTestingLoop1--retesters')
    add_intervention_scheduled(campaign,
                               intervention_list=[retest_signal],
                               targeting_config=target_on_ART,
                               node_ids=rtri_node_ids,
                               target_demographics_config=TargetDemographicsConfig(demographic_coverage=rtri_retesting_rate),
                               start_year=rtri_start_year,
                               event_name='Send people to test even if they are HIV+ and on ART. E.g., they might just be moving health facilities. Happens.',
                               repetition_config=RepetitionConfiguration(number_of_repetitions=-1,  # FOREVER
                                                                         timesteps_between_repetitions=1)  # every timestep
                               )

    # HIV test for retesters (looser property restrictions compared to regular health care testing)
    # we target on-ART people here (again) to ensure that individuals who JUST went off of ART (but after broadcasting
    # HCTTestingLoop1--retesters) do not test. They have to wait until the next timestep, if they wish to retest.
    # distributing PMTCT HIV diagnostic test
    # TODO, QUESTION: should 'retesters' be considered 'presenting as symptomatic'? Ensure json is synced.
    # e.g. how will the health system treat them once they test HIV+ (again)?
    retester_hiv_test = HIVRapidHIVDiagnostic(campaign,
                                              positive_diagnosis_event='retester_is_HIV+',
                                              negative_diagnosis_event=None,
                                              common_intervention_parameters=CommonInterventionParameters(
                                                  disqualifying_properties=['CascadeState:LostForever']))
    add_intervention_triggered(campaign,
                               intervention_list=[retester_hiv_test],
                               triggers_list=['HCTTestingLoop1--retesters'],
                               targeting_config=target_on_ART,
                               start_year=rtri_start_year,
                               node_ids=rtri_node_ids,
                               event_name='HCTTestingLoop: state 1 (HIV rapid diagnostic) -- HIV+/OnART retesters')


# todo: making this function private for now, as it is not yet implemented
def _add_index_testing(campaign: emod_api.campaign,
                       index_testing_triggers: List[str],
                       index_testing_node_ids: List[int] = None,
                       index_testing_start_year: float = 2015,
                       index_testing_partner_coverage: float = 0.5):  # TODO: definitely calibrate this!
    raise NotImplementedError("The index_testing_partner_coverage in this function is not yet implemented.")
    # TODO: add ALL of these campaign elements, when complete, to the original json version
    if index_testing_triggers is None:
        # QUESTION: are these right? Additionally, need to add retester_is_HIV+ in the campaign caller
        index_testing_triggers = ['HIV_Positive_at_ANC', 'ARTStaging9', 'ARTStaging1']

    # Is a HIV+ test followed up with index testing offer by the health system?
    # TODO: set these probabilities properly
    choices = {'INDEX_TESTING_BEGIN_FOLLOWUP': 0.95, 'INDEX_TESTING_LOST_TO_FOLLOWUP': 0.05}
    index_testing_followup = HIVRandomChoice(campaign,
                                             choice_names=list(choices.keys()),
                                             choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[index_testing_followup],
                               triggers_list=index_testing_triggers,
                               start_year=index_testing_start_year,
                               node_ids=index_testing_node_ids,
                               event_name='Follow-up newly diagnosed HIV+ individuals with index testing?')

    # Is the offer of index testing accepted?
    # TODO: set these probabilities properly
    choices = {'INDEX_TESTING_CONSENTED': 0.9, 'INDEX_TESTING_REFUSED': 0.1}
    index_testing_followup = HIVRandomChoice(campaign,
                                             choice_names=list(choices.keys()),
                                             choice_probabilities=list(choices.values()))
    add_intervention_triggered(campaign,
                               intervention_list=[index_testing_followup],
                               triggers_list=['INDEX_TESTING_BEGIN_FOLLOWUP'],
                               start_year=index_testing_start_year,
                               node_ids=index_testing_node_ids,
                               event_name='Is an offer of index testing accepted by an individual?')

    # Actual event targeting partners: % coverage (calibrated) of their partners (of N_Partners) selected
    #   -> signal them.
    # TODO - talk with Dan B about this partner targeting
    
    # todo:
    index_testing_elicit_contacts = BroadcastEvent(campaign,
                                                   broadcast_event='ELICITED_CONTACT')
    add_intervention_triggered(campaign,
                               intervention_list=[index_testing_elicit_contacts],
                               triggers_list=['INDEX_TESTING_CONSENTED'],
                               node_ids=index_testing_node_ids,
                               start_year=index_testing_start_year,
                               event_name='Elicit contacts from index cases',
                               target_demographics_config=TargetDemographicsConfig()
                               )

    # partners: send them to HIV testing. QUESTION: Where exactly to link up in the CoC?
    # QUESTION = need to know which HIV test to send them to... HCT, prenatal (ha), symptomatic presentation, ...
    
    index_testing_contact_to_testing = BroadcastEvent(campaign,
                                                      broadcast_event='TODO:HIV_test_which_one')
    add_intervention_triggered(campaign,
                               intervention_list=[index_testing_contact_to_testing],
                               triggers_list=['ELICITED_CONTACT'],
                               node_ids=index_testing_node_ids,
                               start_year=index_testing_start_year,
                               event_name='Sending elicited contacts/partners to testing'
                               )
