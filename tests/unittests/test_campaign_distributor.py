import unittest
import pytest
import pandas as pd
import json
import os
from emod_api import campaign as api_campaign
from emodpy_hiv.campaign.individual_intervention import MaleCircumcision
from emodpy_hiv.campaign.distributor import (add_intervention_nchooser_df, _add_intervention_nchooser,
                                             add_intervention_reference_tracking)
from emodpy_hiv.campaign.common import (PropertyRestrictions, NChooserTargetedDistributionHIV, ValueMap,
                                        CommonInterventionParameters as CIP,
                                        TargetDemographicsConfig as TDC, TargetGender)
from emodpy_hiv.utils.targeting_config import IsCircumcised, HasIP
from emodpy_hiv.utils.emod_enum import TargetDiseaseState

from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
import helpers


@pytest.mark.unit
class TestDistributor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.campaign = api_campaign
        cls.current_directory = Path(__file__).resolve().parent
        cls.regression_folder = os.path.join(cls.current_directory, 'inputs', 'campaigns_distributor_regression')
        cls.output_folder = os.path.join(cls.current_directory, 'outputs', 'campaign_distributor')
        if not os.path.exists(cls.output_folder):
            os.makedirs(cls.output_folder, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        helpers.delete_existing_folder(path=cls.output_folder, must_be_empty=True)

    def setUp(self):
        self.campaign.set_schema(manifest.schema_path)
    
    def compare_to_regression_json(self, filename):
        regression_file = os.path.join(self.regression_folder, filename)
        campaign_file = os.path.join(self.output_folder, filename)
        self.campaign.save(campaign_file)
        # Make sure the campaign file match regression file.
        # Load the json files into dictionaries and compare them.
        with open(campaign_file, 'r') as f:
            output = json.load(f)
        with open(regression_file, 'r') as f:
            regression = json.load(f)
        self.assertDictEqual(output, regression,
                             f"Output does not match regression file, please check {campaign_file} and {regression_file}")
        helpers.delete_existing_file(campaign_file)

    def test_add_intervention_nchooser_df_default(self):
        intervention_list = [MaleCircumcision(self.campaign)]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted_male': [200, 1300, 290, 1490]
        })
        add_intervention_nchooser_df(self.campaign,
                                     intervention_list=intervention_list,
                                     distribution_df=distribution_df)
        self.compare_to_regression_json("add_intervention_nchooser_df_default.json")

    def test_add_intervention_nchooser_df_num_targeted(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted': [200, 1300, 290, 1490]
        })
        property_restrictions = PropertyRestrictions(individual_property_restrictions=[["Risk: High"]])
        target_disease_state = [[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]]
        event_name = "TestEvent"
        node_ids = [1, 2, 3]
        add_intervention_nchooser_df(self.campaign,
                                     intervention_list=intervention_list,
                                     distribution_df=distribution_df,
                                     property_restrictions=property_restrictions,
                                     target_disease_state=target_disease_state,
                                     target_disease_state_has_intervention_name=intervention_name,
                                     event_name=event_name,
                                     node_ids=node_ids)
        self.compare_to_regression_json("add_intervention_nchooser_df_num_targeted.json")

    def test_add_intervention_nchooser_df_num_targeted_male(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted_male': [200, 1300, 290, 1490]
        })
        property_restrictions = PropertyRestrictions(individual_property_restrictions=[["Risk: High"]])
        target_disease_state = [[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]]
        event_name = "TestEvent"
        node_ids = [1, 2, 3]
        add_intervention_nchooser_df(self.campaign,
                                     intervention_list=intervention_list,
                                     distribution_df=distribution_df,
                                     property_restrictions=property_restrictions,
                                     target_disease_state=target_disease_state,
                                     target_disease_state_has_intervention_name=intervention_name,
                                     event_name=event_name,
                                     node_ids=node_ids)
        self.compare_to_regression_json("add_intervention_nchooser_df_male.json")

    def test_add_intervention_nchooser_df_num_targeted_female(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted_female': [200, 1300, 290, 1490]
        })
        property_restrictions = PropertyRestrictions(individual_property_restrictions=[["Risk: High"]])
        target_disease_state = [[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]]
        event_name = "TestEvent"
        node_ids = [1, 2, 3]
        add_intervention_nchooser_df(self.campaign,
                                     intervention_list=intervention_list,
                                     distribution_df=distribution_df,
                                     property_restrictions=property_restrictions,
                                     target_disease_state=target_disease_state,
                                     target_disease_state_has_intervention_name=intervention_name,
                                     event_name=event_name,
                                     node_ids=node_ids)
        self.compare_to_regression_json("add_intervention_nchooser_df_female.json")

    def test_add_intervention_nchooser_df_num_targeted_two_genders(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted_female': [200, 1300, 290, 1490],
            'num_targeted_male': [1200, 300, 1290, 490]
        })
        property_restrictions = PropertyRestrictions(individual_property_restrictions=[["Risk: High"]])
        target_disease_state = [[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]]
        event_name = "TestEvent"
        node_ids = [1, 2, 3]
        add_intervention_nchooser_df(self.campaign,
                                     intervention_list=intervention_list,
                                     distribution_df=distribution_df,
                                     property_restrictions=property_restrictions,
                                     target_disease_state=target_disease_state,
                                     target_disease_state_has_intervention_name=intervention_name,
                                     event_name=event_name,
                                     node_ids=node_ids)
        self.compare_to_regression_json("add_intervention_nchooser_df_two_genders.json")

    def test_add_intervention_nchooser_df_exception(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999]
        })

        with self.assertRaises(ValueError) as context:
            add_intervention_nchooser_df(self.campaign,
                                         intervention_list=intervention_list,
                                         distribution_df=distribution_df)
        self.assertTrue("Expected at least one of these columns" in str(context.exception))

        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'num_targeted': [200, 1300, 290, 1490]
        })
        with self.assertRaises(ValueError) as context:
            add_intervention_nchooser_df(self.campaign,
                                         intervention_list=intervention_list,
                                         distribution_df=distribution_df)
        self.assertTrue("Expected these columns" in str(context.exception))

        distribution_df = pd.DataFrame({
            'year': [2010, 2010, 2011, 2011],
            'min_age': [1, 15, 1, 15],
            'max_age': [14.999, 49.999, 14.999, 49.999],
            'num_targeted': [200, 1300, 290, 1490],
            'num_targeted_male': [100, 300, 290, 400]
        })
        with self.assertRaises(ValueError) as context:
            add_intervention_nchooser_df(self.campaign,
                                         intervention_list=intervention_list,
                                         distribution_df=distribution_df)
        self.assertTrue("num_targeted column should not be used with num_targeted_female or num_targeted_male" in str(context.exception))

    def test_add_intervention_nchooser(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        targeted_distribution = NChooserTargetedDistributionHIV(
            age_ranges_years=[[0, 1, 15, 50], [0.9999999, 14.9999999, 49.9999999, 64.9999999]],
            start_year=2010,
            end_year=2011,
            num_targeted_males=[0, 8064, 25054, 179],
            num_targeted_females=[0, 0, 0, 0],
            target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION],
                                  [TargetDiseaseState.TESTED_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]],
            target_disease_state_has_intervention_name=intervention_name)

        _add_intervention_nchooser(self.campaign,
                                   intervention_list=intervention_list,
                                   targeted_distributions = [targeted_distribution],
                                   start_year=2010)
        self.compare_to_regression_json("add_intervention_nchooser.json")

    def test_add_intervention_reference_tracking_default(self):
        intervention_list = [MaleCircumcision(self.campaign)]
        time_value_map = ValueMap(times=[1960, 1961, 1962, 1963, 1964], values=[0.25, 0.375, 0.4, 0.4375, 0.46875])
        add_intervention_reference_tracking(api_campaign,
                                            intervention_list=intervention_list,
                                            time_value_map=time_value_map,
                                            tracking_config=IsCircumcised(),
                                            start_year=1955)
        self.compare_to_regression_json("add_intervention_reference_tracking_default.json")

    def test_add_intervention_reference_tracking(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        time_value_map = ValueMap(times=[1960, 1961, 1962, 1963, 1964], values=[0.25, 0.375, 0.4, 0.4375, 0.46875])
        add_intervention_reference_tracking(api_campaign,
                                            intervention_list=intervention_list,
                                            time_value_map=time_value_map,
                                            tracking_config=IsCircumcised(),
                                            start_year=1960,
                                            end_year=1965,
                                            update_period=182,
                                            target_demographics_config=TDC(target_gender=TargetGender.MALE,
                                                                           demographic_coverage=None),
                                            targeting_config=HasIP(ip_key_value="Risk:MEDIUM"))
        self.compare_to_regression_json("add_intervention_reference_tracking.json")

    def test_add_intervention_reference_tracking_exception(self):
        intervention_name = "MaleCircumcision"
        intervention_list = [MaleCircumcision(self.campaign,
                                              common_intervention_parameters=CIP(intervention_name=intervention_name))]
        time_value_map = ValueMap(times=[1960, 1961, 1962, 1963, 1964], values=[0.25, 0.375, 0.4, 0.4375, 0.46875])
        with self.assertWarns(UserWarning) as context:
            add_intervention_reference_tracking(api_campaign,
                                                intervention_list=intervention_list,
                                                time_value_map=time_value_map,
                                                tracking_config=IsCircumcised(),
                                                start_year=1960,
                                                end_year=1963)
        self.assertTrue("At least one year in the time_value_map is not be within the start_year and end_year." in
                        str(context.warning))

        with self.assertRaises(ValueError) as context:
            add_intervention_reference_tracking(api_campaign,
                                                intervention_list=intervention_list,
                                                time_value_map=time_value_map,
                                                tracking_config=IsCircumcised(),
                                                start_year=1965,
                                                end_year=1970)
        self.assertTrue("All years in the time_value_map is not within the start_year and end_year." in str(context.exception))

        with self.assertRaises(ValueError) as context:
            add_intervention_reference_tracking(api_campaign,
                                                intervention_list=intervention_list,
                                                time_value_map=time_value_map,
                                                tracking_config=IsCircumcised(),
                                                start_year=1965,
                                                end_year=1960)
        self.assertTrue("The end_year should be greater than the start_year" in str(context.exception))


if __name__ == '__main__':
    unittest.main()
