import unittest
from emodpy_hiv.campaign.individual_intervention import (
    HIVMuxer, HIVPiecewiseByYearAndSexDiagnostic, HIVRandomChoice, HIVRapidHIVDiagnostic,
    HIVSigmoidByYearAndSexDiagnostic, MaleCircumcision, ModifyStiCoInfectionStatus, PMTCT, STIIsPostDebut,
    ARTDropout, ARTMortalityTable, AntiretroviralTherapy, HIVARTStagingByCD4Diagnostic, HIVARTStagingCD4AgnosticDiagnostic, HIVDrawBlood,
    InterventionForCurrentPartners, IVCalendar, RangeThreshold, AgeDiagnostic, CD4Diagnostic, CoitalActRiskFactors,
    FemaleContraceptive, AntiretroviralTherapyFull, STIBarrier, SetSexualDebutAge, StartNewRelationship, Sigmoid
)
import emodpy_hiv.campaign.waning_config as wc

from emod_api import campaign as api_campaign
from emodpy_hiv.campaign.common import ValueMap, CommonInterventionParameters
from emodpy_hiv.utils.distributions import ExponentialDistribution, ConstantDistribution
from emodpy_hiv.utils.emod_enum import (DistributionType, SensitivityType, RelationshipType, PrioritizePartnersBy, 
                                        SettingType, CondomUsageParametersType
)

from copy import deepcopy
from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest


class TestIntervention(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = api_campaign
        cls.campaign.set_schema(manifest.schema_path)
        cls.CIP = CommonInterventionParameters(
            cost=2,
            disqualifying_properties=["Risk:High"],
            dont_allow_duplicates=True,
            intervention_name="TestIntervention",
            new_property_value="Risk:Low"
        )

    def assertCIP(self, intervention, cost=2, disqualifying_properties=["Risk:High"], dont_allow_duplicates=True,
                  intervention_name="TestIntervention", new_property_value="Risk:Low"):
        if cost is not None:
            self.assertEqual(intervention.Cost_To_Consumer, cost)
        if disqualifying_properties is not None:
            self.assertEqual(intervention.Disqualifying_Properties, disqualifying_properties)
        if dont_allow_duplicates is not None:
            self.assertEqual(intervention.Dont_Allow_Duplicates, dont_allow_duplicates)
        if intervention_name is not None:
            self.assertEqual(intervention.Intervention_Name, intervention_name)
        if new_property_value is not None:
            self.assertEqual(intervention.New_Property_Value, new_property_value)

    def test_AgeDiagnostic(self):
        age_threshold_list = []
        age_threshold_list.append(RangeThreshold(low=180,high=360,event_to_broadcast="GetMMR"))
        age_threshold_list.append(RangeThreshold(low=360,high=720,event_to_broadcast="GetPolio"))
        
        ad = AgeDiagnostic(self.campaign,
                           age_thresholds=age_threshold_list)
        
        self.assertEqual('AgeDiagnostic', ad._intervention['class'])
        self.assertEqual(2, len(ad._intervention.Age_Thresholds))
        self.assertEqual( 180, ad._intervention.Age_Thresholds[0].Low)
        self.assertEqual( 360, ad._intervention.Age_Thresholds[1].Low)
        self.assertEqual( 360, ad._intervention.Age_Thresholds[0].High)
        self.assertEqual( 720, ad._intervention.Age_Thresholds[1].High)
        self.assertEqual( "GetMMR",   ad._intervention.Age_Thresholds[0].Event)
        self.assertEqual( "GetPolio", ad._intervention.Age_Thresholds[1].Event)

    def test_CD4Diagnostic(self):
        cd4_threshold_list = []
        cd4_threshold_list.append(RangeThreshold(low=  0,high=200,event_to_broadcast="GetART"))
        cd4_threshold_list.append(RangeThreshold(low=200,high=300,event_to_broadcast="GetTested"))
        
        cd = CD4Diagnostic(self.campaign,
                           cd4_thresholds=cd4_threshold_list)
        
        self.assertEqual('CD4Diagnostic', cd._intervention['class'])
        self.assertEqual(2, len(cd._intervention.CD4_Thresholds))
        self.assertEqual(   0, cd._intervention.CD4_Thresholds[0].Low)
        self.assertEqual( 200, cd._intervention.CD4_Thresholds[1].Low)
        self.assertEqual( 200, cd._intervention.CD4_Thresholds[0].High)
        self.assertEqual( 300, cd._intervention.CD4_Thresholds[1].High)
        self.assertEqual( "GetART",    cd._intervention.CD4_Thresholds[0].Event)
        self.assertEqual( "GetTested", cd._intervention.CD4_Thresholds[1].Event)

    def test_CoitalActRiskFactors(self):
        carf = CoitalActRiskFactors(self.campaign,
                                    acquisition_multiplier=0.5,
                                    transmission_multiplier=2.0,
                                    expiration_event_trigger="CARF_Expired",
                                    expiration_period_distribution=ConstantDistribution(730))
        
        self.assertEqual('CoitalActRiskFactors', carf._intervention['class'])
        self.assertEqual(0.5, carf._intervention.Acquisition_Multiplier)
        self.assertEqual(2.0, carf._intervention.Transmission_Multiplier)
        self.assertEqual("CARF_Expired", carf._intervention.Expiration_Event_Trigger)
        self.assertEqual(DistributionType.CONSTANT_DISTRIBUTION.value, carf._intervention.Expiration_Period_Distribution)
        self.assertEqual(730, carf._intervention.Expiration_Period_Constant)

    def test_FemaleContraceptive(self):
        fc = FemaleContraceptive(self.campaign,
                                 waning_config=wc.RandomBox(constant_effect=0.9,
                                                            exponential_discard_time=3),
                                 usage_duration_distribution=ConstantDistribution(365),
                                 usage_expiration_event="Stopped_Using_Contraceptive" )
        
        self.assertEqual('FemaleContraceptive', fc._intervention['class'])
        self.assertEqual('WaningEffectRandomBox', fc._intervention.Waning_Config['class'])
        self.assertEqual(0.9, fc._intervention.Waning_Config.Initial_Effect)
        self.assertEqual(3, fc._intervention.Waning_Config.Expected_Discard_Time)
        self.assertEqual("Stopped_Using_Contraceptive", fc._intervention.Usage_Expiration_Event)
        self.assertEqual(DistributionType.CONSTANT_DISTRIBUTION.value, fc._intervention.Usage_Duration_Distribution)
        self.assertEqual(365, fc._intervention.Usage_Duration_Constant)

    def test_STIBarrier(self):
        barrier = STIBarrier( self.campaign, 
                              usage_expiration_event="Barrier_Expired",
                              usage_duration_distribution=ConstantDistribution(365),
                              relationship_type=RelationshipType.MARITAL,
                              condom_usage_sigmoid=Sigmoid( min=0.1, max=0.9, mid=2010, rate=0.5))

        self.assertEqual('STIBarrier', barrier._intervention['class'])
        self.assertEqual("Barrier_Expired", barrier._intervention.Usage_Expiration_Event)
        self.assertEqual(DistributionType.CONSTANT_DISTRIBUTION.value, barrier._intervention.Usage_Duration_Distribution)
        self.assertEqual(365, barrier._intervention.Usage_Duration_Constant) 
        self.assertEqual(RelationshipType.MARITAL, barrier._intervention.Relationship_Type)
        self.assertEqual(0.5,  barrier._intervention.Rate)
        self.assertEqual(2010, barrier._intervention.MidYear)
        self.assertEqual(0.9,  barrier._intervention.Late)
        self.assertEqual(0.1,  barrier._intervention.Early)

    def test_SetSexualDebutAge(self):
        ssda = SetSexualDebutAge(self.campaign,
                                 setting_type=SettingType.USER_SPECIFIED,
                                 age_years=18,
                                 distributed_event_trigger="Debut_Age_Set")

        self.assertEqual('SetSexualDebutAge', ssda._intervention['class'])
        self.assertEqual(SettingType.USER_SPECIFIED, ssda._intervention.Setting_Type)
        self.assertEqual(18, ssda._intervention.Age_Years)
        self.assertEqual("Debut_Age_Set", ssda._intervention.Distributed_Event_Trigger)

    def test_StartNewRelationship(self):
        sig = Sigmoid(min=0.1, max=0.9, mid=2010, rate=0.7)

        new_rel = StartNewRelationship(self.campaign,
                                       relationship_type=RelationshipType.MARITAL,
                                       partner_has_ip="Risk:High",
                                       relationship_created_event="Created_New_Relationship",
                                       condom_usage_sigmoid=sig)

        self.assertEqual('StartNewRelationship', new_rel._intervention['class'])
        self.assertEqual(RelationshipType.MARITAL, new_rel._intervention.Relationship_Type)
        self.assertEqual("Risk:High", new_rel._intervention.Partner_Has_IP)
        self.assertEqual("Created_New_Relationship", new_rel._intervention.Relationship_Created_Event)
        self.assertEqual(CondomUsageParametersType.SPECIFY_USAGE, new_rel._intervention.Condom_Usage_Parameters_Type)
        self.assertEqual(0.1,  new_rel._intervention.Condom_Usage_Sigmoid.Min)
        self.assertEqual(0.9,  new_rel._intervention.Condom_Usage_Sigmoid.Max)
        self.assertEqual(2010, new_rel._intervention.Condom_Usage_Sigmoid.Mid)
        self.assertEqual(0.7,  new_rel._intervention.Condom_Usage_Sigmoid.Rate)

    def testIVCalendar(self):
        circ = MaleCircumcision(self.campaign,
                                circumcision_reduced_acquire=0.9,
                                distributed_event_trigger='WasCircumcised')
        
        age_prob_list = []
        age_prob_list.append( IVCalendar.AgeAndProbability(age_days=1, probability=1))
        age_prob_list.append( IVCalendar.AgeAndProbability(age_days=180, probability=0.5))
        age_prob_list.append( IVCalendar.AgeAndProbability(age_days=365, probability=0.25))

        cal = IVCalendar( self.campaign, 
                          intervention_list=[circ],
                          dropout=False, 
                          calendar=age_prob_list )

        self.assertEqual('IVCalendar', cal._intervention['class'])
        self.assertEqual(3, len(cal._intervention.Calendar))
        self.assertEqual(   1, cal._intervention.Calendar[0].Age) 
        self.assertEqual( 180, cal._intervention.Calendar[1].Age) 
        self.assertEqual( 365, cal._intervention.Calendar[2].Age) 
        self.assertEqual(1.00, cal._intervention.Calendar[0].Probability) 
        self.assertEqual(0.50, cal._intervention.Calendar[1].Probability) 
        self.assertEqual(0.25, cal._intervention.Calendar[2].Probability) 
        self.assertEqual('MaleCircumcision', cal._intervention.Actual_IndividualIntervention_Configs[0]['class'])
        self.assertEqual(               0.9, cal._intervention.Actual_IndividualIntervention_Configs[0].Circumcision_Reduced_Acquire)
        self.assertEqual(  'WasCircumcised', cal._intervention.Actual_IndividualIntervention_Configs[0].Distributed_Event_Trigger)

    def test_HIVMuxer_default(self):
        muxer = HIVMuxer(self.campaign,
                         delay_period_distribution=ConstantDistribution(10),
                         muxer_name="TestMuxer")
        self.assertEqual(muxer._intervention.Muxer_Name, "TestMuxer")
        self.assertEqual(muxer._intervention.Delay_Period_Distribution, DistributionType.CONSTANT_DISTRIBUTION.value)
        self.assertEqual(muxer._intervention.Delay_Period_Constant, 10)
        self.assertEqual(muxer._intervention['class'], 'HIVMuxer')

    def test_HIVMuxer(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        muxer = HIVMuxer(self.campaign,
                         muxer_name="TestMuxer",
                         max_entries=2,
                         expiration_period=10,
                         delay_period_distribution=ExponentialDistribution(5),
                         broadcast_delay_complete_event="TestEvent",
                         broadcast_on_expiration_event="TestEvent2",
                         common_intervention_parameters=CIP)

        self.assertEqual(muxer._intervention.Muxer_Name, "TestMuxer")
        self.assertEqual(muxer._intervention.Max_Entries, 2)
        self.assertEqual(muxer._intervention.Expiration_Period, 10)
        self.assertEqual(muxer._intervention.Delay_Period_Distribution, DistributionType.EXPONENTIAL_DISTRIBUTION.value)
        self.assertEqual(muxer._intervention.Delay_Period_Exponential, 5)
        self.assertEqual(muxer._intervention.Broadcast_Event, "TestEvent")
        self.assertEqual(muxer._intervention.Broadcast_On_Expiration_Event, "TestEvent2")
        self.assertCIP(intervention=muxer._intervention, cost=None)
        self.assertEqual(muxer._intervention['class'], 'HIVMuxer')

    def test_HIVPiecewiseByYearAndSexDiagnostic_default(self):
        time_value_map = ValueMap(times=[1, 2], values=[0.5, 0.6])
        diagnostic = HIVPiecewiseByYearAndSexDiagnostic(self.campaign, time_value_map, positive_diagnosis_event="PositiveEvent",)
        self.assertEqual(diagnostic._intervention.Time_Value_Map, time_value_map.to_schema_dict(self.campaign))
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention['class'], 'HIVPiecewiseByYearAndSexDiagnostic')

    def test_HIVPiecewiseByYearAndSexDiagnostic(self):
        time_value_map = ValueMap(times=[1, 2], values=[0.5, 0.6])
        diagnostic = HIVPiecewiseByYearAndSexDiagnostic(self.campaign, time_value_map,
                                                        positive_diagnosis_event="PositiveEvent",
                                                        negative_diagnosis_event="NegativeEvent",
                                                        linear_interpolation=True,
                                                        female_multiplier=0.5,
                                                        default_value=1,
                                                        common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Time_Value_Map, time_value_map.to_schema_dict(self.campaign))
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, "NegativeEvent")
        self.assertEqual(diagnostic._intervention.Interpolation_Order, 1)
        self.assertEqual(diagnostic._intervention.Female_Multiplier, 0.5)
        self.assertEqual(diagnostic._intervention.Default_Value, 1)
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVPiecewiseByYearAndSexDiagnostic')

    def test_HIVRandomChoice_default(self):
        choice_probabilities = [0.25, 0.75]
        choice_names = ["Choice1", "Choice2"]
        random_choice = HIVRandomChoice(self.campaign, choice_probabilities, choice_names)
        self.assertEqual(random_choice._intervention.Choice_Probabilities, choice_probabilities)
        self.assertEqual(random_choice._intervention.Choice_Names, choice_names)
        self.assertEqual(random_choice._intervention['class'], 'HIVRandomChoice')

    def test_HIVRandomChoice(self):
        choice_probabilities = [0.25, 0.75]
        choice_names = ["Choice1", "Choice2"]
        random_choice = HIVRandomChoice(self.campaign, choice_probabilities, choice_names, self.CIP)
        self.assertEqual(random_choice._intervention.Choice_Probabilities, choice_probabilities)
        self.assertEqual(random_choice._intervention.Choice_Names, choice_names)
        self.assertCIP(intervention=random_choice._intervention)
        self.assertEqual(random_choice._intervention['class'], 'HIVRandomChoice')

    def test_HIVRapidHIVDiagnostic_default(self):
        diagnostic = HIVRapidHIVDiagnostic(self.campaign, base_sensitivity=0.98, positive_diagnosis_event="PositiveEvent",)
        self.assertEqual(diagnostic._intervention.Base_Sensitivity, 0.98)
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention['class'], 'HIVRapidHIVDiagnostic')

    def test_HIVRapidHIVDiagnostic_base_sensitivity(self):
        diagnostic = HIVRapidHIVDiagnostic(self.campaign, base_sensitivity=0.98, base_specificity=0.95,
                                           probability_received_result=0.9,
                                           positive_diagnosis_event="PositiveEvent",
                                           negative_diagnosis_event="NegativeEvent",
                                           enable_is_symptomatic=False,
                                           days_to_diagnosis=4,
                                           common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Base_Sensitivity, 0.98)
        self.assertEqual(diagnostic._intervention.Base_Specificity, 0.95)
        self.assertEqual(diagnostic._intervention.Sensitivity_Type, SensitivityType.SINGLE_VALUE.value)
        self.assertEqual(diagnostic._intervention.Probability_Received_Result, 0.9)
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, "NegativeEvent")
        self.assertEqual(diagnostic._intervention.Enable_Is_Symptomatic, 0)
        self.assertEqual(diagnostic._intervention.Days_To_Diagnosis, 4)
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVRapidHIVDiagnostic')

    def test_HIVRapidHIVDiagnostic_sensitivity_versus_time(self):
        value_map = ValueMap(times=[10, 180], values=[0.98, 0.97])
        diagnostic = HIVRapidHIVDiagnostic(self.campaign, sensitivity_versus_time=value_map, base_specificity=0.95,
                                           probability_received_result=0.9,
                                           positive_diagnosis_event="PositiveEvent",
                                           negative_diagnosis_event="NegativeEvent",
                                           enable_is_symptomatic=False,
                                           days_to_diagnosis=4,
                                           common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Sensitivity_Versus_Time, value_map.to_schema_dict(self.campaign))
        self.assertEqual(diagnostic._intervention.Base_Specificity, 0.95)
        self.assertEqual(diagnostic._intervention.Sensitivity_Type, SensitivityType.VERSUS_TIME.value)
        self.assertEqual(diagnostic._intervention.Probability_Received_Result, 0.9)
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, "NegativeEvent")
        self.assertEqual(diagnostic._intervention.Enable_Is_Symptomatic, 0)
        self.assertEqual(diagnostic._intervention.Days_To_Diagnosis, 4)
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVRapidHIVDiagnostic')

    def test_HIVSigmoidByYearAndSexDiagnostic_default(self):
        diagnostic = HIVSigmoidByYearAndSexDiagnostic(self.campaign, year_sigmoid=Sigmoid(), positive_diagnosis_event="PositiveEvent")
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention['class'], 'HIVSigmoidByYearAndSexDiagnostic')

    def test_HIVSigmoidByYearAndSexDiagnostic(self):
        diagnostic = HIVSigmoidByYearAndSexDiagnostic(self.campaign,
                                                      year_sigmoid=Sigmoid(min=0.5, max=0.8, mid=2005, rate=1.5),
                                                      female_multiplier=2,
                                                      positive_diagnosis_event="PositiveEvent",
                                                      negative_diagnosis_event="NegativeEvent",
                                                      common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Ramp_Rate, 1.5)
        self.assertEqual(diagnostic._intervention.Ramp_Min, 0.5)
        self.assertEqual(diagnostic._intervention.Ramp_Max, 0.8)
        self.assertEqual(diagnostic._intervention.Ramp_MidYear, 2005)
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, "NegativeEvent")
        self.assertEqual(diagnostic._intervention.Female_Multiplier, 2)
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVSigmoidByYearAndSexDiagnostic')

    def test_MaleCircumcision_default(self):
        circumcision = MaleCircumcision(self.campaign)
        self.assertEqual(circumcision._intervention.Circumcision_Reduced_Acquire, 0.6)
        self.assertEqual(circumcision._intervention['class'], 'MaleCircumcision')

    def test_MaleCircumcision(self):
        circumcision = MaleCircumcision(self.campaign, distributed_event_trigger="DistributedEvent",
                                        circumcision_reduced_acquire=0.5, common_intervention_parameters=self.CIP)
        self.assertEqual(circumcision._intervention.Circumcision_Reduced_Acquire, 0.5)
        self.assertEqual(circumcision._intervention.Distributed_Event_Trigger, "DistributedEvent")
        self.assertCIP(intervention=circumcision._intervention)
        self.assertEqual(circumcision._intervention['class'], 'MaleCircumcision')

    def test_ModifyStiCoInfectionStatus_default(self):
        status = ModifyStiCoInfectionStatus(self.campaign, False)
        self.assertEqual(status._intervention.New_STI_CoInfection_Status, 0)
        self.assertEqual(status._intervention['class'], 'ModifyStiCoInfectionStatus')

    def test_ModifyStiCoInfectionStatus(self):
        status = ModifyStiCoInfectionStatus(self.campaign, new_sti_coinfection_status=True)
        self.assertEqual(status._intervention.New_STI_CoInfection_Status, 1)
        self.assertEqual(status._intervention['class'], 'ModifyStiCoInfectionStatus')

    def test_PMTCT_default(self):
        pmtct = PMTCT(self.campaign)
        self.assertEqual(pmtct._intervention.Efficacy, 0.5)
        self.assertEqual(pmtct._intervention['class'], 'PMTCT')

    def test_PMTCT(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        pmtct = PMTCT(self.campaign, efficacy=0.9, common_intervention_parameters=CIP)
        self.assertEqual(pmtct._intervention.Efficacy, 0.9)
        self.assertCIP(intervention=pmtct._intervention, cost=None)
        self.assertEqual(pmtct._intervention['class'], 'PMTCT')

    def test_STIIsPostDebut_config(self):
        positive_diagnosis_config = MaleCircumcision(self.campaign)
        negative_diagnosis_config = HIVPiecewiseByYearAndSexDiagnostic(self.campaign, ValueMap(times=[1, 2], values=[0.5, 0.6]),
                                                                       positive_diagnosis_event="PositiveEvent")
        sti_post_debut = STIIsPostDebut(self.campaign, positive_diagnosis_config, negative_diagnosis_config,
                                        common_intervention_parameters=self.CIP)
        self.assertDictEqual(sti_post_debut._intervention.Positive_Diagnosis_Config, positive_diagnosis_config._intervention)
        self.assertDictEqual(sti_post_debut._intervention.Negative_Diagnosis_Config, negative_diagnosis_config._intervention)
        self.assertEqual(sti_post_debut._intervention.Event_Or_Config, "Config")
        self.assertCIP(intervention=sti_post_debut._intervention)
        self.assertEqual(sti_post_debut._intervention['class'], 'STIIsPostDebut')

    def test_STIIsPostDebut_event(self):
        positive_diagnosis_event = "PositiveEvent"
        negative_diagnosis_event = "NegativeEvent"
        sti_post_debut = STIIsPostDebut(self.campaign, positive_diagnosis_event=positive_diagnosis_event,
                                        negative_diagnosis_event=negative_diagnosis_event,
                                        common_intervention_parameters=self.CIP)
        self.assertEqual(sti_post_debut._intervention.Positive_Diagnosis_Event, positive_diagnosis_event)
        self.assertEqual(sti_post_debut._intervention.Negative_Diagnosis_Event, negative_diagnosis_event)
        self.assertEqual(sti_post_debut._intervention.Event_Or_Config, "Event")
        self.assertCIP(intervention=sti_post_debut._intervention)
        self.assertEqual(sti_post_debut._intervention['class'], 'STIIsPostDebut')

    def test_STIIsPostDebut_exception(self):
        # Test exception when both config and event are not set
        with self.assertRaises(ValueError) as context:
            STIIsPostDebut(self.campaign)
        self.assertTrue(" either diagnosis_config(s) or diagnosis_event(s)."
                        in str(context.exception), str(context.exception))

        # Test exception when both config and event are set
        positive_diagnosis_config = MaleCircumcision(self.campaign)
        negative_diagnosis_event = "NegativeEvent"
        with self.assertRaises(ValueError) as context:
            STIIsPostDebut(self.campaign, positive_diagnosis_config=positive_diagnosis_config,
                           negative_diagnosis_event=negative_diagnosis_event)
        self.assertTrue(" either diagnosis_config(s) or diagnosis_event(s)" in
                        str(context.exception), str(context.exception))

    def test_ARTDropout_default(self):
        dropout = ARTDropout(self.campaign)
        self.assertEqual(dropout._intervention['class'], 'ARTDropout')

    def test_ARTDropout(self):
        dropout = ARTDropout(self.campaign,
                             common_intervention_parameters=self.CIP)
        self.assertCIP(intervention=dropout._intervention)
        self.assertEqual(dropout._intervention['class'], 'ARTDropout')

    def test_ARTMortalityTable_missing_required_parameters(self):
        # Test that missing required parameters raise TypeError
        with self.assertRaises(TypeError) as context:
            ARTMortalityTable(self.campaign)
        self.assertIn("missing", str(context.exception))

    def test_ARTMortalityTable_minimal_valid_case(self):
        # Test with minimal valid inputs to verify required parameters work
        mortality_table = [[[0.1]]]  # 1x1x1 table
        art_intervention = ARTMortalityTable(
            self.campaign,
            mortality_table=mortality_table,
            art_duration_days_bins=[0],
            age_years_bins=[18],
            cd4_count_bins=[200]
        )
        
        self.assertEqual(art_intervention._intervention['class'], 'ARTMortalityTable')
        self.assertEqual(art_intervention._intervention.MortalityTable, mortality_table)
        self.assertEqual(art_intervention._intervention.ART_Duration_Days_Bins, [0])
        self.assertEqual(art_intervention._intervention.Age_Years_Bins, [18])
        self.assertEqual(art_intervention._intervention.CD4_Count_Bins, [200])
        # Test default values for optional parameters
        self.assertEqual(art_intervention._intervention.Days_To_Achieve_Viral_Suppression, 183)
        self.assertEqual(art_intervention._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act, 0.08)
        self.assertEqual(art_intervention._intervention.ART_Is_Active_Against_Mortality_And_Transmission, True)

    def test_ARTMortalityTable_with_valid_inputs(self):
        # Valid 3D mortality table: 2x3x2 (duration_bins x age_bins x cd4_bins)
        mortality_table = [
            [[0.1, 0.05], [0.08, 0.04], [0.06, 0.03]],  # First duration bin
            [[0.12, 0.07], [0.09, 0.05], [0.07, 0.04]]   # Second duration bin
        ]
        duration_bins = [0, 365]  # 0 days, 365 days
        age_bins = [18, 35, 50]   # 18, 35, 50 years
        cd4_bins = [200, 500]     # 200, 500 CD4 count
        
        art_mortality = ARTMortalityTable(
            self.campaign,
            mortality_table=mortality_table,
            art_duration_days_bins=duration_bins,
            age_years_bins=age_bins,
            cd4_count_bins=cd4_bins,
            days_to_achieve_viral_suppression=90,
            art_multiplier_on_transmission_prob_per_act=0.05,
            art_is_active_against_mortality_and_transmission=False,
            common_intervention_parameters=self.CIP
        )
        
        self.assertEqual(art_mortality._intervention['class'], 'ARTMortalityTable')
        self.assertEqual(art_mortality._intervention.MortalityTable, mortality_table)
        self.assertEqual(art_mortality._intervention.ART_Duration_Days_Bins, duration_bins)
        self.assertEqual(art_mortality._intervention.Age_Years_Bins, age_bins)
        self.assertEqual(art_mortality._intervention.CD4_Count_Bins, cd4_bins)
        self.assertEqual(art_mortality._intervention.Days_To_Achieve_Viral_Suppression, 90)
        self.assertEqual(art_mortality._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act, 0.05)
        self.assertEqual(art_mortality._intervention.ART_Is_Active_Against_Mortality_And_Transmission, False)
        self.assertCIP(intervention=art_mortality._intervention)

    def test_ARTMortalityTable_invalid_mortality_table_type(self):
        with self.assertRaises(TypeError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table="invalid_string",  # Should be a list
                art_duration_days_bins=[0, 365],
                age_years_bins=[18, 35],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("mortality_table must be a list", str(context.exception))

    def test_ARTMortalityTable_dimension_mismatch(self):
        # Mortality table doesn't match bins
        mortality_table = [
            [[0.1, 0.05]]  # Only 1x1x2, but bins suggest 2x3x2
        ]
        
        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[0, 365],  # 2 bins
                age_years_bins=[18, 35, 50],      # 3 bins  
                cd4_count_bins=[200, 500]         # 2 bins
            )
        self.assertIn("must match", str(context.exception))

    def test_ARTMortalityTable_negative_mortality_rate(self):
        mortality_table = [
            [[-0.1, 0.05]]  # Negative rate should be rejected
        ]
        
        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[0],
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("must between 0 and 1", str(context.exception))

    def test_ARTMortalityTable_large_mortality_rate(self):
        mortality_table = [
            [[0.1, 1.05]]  # Rate greater than 1 should be rejected
        ]

        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[0],
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("must between 0 and 1", str(context.exception))

    def test_ARTMortalityTable_negative_art_duration(self):
        mortality_table = [
            [[0.1, 0.05]]
        ]

        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[-1], # Negative rate should be rejected
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("must be non-negative", str(context.exception))

    def test_ARTMortalityTable_large_cd4_count(self):
        mortality_table = [
            [[0.1, 0.05]]
        ]

        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[10],
                age_years_bins=[18],
                cd4_count_bins=[200, 1001]  # CD4 count greater than 1000
            )
        self.assertIn("must be less than or equal to 1000", str(context.exception))


    def test_ARTMortalityTable_unordered_bins(self):
        mortality_table = [
            [[0.1, 0.05]],
            [[0.08, 0.04]]
        ]
        
        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[365, 0],  # Wrong order
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("must be in ascending order", str(context.exception))

    def test_ARTMortalityTable_empty_mortality_table(self):
        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=[],  # Empty list
                art_duration_days_bins=[0],
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("mortality_table first dimension (0) must match art_duration_days_bins length (1)", str(context.exception))

    def test_ARTMortalityTable_empty_age_years_bins(self):
        with self.assertRaises(ValueError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=[[[1]]],
                art_duration_days_bins=[0],
                age_years_bins=[], # Empty list
                cd4_count_bins=[200, 500]
            )
        self.assertIn("cannot be empty", str(context.exception))

    def test_ARTMortalityTable_tuple_not_allowed(self):
        # Test that tuples are not allowed (only lists)
        mortality_table = (  # Using tuple instead of list
            (
                (0.1, 0.05),
            ),
        )
        
        with self.assertRaises(TypeError) as context:
            ARTMortalityTable(
                self.campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[0],
                age_years_bins=[18],
                cd4_count_bins=[200, 500]
            )
        self.assertIn("mortality_table must be a list", str(context.exception))

    def test_ARTMortalityTable_documentation_example(self):
        # Test the exact example from the class documentation
        # Define mortality table: 5 duration bins x 2 age bins x 7 CD4 bins
        mortality_table = [
            [  # Duration bin 0 (0-6 months)
                [0.2015, 0.2015, 0.1128, 0.0625, 0.0312, 0.0206, 0.0162],  # Age 0-40
                [0.0875, 0.0875, 0.0490, 0.0271, 0.0136, 0.0062, 0.0041]   # Age 40+
            ],
            [  # Duration bin 1 (6-12 months)
                [0.0271, 0.0271, 0.0184, 0.0149, 0.0074, 0.0048, 0.0048],
                [0.0171, 0.0171, 0.0116, 0.0094, 0.0047, 0.0030, 0.0030]
            ],
            [  # Duration bin 2 (12-24 months)
                [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026],
                [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026]
            ],
            [  # Duration bin 3 (24-36 months)
                [0.0075, 0.0075, 0.0051, 0.0041, 0.0021, 0.0021, 0.0021],
                [0.0075, 0.0075, 0.0051, 0.0041, 0.0021, 0.0021, 0.0021]
            ],
            [  # Duration bin 4 (36+ months)
                [0.0060, 0.0060, 0.0041, 0.0033, 0.0017, 0.0017, 0.0017],
                [0.0060, 0.0060, 0.0041, 0.0033, 0.0017, 0.0017, 0.0017]
            ]
        ]

        # Create the intervention with the documentation example parameters
        art_intervention = ARTMortalityTable(
            self.campaign,
            mortality_table=mortality_table,
            art_duration_days_bins=[0, 183, 365, 730, 1095],  # 0, 6mo, 1yr, 2yr, 3yr in days
            age_years_bins=[0, 40],                           # Under 40, 40+
            cd4_count_bins=[0, 25, 74.5, 149.5, 274.5, 424.5, 624.5],  # CD4 count thresholds
            days_to_achieve_viral_suppression=183.0,
            art_multiplier_on_transmission_prob_per_act=0.08,
            art_is_active_against_mortality_and_transmission=True,
            common_intervention_parameters=self.CIP
        )

        # Verify the intervention was created correctly
        self.assertEqual(art_intervention._intervention['class'], 'ARTMortalityTable')
        
        # Verify mortality table dimensions and structure
        self.assertEqual(len(art_intervention._intervention.MortalityTable), 5)  # 5 duration bins
        self.assertEqual(len(art_intervention._intervention.MortalityTable[0]), 2)  # 2 age bins
        self.assertEqual(len(art_intervention._intervention.MortalityTable[0][0]), 7)  # 7 CD4 bins
        
        # Verify specific mortality values from the example
        self.assertEqual(art_intervention._intervention.MortalityTable[0][0][0], 0.2015)  # First duration, first age, first CD4
        self.assertEqual(art_intervention._intervention.MortalityTable[0][1][6], 0.0041)  # First duration, second age, last CD4
        self.assertEqual(art_intervention._intervention.MortalityTable[4][1][4], 0.0017)  # Last duration, second age, middle CD4
        
        # Verify bins
        self.assertEqual(art_intervention._intervention.ART_Duration_Days_Bins, [0, 183, 365, 730, 1095])
        self.assertEqual(art_intervention._intervention.Age_Years_Bins, [0, 40])
        self.assertEqual(art_intervention._intervention.CD4_Count_Bins, [0, 25, 74.5, 149.5, 274.5, 424.5, 624.5])
        
        # Verify other parameters match the example
        self.assertEqual(art_intervention._intervention.Days_To_Achieve_Viral_Suppression, 183.0)
        self.assertEqual(art_intervention._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act, 0.08)
        self.assertEqual(art_intervention._intervention.ART_Is_Active_Against_Mortality_And_Transmission, True)
        
        # Verify common intervention parameters were applied
        self.assertCIP(intervention=art_intervention._intervention)
        
        # Verify medical realism - mortality decreases over time on ART
        # Compare mortality rates across duration bins for the same age/CD4 combination
        duration_0_mortality = art_intervention._intervention.MortalityTable[0][0][0]  # 0.2015
        duration_1_mortality = art_intervention._intervention.MortalityTable[1][0][0]  # 0.0271
        duration_2_mortality = art_intervention._intervention.MortalityTable[2][0][0]  # 0.0095
        duration_3_mortality = art_intervention._intervention.MortalityTable[3][0][0]  # 0.0075
        duration_4_mortality = art_intervention._intervention.MortalityTable[4][0][0]  # 0.0060
        
        # Mortality should decrease as time on ART increases
        self.assertEqual(duration_0_mortality, 0.2015)
        self.assertEqual(duration_1_mortality, 0.0271)
        self.assertEqual(duration_2_mortality, 0.0095)
        self.assertEqual(duration_3_mortality, 0.0075)
        self.assertEqual(duration_4_mortality, 0.0060)

    def test_AntiretroviralTherapy_default(self):
        therapy = AntiretroviralTherapy(self.campaign)
        self.assertEqual(therapy._intervention['class'], 'AntiretroviralTherapy')

    def test_AntiretroviralTherapy(self):
        therapy = AntiretroviralTherapy(self.campaign,
                                        days_to_achieve_viral_suppression=30,
                                        art_survival_who_stage_threshold_for_cox=1,
                                        art_survival_baseline_hazard_weibull_scale=100,
                                        art_survival_baseline_hazard_weibull_shape=0.5,
                                        art_survival_hazard_ratio_female=0.2,
                                        art_survival_hazard_ratio_cd4_intercept=1,
                                        art_survival_hazard_ratio_cd4_slope=-0.1,
                                        art_survival_hazard_ratio_body_weight_kg_intercept=2,
                                        art_survival_hazard_ratio_body_weight_kg_slope=-0.2,
                                        art_survival_hazard_ratio_age_over_40yr=11,
                                        art_survival_hazard_ratio_who_stage_3plus=3,
                                        art_cd4_at_initiation_saturating_reduction_in_mortality=8,
                                        art_is_active_against_mortality_and_transmission=True,
                                        art_multiplier_on_transmission_prob_per_act=0.8,
                                        common_intervention_parameters=self.CIP)
        self.assertEqual(therapy._intervention.Days_To_Achieve_Viral_Suppression, 30)
        self.assertEqual(therapy._intervention.ART_Survival_WHO_Stage_Threshold_For_Cox, 1)
        self.assertEqual(therapy._intervention.ART_Survival_Baseline_Hazard_Weibull_Scale, 100)
        self.assertEqual(therapy._intervention.ART_Survival_Baseline_Hazard_Weibull_Shape, 0.5)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Female, 0.2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_CD4_Intercept, 1)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_CD4_Slope, -0.1)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Intercept, 2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Slope, -0.2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Age_Over_40Yr, 11)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_WHO_Stage_3Plus, 3)
        self.assertEqual(therapy._intervention.ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality, 8)
        self.assertEqual(therapy._intervention.ART_Is_Active_Against_Mortality_And_Transmission, 1)
        self.assertEqual(therapy._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act, 0.8)
        self.assertCIP(intervention=therapy._intervention)
        self.assertEqual(therapy._intervention['class'], 'AntiretroviralTherapy')

    def test_AntiretroviralTherapyFull(self):
        therapy = AntiretroviralTherapyFull(self.campaign,
                                            time_on_art_distribution=ConstantDistribution(7300),
                                            stop_art_event="Dropped_ART",
                                            days_to_achieve_viral_suppression=30,
                                            art_survival_who_stage_threshold_for_cox=1,
                                            art_survival_baseline_hazard_weibull_scale=100,
                                            art_survival_baseline_hazard_weibull_shape=0.5,
                                            art_survival_hazard_ratio_female=0.2,
                                            art_survival_hazard_ratio_cd4_intercept=1,
                                            art_survival_hazard_ratio_cd4_slope=-0.1,
                                            art_survival_hazard_ratio_body_weight_kg_intercept=2,
                                            art_survival_hazard_ratio_body_weight_kg_slope=-0.2,
                                            art_survival_hazard_ratio_age_over_40yr=11,
                                            art_survival_hazard_ratio_who_stage_3plus=3,
                                            art_cd4_at_initiation_saturating_reduction_in_mortality=8,
                                            art_is_active_against_mortality_and_transmission=False,
                                            art_multiplier_on_transmission_prob_per_act=0.8,
                                            common_intervention_parameters=self.CIP)
        self.assertEqual(therapy._intervention.Time_On_ART_Distribution, DistributionType.CONSTANT_DISTRIBUTION.value)
        self.assertEqual(therapy._intervention.Time_On_ART_Constant, 7300)
        self.assertEqual(therapy._intervention.Stop_ART_Event, "Dropped_ART")
        self.assertEqual(therapy._intervention.Days_To_Achieve_Viral_Suppression, 30)
        self.assertEqual(therapy._intervention.ART_Survival_WHO_Stage_Threshold_For_Cox, 1)
        self.assertEqual(therapy._intervention.ART_Survival_Baseline_Hazard_Weibull_Scale, 100)
        self.assertEqual(therapy._intervention.ART_Survival_Baseline_Hazard_Weibull_Shape, 0.5)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Female, 0.2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_CD4_Intercept, 1)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_CD4_Slope, -0.1)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Intercept, 2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Slope, -0.2)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_Age_Over_40Yr, 11)
        self.assertEqual(therapy._intervention.ART_Survival_Hazard_Ratio_WHO_Stage_3Plus, 3)
        self.assertEqual(therapy._intervention.ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality, 8)
        self.assertEqual(therapy._intervention.ART_Is_Active_Against_Mortality_And_Transmission, 0)
        self.assertEqual(therapy._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act, 0.8)
        self.assertCIP(intervention=therapy._intervention)
        self.assertEqual(therapy._intervention['class'], 'AntiretroviralTherapyFull')

    def test_HIVARTStagingByCD4Diagnostic_default(self):
        diagnostic = HIVARTStagingByCD4Diagnostic(self.campaign,
                                                  cd4_threshold=ValueMap(times=[2010, 2020], values=[200, 350]),
                                                  if_pregnant=ValueMap(times=[2010, 2020], values=[250, 450]),
                                                  if_active_tb=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                  positive_diagnosis_event="PositiveEvent",)
        self.assertEqual(diagnostic._intervention.Threshold, {"Times": [2010, 2020], "Values": [200, 350]})
        self.assertEqual(diagnostic._intervention.If_Pregnant, {"Times": [2010, 2020], "Values": [250, 450]})
        self.assertEqual(diagnostic._intervention.If_Active_TB, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, 'PositiveEvent')
        self.assertEqual(diagnostic._intervention['class'], 'HIVARTStagingByCD4Diagnostic')

    def test_HIVARTStagingByCD4Diagnostic(self):
        diagnostic = HIVARTStagingByCD4Diagnostic(self.campaign,
                                                  cd4_threshold=ValueMap(times=[2010, 2020], values=[200, 350]),
                                                  if_pregnant=ValueMap(times=[2010, 2020], values=[250, 450]),
                                                  if_active_tb=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                  positive_diagnosis_event="PositiveEvent",
                                                  negative_diagnosis_event="NegativeEvent",
                                                  individual_property_active_tb_key="HasActiveTB",
                                                  individual_property_active_tb_value="Yes",
                                                  common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Threshold, {"Times": [2010, 2020], "Values": [200, 350]})
        self.assertEqual(diagnostic._intervention.If_Pregnant, {"Times": [2010, 2020], "Values": [250, 450]})
        self.assertEqual(diagnostic._intervention.If_Active_TB, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, 'PositiveEvent')
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, 'NegativeEvent')
        self.assertEqual(diagnostic._intervention.Individual_Property_Active_TB_Key, 'HasActiveTB')
        self.assertEqual(diagnostic._intervention.Individual_Property_Active_TB_Value, 'Yes')
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVARTStagingByCD4Diagnostic')

    def test_HIVARTStagingCD4AgnosticDiagnostic_default(self):
        diagnostic = HIVARTStagingCD4AgnosticDiagnostic(self.campaign,
                                                        child_treat_under_age_in_years_threshold=ValueMap(times=[2010, 2020], values=[200, 300]),
                                                        child_by_who_stage=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                        child_by_tb=ValueMap(times=[2010, 2020], values=[100, 200]),
                                                        adult_by_who_stage=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                        adult_by_tb=ValueMap(times=[2010, 2020], values=[100, 200]),
                                                        adult_by_pregnant=ValueMap(times=[2010, 2020], values=[200, 300]),
                                                        positive_diagnosis_event="PositiveEvent")
        self.assertEqual(diagnostic._intervention.Child_Treat_Under_Age_In_Years_Threshold, {"Times": [2010, 2020], "Values": [200, 300]})
        self.assertEqual(diagnostic._intervention.Child_By_WHO_Stage, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Child_By_TB, {"Times": [2010, 2020], "Values": [100, 200]})
        self.assertEqual(diagnostic._intervention.Adult_By_WHO_Stage, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Adult_By_TB, {"Times": [2010, 2020], "Values": [100, 200]})
        self.assertEqual(diagnostic._intervention.Adult_By_Pregnant, {"Times": [2010, 2020], "Values": [200, 300]})
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, 'PositiveEvent')
        self.assertEqual(diagnostic._intervention['class'], 'HIVARTStagingCD4AgnosticDiagnostic')

    def test_HIVARTStagingCD4AgnosticDiagnostic(self):
        diagnostic = HIVARTStagingCD4AgnosticDiagnostic(self.campaign,
                                                        child_treat_under_age_in_years_threshold=ValueMap(times=[2010, 2020], values=[200, 300]),
                                                        child_by_who_stage=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                        child_by_tb=ValueMap(times=[2010, 2020], values=[100, 200]),
                                                        adult_by_who_stage=ValueMap(times=[2010, 2020], values=[150, 250]),
                                                        adult_by_tb=ValueMap(times=[2010, 2020], values=[100, 200]),
                                                        adult_by_pregnant=ValueMap(times=[2010, 2020], values=[200, 300]),
                                                        positive_diagnosis_event="PositiveEvent",
                                                        negative_diagnosis_event="NegativeEvent",
                                                        individual_property_active_tb_key="HasActiveTB",
                                                        individual_property_active_tb_value="Yes",
                                                        adult_treatment_age=15,
                                                        common_intervention_parameters=self.CIP)
        self.assertEqual(diagnostic._intervention.Child_Treat_Under_Age_In_Years_Threshold, {"Times": [2010, 2020], "Values": [200, 300]})
        self.assertEqual(diagnostic._intervention.Child_By_WHO_Stage, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Child_By_TB, {"Times": [2010, 2020], "Values": [100, 200]})
        self.assertEqual(diagnostic._intervention.Adult_By_WHO_Stage, {"Times": [2010, 2020], "Values": [150, 250]})
        self.assertEqual(diagnostic._intervention.Adult_By_TB, {"Times": [2010, 2020], "Values": [100, 200]})
        self.assertEqual(diagnostic._intervention.Adult_By_Pregnant, {"Times": [2010, 2020], "Values": [200, 300]})
        self.assertEqual(diagnostic._intervention.Positive_Diagnosis_Event, 'PositiveEvent')
        self.assertEqual(diagnostic._intervention.Negative_Diagnosis_Event, 'NegativeEvent')
        self.assertEqual(diagnostic._intervention.Individual_Property_Active_TB_Key, 'HasActiveTB')
        self.assertEqual(diagnostic._intervention.Individual_Property_Active_TB_Value, 'Yes')
        self.assertEqual(diagnostic._intervention.Adult_Treatment_Age, 15)
        self.assertCIP(intervention=diagnostic._intervention)
        self.assertEqual(diagnostic._intervention['class'], 'HIVARTStagingCD4AgnosticDiagnostic')

    def test_HIVDrawBlood(self):
        draw_blood = HIVDrawBlood(self.campaign,
                                  positive_diagnosis_event="PositiveEvent",
                                  common_intervention_parameters=self.CIP)
        self.assertCIP(intervention=draw_blood._intervention)
        self.assertEqual(draw_blood._intervention.Positive_Diagnosis_Event, "PositiveEvent")
        self.assertEqual(draw_blood._intervention['class'], 'HIVDrawBlood')

    def test_InterventionForCurrentPartners_Config(self):
        CIP = deepcopy(self.CIP)
        CIP.cost = None
        intervention_config = MaleCircumcision(self.campaign)
        intervention = InterventionForCurrentPartners(self.campaign,
                                                      intervention_config=intervention_config,
                                                      prioritize_partners_by=PrioritizePartnersBy.RELATIONSHIP_TYPE,
                                                      relationship_types=[RelationshipType.MARITAL, RelationshipType.COMMERCIAL],
                                                      minimum_duration_years=1,
                                                      maximum_partners=10,
                                                      common_intervention_parameters=CIP)
        self.assertEqual(intervention._intervention.Prioritize_Partners_By, PrioritizePartnersBy.RELATIONSHIP_TYPE.value)
        self.assertEqual(intervention._intervention.Relationship_Types, [RelationshipType.MARITAL.value, RelationshipType.COMMERCIAL.value])
        self.assertEqual(intervention._intervention.Minimum_Duration_Years, 1)
        self.assertEqual(intervention._intervention.Maximum_Partners, 10)
        self.assertDictEqual(intervention._intervention.Intervention_Config, intervention_config._intervention)
        self.assertEqual(intervention._intervention.Event_Or_Config, "Config")
        self.assertCIP(intervention=intervention._intervention, cost=None)
        self.assertEqual(intervention._intervention['class'], 'InterventionForCurrentPartners')

    def test_InterventionForCurrentPartners_Event(self):
        intervention = InterventionForCurrentPartners(self.campaign,
                                                      broadcast_event="BroadcastEvent",
                                                      prioritize_partners_by=PrioritizePartnersBy.OLDER_AGE,
                                                      minimum_duration_years=1,
                                                      maximum_partners=10)
        self.assertEqual(intervention._intervention.Prioritize_Partners_By, PrioritizePartnersBy.OLDER_AGE.value)
        self.assertEqual(intervention._intervention.Minimum_Duration_Years, 1)
        self.assertEqual(intervention._intervention.Maximum_Partners, 10)
        self.assertEqual(intervention._intervention.Broadcast_Event, "BroadcastEvent")
        self.assertEqual(intervention._intervention.Event_Or_Config, "Event")
        self.assertEqual(intervention._intervention['class'], 'InterventionForCurrentPartners')

    def test_InterventionForCurrentPartners_Exception_1(self):
        # Test exception when relationship_types is not set
        with self.assertRaises(ValueError) as context:
            intervention_config = MaleCircumcision(self.campaign)
            InterventionForCurrentPartners(self.campaign,
                                           intervention_config=intervention_config,
                                           prioritize_partners_by=PrioritizePartnersBy.RELATIONSHIP_TYPE)
        self.assertTrue("The relationship_types parameter must be set when prioritize_partners_by is set to RELATIONSHIP_TYPE." in str(context.exception))

    def test_InterventionForCurrentPartners_Exception_2(self):
        # Test exception when both config and event are not set
        with self.assertRaises(ValueError) as context:
            InterventionForCurrentPartners(self.campaign)
        self.assertTrue("You must set either intervention_config or broadcast_event." in str(context.exception))

    def test_InterventionForCurrentPartners_Exception_3(self):
        # Test exception when both config and event are set
        intervention_config = MaleCircumcision(self.campaign)
        with self.assertRaises(ValueError) as context:
            InterventionForCurrentPartners(self.campaign,
                                           intervention_config=intervention_config,
                                           broadcast_event="BroadcastEvent")
        self.assertTrue("You can only set either intervention_config or broadcast_event, but not both." in str(context.exception))


if __name__ == '__main__':
    unittest.main()
