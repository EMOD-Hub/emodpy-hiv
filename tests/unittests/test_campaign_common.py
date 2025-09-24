import unittest
import pytest
from pathlib import Path
import sys
import os
from emod_api import schema_to_class as s2c
from emod_api import campaign

from emodpy_hiv.campaign.common import (TargetGender, TargetDemographicsConfig, MAX_AGE_YEARS,
                                        RepetitionConfig, PropertyRestrictions, NChooserTargetedDistributionHIV, ValueMap,
                                        CommonInterventionParameters)
from emodpy_hiv.utils.emod_enum import TargetDiseaseState

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest


# Todo: package some of the tests classes from Emodpy as a standalone package and import them here.
@pytest.mark.unit
class TestDemographicsConfig(unittest.TestCase):
    def setUp(self):
        with open(manifest.schema_path) as schema_file:
            self.schema_json = json.load(schema_file)
        print(f"running test: {self._testMethodName}:")

    def test_init(self):
        demo_config = TargetDemographicsConfig()
        self.assertEqual(demo_config.demographic_coverage, 1.0)
        self.assertEqual(demo_config.target_age_min, 0)
        self.assertEqual(demo_config.target_age_max, MAX_AGE_YEARS)
        self.assertEqual(demo_config.target_gender, TargetGender.ALL)
        self.assertEqual(demo_config.target_residents_only, False)

    def test_set_target_demographics_default(self):
        demo_config = TargetDemographicsConfig()
        campaign_object = s2c.get_class_with_defaults('NodeLevelHealthTriggeredIV', schema_json=self.schema_json)
        demo_config._set_target_demographics(campaign_object)
        self.assertEqual(campaign_object.Demographic_Coverage, 1.0)
        self.assertEqual(campaign_object.Target_Residents_Only, False)
        self.assertEqual(campaign_object.Target_Demographic, "Everyone")

    def test_set_target_demographics_age(self):
        demo_config = TargetDemographicsConfig(demographic_coverage=0.6, target_age_min=15, target_age_max=49)
        campaign_object = s2c.get_class_with_defaults('NodeLevelHealthTriggeredIV', schema_json=self.schema_json)
        demo_config._set_target_demographics(campaign_object)
        self.assertEqual(campaign_object.Demographic_Coverage, 0.6)
        self.assertEqual(campaign_object.Target_Residents_Only, False)
        self.assertEqual(campaign_object.Target_Age_Min, 15)
        self.assertEqual(campaign_object.Target_Age_Max, 49)
        self.assertEqual(campaign_object.Target_Demographic, 'ExplicitAgeRanges')

    def test_set_target_demographics_gender(self):
        demo_config = TargetDemographicsConfig(demographic_coverage=0.9, target_gender=TargetGender.FEMALE)
        campaign_object = s2c.get_class_with_defaults('NodeLevelHealthTriggeredIV', schema_json=self.schema_json)
        demo_config._set_target_demographics(campaign_object)
        self.assertEqual(campaign_object.Demographic_Coverage, 0.9)
        self.assertEqual(campaign_object.Target_Residents_Only, False)
        self.assertEqual(campaign_object.Target_Gender, TargetGender.FEMALE.value)
        self.assertEqual(campaign_object.Target_Demographic, 'ExplicitGender')

    def test_set_target_demographics_age_gender(self):
        demo_config = TargetDemographicsConfig(demographic_coverage=0.8, target_age_min=10, target_age_max=30, target_gender=TargetGender.MALE)
        campaign_object = s2c.get_class_with_defaults('NodeLevelHealthTriggeredIV', schema_json=self.schema_json)
        demo_config._set_target_demographics(campaign_object)
        self.assertEqual(campaign_object.Demographic_Coverage, 0.8)
        self.assertEqual(campaign_object.Target_Residents_Only, False)
        self.assertEqual(campaign_object.Target_Age_Min, 10)
        self.assertEqual(campaign_object.Target_Age_Max, 30)
        self.assertEqual(campaign_object.Target_Gender, TargetGender.MALE.value)
        self.assertEqual(campaign_object.Target_Demographic, 'ExplicitAgeRangesAndGender')

    def test_set_target_demographics_residents_only(self):
        demo_config = TargetDemographicsConfig(demographic_coverage=0.7, target_residents_only=True)
        campaign_object = s2c.get_class_with_defaults('NodeLevelHealthTriggeredIV', schema_json=self.schema_json)
        demo_config._set_target_demographics(campaign_object)
        self.assertEqual(campaign_object.Demographic_Coverage, 0.7)
        self.assertEqual(campaign_object.Target_Residents_Only, True)
        self.assertEqual(campaign_object.Target_Demographic, 'Everyone')


@pytest.mark.unit
class TestRepetitionConfig(unittest.TestCase):
    def setUp(self):
        with open(manifest.schema_path) as schema_file:
            self.schema_json = json.load(schema_file)
        print(f"running test: {self._testMethodName}:")

    def test_init(self):
        with self.assertWarns(Warning) as context:
            repetition_config = RepetitionConfig()
            self.assertEqual(repetition_config.number_repetitions, 1)
            self.assertEqual(repetition_config.timesteps_between_repetitions, None)
        self.assertTrue("the event will not be repeated" in str(context.warning))

    def test_set_repetitions(self):
        repetition_config = RepetitionConfig(number_repetitions=3, timesteps_between_repetitions=5)
        campaign_object = s2c.get_class_with_defaults('StandardEventCoordinator', schema_json=self.schema_json)
        repetition_config._set_repetitions(campaign_object)
        self.assertEqual(campaign_object["Number_Repetitions"], 3)
        self.assertEqual(campaign_object["Timesteps_Between_Repetitions"], 5)

    def test_set_repetitions_infinity(self):
        repetition_config = RepetitionConfig(infinite_repetitions=True, timesteps_between_repetitions=30)
        campaign_object = s2c.get_class_with_defaults('StandardEventCoordinator', schema_json=self.schema_json)
        repetition_config._set_repetitions(campaign_object)
        self.assertEqual(campaign_object["Number_Repetitions"], -1)
        self.assertEqual(campaign_object["Timesteps_Between_Repetitions"], 30)

    def test_set_repetitions_exception_1(self):
        with self.assertRaises(ValueError) as context:
            RepetitionConfig(number_repetitions=2)
        self.assertTrue("timesteps_between_repetitions must be set" in str(context.exception))

    def test_set_repetitions_exception_2(self):
        with self.assertRaises(ValueError) as context:
            RepetitionConfig(infinite_repetitions=True)
        self.assertTrue("timesteps_between_repetitions must be set" in str(context.exception))

    def test_set_repetitions_exception_3(self):
        with self.assertRaises(ValueError) as context:
            RepetitionConfig(infinite_repetitions=True, timesteps_between_repetitions=-1)
        self.assertTrue("timesteps_between_repetitions is set to a non positive value" in str(context.exception))

    def test_set_repetitions_exception_4(self):
        with self.assertRaises(ValueError) as context:
            RepetitionConfig(number_repetitions=2, timesteps_between_repetitions=0)
        self.assertTrue("timesteps_between_repetitions is set to a non positive value" in str(context.exception))


@pytest.mark.unit
class TestPropertyRestrictions(unittest.TestCase):
    def setUp(self):
        with open(manifest.schema_path) as schema_file:
            self.schema_json = json.load(schema_file)
        print(f"running test: {self._testMethodName}:")

    def test_init(self):
        with self.assertWarns(Warning) as context:
            property_restrictions = PropertyRestrictions()
            self.assertIsNone(property_restrictions.individual_property_restrictions)
            self.assertIsNone(property_restrictions.node_property_restrictions)
        self.assertTrue("No property restrictions are provided." in str(context.warning))

    def test_individual_space(self):
        campaign_object = s2c.get_class_with_defaults('ReferenceTrackingEventCoordinator', schema_json=self.schema_json)
        property_restrictions = PropertyRestrictions(
            individual_property_restrictions=[[" Risk : High ", " InterventionStatus : ARTStaging "]])
        property_restrictions._set_property_restrictions(campaign_object)
        self.assertEqual(campaign_object["Property_Restrictions"], [])
        self.assertEqual(campaign_object["Property_Restrictions_Within_Node"],
                         [{"Risk": "High", "InterventionStatus": "ARTStaging"}])
        self.assertEqual(campaign_object["Node_Property_Restrictions"], [])

    def test_individual_and_logic(self):
        campaign_object = s2c.get_class_with_defaults('ReferenceTrackingEventCoordinator', schema_json=self.schema_json)
        property_restrictions = PropertyRestrictions(
            individual_property_restrictions=[["Risk:HIGH", "InterventionStatus:ARTStaging"]])
        property_restrictions._set_property_restrictions(campaign_object)
        self.assertEqual(campaign_object["Property_Restrictions"], [])
        self.assertEqual(campaign_object["Property_Restrictions_Within_Node"],
                         [{"Risk": "HIGH", "InterventionStatus": "ARTStaging"}])
        self.assertEqual(campaign_object["Node_Property_Restrictions"], [])

    def test_individual_and_or_logic(self):
        campaign_object = s2c.get_class_with_defaults('ReferenceTrackingEventCoordinator', schema_json=self.schema_json)
        individual_property_restrictions = [["Risk:HIGH",   "InterventionStatus:ARTStaging"], # noqa: E241
                                            ["Risk:MEDIUM", "InterventionStatus:ARTStaging"]]
        property_restrictions = PropertyRestrictions(individual_property_restrictions)
        property_restrictions._set_property_restrictions(campaign_object)
        self.assertEqual(campaign_object["Property_Restrictions"], [])
        self.assertEqual(campaign_object["Property_Restrictions_Within_Node"],
                         [{"Risk": "HIGH", "InterventionStatus": "ARTStaging"},
                          {"Risk": "MEDIUM", "InterventionStatus": "ARTStaging"}])
        self.assertEqual(campaign_object["Node_Property_Restrictions"], [])

    def test_node(self):
        campaign_object = s2c.get_class_with_defaults('ReferenceTrackingEventCoordinator', schema_json=self.schema_json)
        property_restrictions = PropertyRestrictions(
            node_property_restrictions=[["Risk:MEDIUM", "Place:URBAN"], ["Risk:LOW", "Place:RURAL"]])
        property_restrictions._set_property_restrictions(campaign_object)
        self.assertEqual(campaign_object["Property_Restrictions"], [])
        self.assertEqual(campaign_object["Property_Restrictions_Within_Node"], [])
        self.assertEqual(campaign_object["Node_Property_Restrictions"],
                         [{"Risk": "MEDIUM", "Place": "URBAN"},
                          {"Risk": "LOW", "Place": "RURAL"}])

    def test_exception_invalid_restriction(self):
        with self.assertRaises(ValueError) as context:
            PropertyRestrictions(individual_property_restrictions=[["'Risk':'HIGH'"]])
        self.assertTrue("should be strings that represent dictionaries key:value pairs with at least one alphanumeric "
                        "character before and after ':'" in str(context.exception))

    def test_exception_invalid_restriction_2(self):
        with self.assertRaises(ValueError) as context:
            PropertyRestrictions(individual_property_restrictions=[['Risk HIGH']])
        self.assertTrue("should be strings that represent dictionaries key:value pairs with at least one alphanumeric "
                        "character before and after ':'" in str(context.exception))

    def test_exception_invalid_restriction_3(self):
        with self.assertRaises(ValueError) as context:
            PropertyRestrictions(individual_property_restrictions=[{'Risk': 'HIGH'}])
        self.assertTrue("The individual_property_restrictions should be a 2D list" in str(context.exception))


# This one is not in the Emodpy package
@pytest.mark.unit
class TestNChooserTargetedDistributionHIV(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.campaign_obj = campaign
        cls.campaign_obj.set_schema(manifest.schema_path)
        cls.age_ranges_years = [
            [0, 1, 15, 50],                          # Min ages
            [0.99999, 14.9999999, 49.9999, 64.9999]  # Max ages
        ]
        cls.num_targeted_females = [0, 0, 0, 0]
        cls.num_targeted_males = [0, 8064.777513, 25054.39959, 179.0207223]
        cls.start_year = 2010.0
        cls.end_year = 2010.999
        cls.expected_age_ranges = [{'Max': 0.99999, 'Min': 0.0}, {'Max': 14.9999999, 'Min': 1.0},
                                   {'Max': 49.9999, 'Min': 15.0}, {'Max': 64.9999, 'Min': 50.0}]

    def setUp(self):
        self.campaign_obj.reset()
        print(f"running test: {self._testMethodName}:")

    def test_with_disease_state(self):
        target_distribution = NChooserTargetedDistributionHIV(
            age_ranges_years=self.age_ranges_years,
            start_year=self.start_year,
            end_year=self.end_year,
            num_targeted_females=self.num_targeted_females,
            num_targeted_males=self.num_targeted_males,
            target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.HAS_INTERVENTION],
                                  [TargetDiseaseState.TESTED_POSITIVE, TargetDiseaseState.HAS_INTERVENTION]],
            target_disease_state_has_intervention_name="DMPA_or_control"
        )

        self.assertIsInstance(target_distribution, NChooserTargetedDistributionHIV)
        distribution = target_distribution.to_schema_dict(self.campaign_obj)
        self.assertIsInstance(distribution, s2c.ReadOnlyDict)
        self.assertListEqual(distribution.Age_Ranges_Years, self.expected_age_ranges)
        self.assertListEqual(distribution.Num_Targeted_Males, [0, 8064.777513, 25054.39959, 179.0207223])
        self.assertListEqual(distribution.Num_Targeted_Females, [0, 0, 0, 0])
        self.assertListEqual(distribution.Num_Targeted, [])
        self.assertEqual(distribution.Start_Year, self.start_year)
        self.assertEqual(distribution.End_Year, self.end_year)
        self.assertEqual(distribution.Target_Disease_State, [['HIV_Positive', 'Has_Intervention'],
                                                             ['Tested_Positive', 'Has_Intervention']])
        self.assertEqual(distribution.Target_Disease_State_Has_Intervention_Name, "DMPA_or_control")

    def test_with_property_restriction(self):
        target_distribution = NChooserTargetedDistributionHIV(
            age_ranges_years=self.age_ranges_years,
            start_year=self.start_year,
            end_year=self.end_year,
            num_targeted_females=self.num_targeted_females,
            num_targeted_males=self.num_targeted_males,
            property_restrictions=PropertyRestrictions(individual_property_restrictions=[["Risk:HIGH"]])
        )
        self.assertIsInstance(target_distribution, NChooserTargetedDistributionHIV)
        distribution = target_distribution.to_schema_dict(self.campaign_obj)
        self.assertIsInstance(distribution, s2c.ReadOnlyDict)
        self.assertListEqual(distribution.Age_Ranges_Years, self.expected_age_ranges)
        self.assertListEqual(distribution.Num_Targeted_Males, [0, 8064.777513, 25054.39959, 179.0207223])
        self.assertListEqual(distribution.Num_Targeted_Females, [0, 0, 0, 0])
        self.assertListEqual(distribution.Num_Targeted, [])
        self.assertEqual(distribution.Start_Year, self.start_year)
        self.assertEqual(distribution.End_Year, self.end_year)
        self.assertEqual(distribution.Target_Disease_State, [])
        self.assertEqual(distribution.Target_Disease_State_Has_Intervention_Name, "")
        self.assertEqual(distribution.Property_Restrictions_Within_Node, [{"Risk": "HIGH"}])

    def test_num_targeted(self):
        target_distribution = NChooserTargetedDistributionHIV(
            age_ranges_years=self.age_ranges_years,
            start_year=self.start_year,
            end_year=self.end_year,
            num_targeted=self.num_targeted_males)
        self.assertIsInstance(target_distribution, NChooserTargetedDistributionHIV)
        distribution = target_distribution.to_schema_dict(self.campaign_obj)
        self.assertIsInstance(distribution, s2c.ReadOnlyDict)
        self.assertListEqual(distribution.Age_Ranges_Years, self.expected_age_ranges)
        self.assertListEqual(distribution.Num_Targeted, [0, 8064.777513, 25054.39959, 179.0207223])
        self.assertListEqual(distribution.Num_Targeted_Males, [])
        self.assertListEqual(distribution.Num_Targeted_Females, [])
        self.assertEqual(distribution.Start_Year, self.start_year)
        self.assertEqual(distribution.End_Year, self.end_year)

    def test_with_disease_state_exception_no_intervention_name(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=self.num_targeted_females,
                num_targeted_males=self.num_targeted_males,
                target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.HAS_INTERVENTION]]
            )
        self.assertTrue("you must also define 'target_disease_state_has_intervention_name'" in str(context.exception))

    def test_with_disease_state_exception_invalid_disease_state(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=self.num_targeted_females,
                num_targeted_males=self.num_targeted_males,
                target_disease_state=[['Received_Positive_Results']]
            )
        self.assertTrue("Invalid target_disease_state" in str(context.exception))

    def test_with_property_restriction_exception_node(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=self.num_targeted_females,
                num_targeted_males=self.num_targeted_males,
                property_restrictions=PropertyRestrictions(node_property_restrictions=[["Place:URBAN"]])
            )
        self.assertTrue("property_restrictions should have only individual property restrictions." in str(context.exception))

    def test_exception_num_targeted(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=[],
                num_targeted_males=self.num_targeted_males
            )
        self.assertTrue("Either num_targeted or num_targeted_male and num_targeted_females should be provided." in str(context.exception))

    def test_exception_invalid_length(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=[1, 2, 3],
                num_targeted_males=[3, 4, 5]
            )
        self.assertTrue("num_targeted_males and num_targeted_females should have the same length as age ranges." in
                        str(context.exception))

    def test_exception_overlapping_age_ranges(self):
        with self.assertRaises(ValueError) as context:
            age_ranges_years = [
                [0, 1, 10, 25],  # Min ages
                [0.99999, 14.9999999, 49.9999, 64.9999]  # Max ages
            ]
            NChooserTargetedDistributionHIV(
                age_ranges_years=age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=self.num_targeted_females,
                num_targeted_males=self.num_targeted_males
            )
        self.assertTrue("Your age ranges are overlapping" in str(context.exception))

    def test_exception_invalid_age_max(self):
        with self.assertRaises(ValueError) as context:
            age_ranges_years = [
                [0, 1, 50, 55],  # Min ages
                [0.99999, 14.9999999, 49.9999, 64.9999]  # Max ages
            ]
            NChooserTargetedDistributionHIV(
                age_ranges_years=age_ranges_years,
                start_year=self.start_year,
                end_year=self.end_year,
                num_targeted_females=self.num_targeted_females,
                num_targeted_males=self.num_targeted_males
            )
        self.assertTrue("should be larger than min age" in str(context.exception))

    def test_exception_invalid_start_year(self):
        with self.assertRaises(ValueError) as context:
            NChooserTargetedDistributionHIV(
                age_ranges_years=self.age_ranges_years,
                start_year=2010.0,
                end_year=2009.999,
                num_targeted_males=self.num_targeted_males,
                num_targeted_females=self.num_targeted_females
            )
        self.assertTrue("should be less than end_year" in str(context.exception))


@pytest.mark.unit
class TestValueMap(unittest.TestCase):
    def setUp(self):
        self.campaign_obj = campaign
        self.campaign_obj.set_schema(manifest.schema_path)
        print(f"running test: {self._testMethodName}:")

    def test_value_map(self):
        value_map = ValueMap([1995, 2005], [10, 20])
        self.assertEqual(value_map.to_schema_dict(self.campaign_obj), {"Times": [1995, 2005], "Values": [10, 20]})


@pytest.mark.unit
class TestCommonInterventionParameters(unittest.TestCase):
    def setUp(self):
        print(f"running test: {self._testMethodName}:")

    def test_init_default(self):
        common_intervention_parameters = CommonInterventionParameters()
        self.assertEqual(common_intervention_parameters.intervention_name, None)
        self.assertEqual(common_intervention_parameters.cost, None)
        self.assertEqual(common_intervention_parameters.disqualifying_properties, None)
        self.assertEqual(common_intervention_parameters.new_property_value, None)
        self.assertEqual(common_intervention_parameters.dont_allow_duplicates, None)

    def test_init(self):
        common_intervention_parameters = CommonInterventionParameters(intervention_name="Intervention1", cost=100,
                                                                      disqualifying_properties=["Risk:HIGH", "Place:URBAN"],
                                                                      new_property_value="Risk:HIGH",
                                                                      dont_allow_duplicates=True)
        self.assertEqual(common_intervention_parameters.intervention_name, "Intervention1")
        self.assertEqual(common_intervention_parameters.cost, 100)
        self.assertEqual(common_intervention_parameters.disqualifying_properties, ["Risk:HIGH", "Place:URBAN"])
        self.assertEqual(common_intervention_parameters.new_property_value, "Risk:HIGH")
        self.assertEqual(common_intervention_parameters.dont_allow_duplicates, True)


if __name__ == '__main__':
    unittest.main()
