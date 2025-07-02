import os.path
import unittest
import pytest
import json
import difflib
import math
import pandas as pd
import sys
from pathlib import Path

from emodpy_hiv.campaign.cascade_of_care import CascadeState
from emodpy_hiv.campaign.cascade_of_care import timestep_from_year
from emodpy_hiv.campaign.cascade_of_care import convert_time_value_map
from emodpy_hiv.campaign.cascade_of_care import all_negative_time_value_map
from emodpy_hiv.campaign.cascade_of_care import add_state_TestingOnSymptomatic
from emodpy_hiv.campaign.cascade_of_care import add_state_ARTStagingDiagnosticTest
from emodpy_hiv.campaign.cascade_of_care import add_state_ARTStaging
from emodpy_hiv.campaign.cascade_of_care import add_state_LinkingToPreART
from emodpy_hiv.campaign.cascade_of_care import add_state_OnPreART
from emodpy_hiv.campaign.cascade_of_care import add_state_LinkingToART
from emodpy_hiv.campaign.cascade_of_care import add_state_OnART
from emodpy_hiv.campaign.cascade_of_care import add_state_LostForever
from emodpy_hiv.campaign.cascade_of_care import add_state_HCTUptakeAtDebut
from emodpy_hiv.campaign.cascade_of_care import add_state_HCTUptakePostDebut
from emodpy_hiv.campaign.cascade_of_care import add_state_HCTTestingLoop
from emodpy_hiv.campaign.cascade_of_care import add_state_TestingOnANC
from emodpy_hiv.campaign.cascade_of_care import add_state_TestingOnChild6w
from emodpy_hiv.campaign.cascade_of_care import add_post_debut_coinfection
from emodpy_hiv.campaign.cascade_of_care import add_csw
from emodpy_hiv.campaign.cascade_of_care import add_traditional_male_circumcision
from emodpy_hiv.campaign.cascade_of_care import add_vmmc_reference_tracking
from emodpy_hiv.campaign.cascade_of_care import add_health_care_testing
from emodpy_hiv.campaign.cascade_of_care import add_pmtct
from emodpy_hiv.campaign.cascade_of_care import seed_infections
from emodpy_hiv.campaign.cascade_of_care import add_historical_vmmc_nchooser
from emodpy_hiv.campaign.cascade_of_care import add_ART_cascade

manifest_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(manifest_directory))
import manifest

from emodpy_hiv.campaign.common import TargetGender


from emod_api import campaign as camp


NODE_SETS = {
    '1': [1],
    '2': [2],
    '3': [3],
    '4': [4],
    '5': [5],
    '6': [6],
    '7': [7],
    '8': [8],
    '9': [9],
    '10': [10],
    'NODE_SET_1': [1, 2, 3, 7, 9],
    'NODE_SET_2': [4, 5, 6, 8, 10],
    'NODE_SET_3': [1, 2, 3, 4, 6, 7],
    'NODE_SET_4': [5, 9, 10],
    'NODE_SET_5': [8],
    'All': None
}

current_folder = os.path.dirname(os.path.abspath(__file__))
regression_folder = os.path.join(current_folder, 'regression_files')
output_folder = os.path.join(current_folder, 'coc_output')

@pytest.mark.unit
class TestCampaignMethods(unittest.TestCase):
    def setUp(self):
        print(f"running test: {self._testMethodName}:")

    def test_timestep_from_year(self):
        self.assertEqual(timestep_from_year(1991, 1990), 365)
        self.assertEqual(timestep_from_year(1990, 1990), 0)
        self.assertEqual(timestep_from_year(1989, 1990), -365)  # exception
        self.assertEqual(timestep_from_year(2016.5, 2016), 182)

    def test_convert_time_value_map(self):
        self.assertEqual(convert_time_value_map({"Times": [1990, 2016], "Values": [0, 0]}), {1990: 0, 2016: 0})
        self.assertEqual(convert_time_value_map({"Times": [2000, 2010], "Values": [1, 0.5]}), {2000: 1, 2010: 0.5})


@pytest.mark.unit
class TestAddStateFunctions(unittest.TestCase):
    is_debugging = False

    @classmethod
    def setUpClass(cls):
        cls.camp = camp
        cls.camp.schema_path = manifest.schema_path
        cls.camp.base_year = 1960.5
        cls.art_cascade_start_year = 1990
        cls.output_dir = output_folder
        if not os.path.isdir(cls.output_dir):
            # shutil.rmtree(cls.output_dir)
            os.makedirs(cls.output_dir)

    def setUp(self):
        self.camp.reset()
        self.output_filename = None
        print(f"running test: {self._testMethodName}:")

    def tearDown(self):
        if self.output_filename and os.path.exists(self.output_filename) and not self.is_debugging:
            os.remove(self.output_filename)

    def save_json_with_expected_exception(self, file_name):
        file_path = os.path.join(self.output_dir, f'{file_name}.json')
        self.output_filename = file_path
        if os.path.isfile(file_path):
            os.remove(file_path)
        try:
            self.camp.save(os.path.join(file_path))
        except Exception as e:
            assert isinstance(e, RuntimeError), "Exception is not a RuntimeError"
            assert str(e) == 'Please fix above error.', "Exception message does not match 'Please fix above error.'"

    def save_json_no_exception(self, file_name):
        file_path = os.path.join(self.output_dir, f'{file_name}.json')
        if os.path.isfile(file_path):
            os.remove(file_path)
        self.camp.save(os.path.join(file_path))
        self.output_filename = file_path

    def compare_json(self, json1, json2):
        if type(json1) != type(json2): # noqa: E721
            return False

        if isinstance(json1, dict):
            if set(json1.keys()) != set(json2.keys()):
                return False
            return all(self.compare_json(json1[key], json2[key]) for key in json1.keys())

        if isinstance(json1, list):
            if len(json1) != len(json2):
                return False
            return all(self.compare_json(item1, item2) for item1, item2 in zip(json1, json2))

        if isinstance(json1, float):
            return math.isclose(json1, json2, rel_tol=1e-7)

        return json1 == json2

    def compare_json_files(self, file_name: str):
        test_file = os.path.join(self.output_dir, f'{file_name}.json')
        regression_file = os.path.join(regression_folder, f'{file_name}.json')
        with open(test_file) as f1, open(regression_file) as f2:
            test_json = json.load(f1)
            regression_json = json.load(f2)

        if not self.compare_json(test_json, regression_json):
            print("The JSON files are not the same.")
            with open(test_file) as f1, open(regression_file) as f2:
                diff = difflib.unified_diff(
                    f1.readlines(),
                    f2.readlines(),
                    fromfile='test_file',
                    tofile='regression_file',
                )
                for line in diff:
                    print(line)
            return False
        else:
            print("The JSON files are the same.")
            return True

    def test_add_state_TestingOnSymptomatic(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART]

        disqualifying_properties_plus_art_staging = disqualifying_properties + [CascadeState.ART_STAGING]

        add_state_TestingOnSymptomatic(campaign=self.camp,
                                       node_ids=None,
                                       disqualifying_properties=disqualifying_properties_plus_art_staging,
                                       start_year=self.art_cascade_start_year,
                                       tvmap_increased_symptomatic_presentation=all_negative_time_value_map)
        file_name = 'TestingOnSymptomatic'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_ARTStagingDiagnosticTest(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART]
        add_state_ARTStagingDiagnosticTest(campaign=self.camp,
                                           node_ids=None,
                                           disqualifying_properties=disqualifying_properties,
                                           start_year=self.art_cascade_start_year)
        file_name = 'ARTStagingDiagnosticTest'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_ARTStaging(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART]
        art_cascade_pre_staging_retention: float = 0.85
        art_cascade_cd4_retention_rate: float = 1
        add_state_ARTStaging(campaign=self.camp,
                             cd4_retention_rate=art_cascade_cd4_retention_rate,
                             pre_staging_retention=art_cascade_pre_staging_retention,
                             node_ids=None,
                             disqualifying_properties=disqualifying_properties,
                             start_year=self.art_cascade_start_year)
        file_name = 'ARTStaging'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_LinkingToPreART(self):
        disqualifying_properties_pre_art_linking = [CascadeState.LOST_FOREVER,
                                                    CascadeState.ON_ART,
                                                    CascadeState.LINKING_TO_ART,
                                                    CascadeState.ON_PRE_ART]
        add_state_LinkingToPreART(campaign=self.camp,
                                  node_ids=None,
                                  disqualifying_properties=disqualifying_properties_pre_art_linking,
                                  start_year=self.art_cascade_start_year)
        file_name = 'LinkingToPreART'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_OnPreART(self):
        disqualifying_properties_pre_art = [CascadeState.LOST_FOREVER,
                                            CascadeState.ON_ART,
                                            CascadeState.LINKING_TO_ART]
        art_cascade_pre_art_retention: float = 0.75
        add_state_OnPreART(campaign=self.camp,
                           node_ids=None,
                           pre_art_retention=art_cascade_pre_art_retention,
                           disqualifying_properties=disqualifying_properties_pre_art,
                           start_year=self.art_cascade_start_year)
        file_name = 'OnPreART'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_LinkingToART(self):
        art_linking_disqualifying_properties = [CascadeState.LOST_FOREVER, CascadeState.ON_ART]
        add_state_LinkingToART(campaign=self.camp,
                               node_ids=None,
                               disqualifying_properties=art_linking_disqualifying_properties,
                               start_year=self.art_cascade_start_year)
        file_name = 'LinkingToART'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_OnART(self):
        disqualifying_properties_art = [CascadeState.LOST_FOREVER]
        art_cascade_immediate_art_rate: float = 0.1
        art_cascade_art_reenrollment_willingness: float = 0.9
        add_state_OnART(campaign=self.camp,
                        art_reenrollment_willingness=art_cascade_art_reenrollment_willingness,
                        immediate_art_rate=art_cascade_immediate_art_rate,
                        node_ids=None,
                        disqualifying_properties=disqualifying_properties_art,
                        start_year=self.art_cascade_start_year,
                        tvmap_immediate_ART_restart=all_negative_time_value_map,
                        tvmap_reconsider_lost_forever=all_negative_time_value_map)
        file_name = 'OnART'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_LostForever(self):
        add_state_LostForever(campaign=self.camp, node_ids=None, start_year=self.art_cascade_start_year)
        file_name = 'LostForever'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_HCTUptakeAtDebut(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART,
                                    CascadeState.ART_STAGING]

        add_state_HCTUptakeAtDebut(campaign=self.camp,
                                   disqualifying_properties=disqualifying_properties,
                                   node_ids=None,
                                   start_year=self.art_cascade_start_year)
        file_name = 'HCTUptakeAtDebut'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_HCTUptakePostDebut(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART,
                                    CascadeState.ART_STAGING]
        hct_reentry_rate = 1
        add_state_HCTUptakePostDebut(campaign=self.camp,
                                     disqualifying_properties=disqualifying_properties,
                                     node_ids=None,
                                     hct_reentry_rate=hct_reentry_rate,
                                     start_year=self.art_cascade_start_year,
                                     tvmap_test_for_enter_HCT_testing_loop=all_negative_time_value_map)
        file_name = 'HCTUptakePostDebut'
        self.save_json_with_expected_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_HCTTestingLoop(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART,
                                    CascadeState.ART_STAGING]
        hct_retention_rate = 0.95
        hct_delay_to_next_test = [730, 365, 1100]
        hct_delay_to_next_test_node_ids = [[1, 2, 3, 4, 6, 7], [5, 9, 10], [8]]
        hct_delay_to_next_test_node_names = ['Default', 'Lusaka, Southern, Western', 'Northern']
        add_state_HCTTestingLoop(campaign=self.camp,
                                 disqualifying_properties=disqualifying_properties,
                                 hct_delay_to_next_test=hct_delay_to_next_test,
                                 node_ids=None,
                                 hct_retention_rate=hct_retention_rate,
                                 start_year=self.art_cascade_start_year,
                                 tvmap_consider_immediate_ART=all_negative_time_value_map,
                                 hct_delay_to_next_test_node_ids=hct_delay_to_next_test_node_ids,
                                 hct_delay_to_next_test_node_names=hct_delay_to_next_test_node_names)
        file_name = 'HCTTestingLoop'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_state_TestingOnANC(self):
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART,
                                    CascadeState.ART_STAGING,
                                    CascadeState.TESTING_ON_SYMPTOMATIC]
        property_restrictions = 'Accessibility:Yes'
        pmtct_coverage = 1.0
        pmtct_sigmoid_min = 0
        pmtct_sigmoid_max = 0.975
        pmtct_sigmoid_midyear = 2005.87
        pmtct_sigmoid_rate = 0.7136
        pmtct_link_to_ART_rate = 0.8
        treatment_a_efficacy = 0.9
        treatment_b_efficacy = 0.96667
        sdNVP_efficacy = 0.66

        add_state_TestingOnANC(campaign=self.camp,
                               disqualifying_properties=disqualifying_properties,
                               coverage=pmtct_coverage,
                               link_to_ART_rate=pmtct_link_to_ART_rate,
                               node_ids=None,
                               sigmoid_min=pmtct_sigmoid_min,
                               sigmoid_max=pmtct_sigmoid_max,
                               sigmoid_midyear=pmtct_sigmoid_midyear,
                               sigmoid_rate=pmtct_sigmoid_rate,
                               treatment_a_efficacy=treatment_a_efficacy,
                               treatment_b_efficacy=treatment_b_efficacy,
                               sdNVP_efficacy=sdNVP_efficacy,
                               start_year=self.art_cascade_start_year,
                               property_restrictions=property_restrictions)
        file_name = 'TestingOnANC'
        self.save_json_no_exception('TestingOnANC')
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_TestingOnChild6w(self):
        child_testing_start_year = 2004
        property_restrictions = 'Accessibility:Yes'
        pmtct_child_testing_time_value_map = {"Times": [2004, 2005, 2006, 2008, 2009], "Values": [0, 0.03, 0.1, 0.2, 0.3365]}
        disqualifying_properties = [CascadeState.LOST_FOREVER,
                                    CascadeState.ON_ART,
                                    CascadeState.LINKING_TO_ART,
                                    CascadeState.ON_PRE_ART,
                                    CascadeState.LINKING_TO_PRE_ART,
                                    CascadeState.ART_STAGING,
                                    CascadeState.TESTING_ON_SYMPTOMATIC]
        add_state_TestingOnChild6w(campaign=self.camp,
                                   start_year=child_testing_start_year,
                                   disqualifying_properties=disqualifying_properties,
                                   time_value_map=pmtct_child_testing_time_value_map,
                                   node_ids=None,
                                   property_restrictions=property_restrictions)
        file_name = 'TestingOnChild6w'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_post_debut_coinfection(self):
        coinfection_high_risk_coverage = 0.3
        coinfection_medium_risk_coverage = 0.3
        coinfection_low_risk_coverage = 0.1
        target_gender = TargetGender.ALL
        add_post_debut_coinfection(campaign=self.camp,
                                   coinfection_coverage=coinfection_high_risk_coverage,
                                   coinfection_gender=target_gender,
                                   coinfection_IP='Risk:HIGH')
        add_post_debut_coinfection(campaign=self.camp,
                                   coinfection_coverage=coinfection_medium_risk_coverage,
                                   coinfection_gender=target_gender,
                                   coinfection_IP='Risk:MEDIUM')
        add_post_debut_coinfection(campaign=self.camp,
                                   coinfection_coverage=coinfection_low_risk_coverage,
                                   coinfection_gender=target_gender,
                                   coinfection_IP='Risk:LOW')
        file_name = 'STI-co'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_csw(self):
        csw_male_uptake_coverage_nodeset1 = 0.195
        csw_female_uptake_coverage_nodeset1 = 0.125
        csw_male_uptake_coverage_nodeset2 = 0.0781
        csw_female_uptake_coverage_nodeset2 = 0.05
        add_csw(campaign=self.camp,
                node_ids=NODE_SETS['NODE_SET_1'],
                male_uptake_coverage=csw_male_uptake_coverage_nodeset1,
                female_uptake_coverage=csw_female_uptake_coverage_nodeset1)
        add_csw(campaign=self.camp,
                node_ids=NODE_SETS['NODE_SET_2'],
                male_uptake_coverage=csw_male_uptake_coverage_nodeset2,
                female_uptake_coverage=csw_female_uptake_coverage_nodeset2)
        file_name = 'CSW'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_traditional_male_circumcision(self):
        traditional_male_circumcision_reduced_acquire = 0.6
        coverages = [0.054978651, 0.139462861, 0.028676043, 0.091349358, 0.12318707, 0.039308099, 0.727917322,
                     0.041105263, 0.044388102, 0.398239794]
        for i in range(len(coverages)):
            add_traditional_male_circumcision(campaign=self.camp,
                                              traditional_male_circumcision_node_ids=NODE_SETS[f'{i + 1}'],
                                              traditional_male_circumcision_reduced_acquire=traditional_male_circumcision_reduced_acquire,
                                              traditional_male_circumcision_coverage=coverages[i])

        file_name = 'Traditional_male_circumcision'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_vmmc_reference_tracking(self):
        vmmc_reference_tracking_time_value_map = {"Times": [2015.9999, 2016, 2021],
                                                  "Values": [0, 0.54, 0.9]}
        add_vmmc_reference_tracking(campaign=self.camp,
                                    vmmc_time_value_map=vmmc_reference_tracking_time_value_map)
        file_name = 'VMMC_reference_tracking'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_cascade_of_care(self):
        add_ART_cascade(campaign=self.camp)
        file_name = 'cascade_of_care'
        self.save_json_no_exception(file_name)
        # the regression file is tested in the previous individual add_state_** tests

    def test_add_health_care_testing(self):
        add_health_care_testing(campaign=self.camp)
        file_name = 'health_care_testing'
        self.save_json_with_expected_exception(file_name)
        # the regression file is tested in the previous individual add_state_** tests

    def test_add_pmtct(self):
        child_testing_time_value_map = {"Times": [2004, 2005, 2006, 2008, 2009],
                                        "Values": [0, 0.03, 0.1, 0.2, 0.3365]}
        add_pmtct(campaign=self.camp, child_testing_time_value_map=child_testing_time_value_map)
        file_name = 'pmtct'
        self.save_json_no_exception(file_name)
        # the regression file is tested in the previous individual add_state_** tests

    def test_seed_infection(self):
        seeding_target_gender = TargetGender.ALL
        seeding_target_property_restrictions = ["Risk:HIGH"]

        seed_infections(campaign=self.camp,
                        seeding_node_ids=NODE_SETS['All'],
                        seeding_start_year=1982,
                        seeding_coverage=0.1,
                        seeding_target_min_age=0,
                        seeding_target_max_age=200,
                        seeding_target_gender=seeding_target_gender,
                        seeding_target_property_restrictions=seeding_target_property_restrictions)
        file_name = 'seed_infection'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')

    def test_add_historical_vmmc_nchooser(self):
        data = {'year': [2010, 2010, 2011, 2011],
                'min_age': [1, 15, 1, 15],
                'max_age': [14.999, 49.999, 14.999, 49.999],
                'n_circumcisions': [200, 1300, 290, 1490]}
        historical_vmmc_distributions_by_time = pd.DataFrame.from_dict(data)
        add_historical_vmmc_nchooser(campaign=self.camp, historical_vmmc_distributions_by_time=historical_vmmc_distributions_by_time)
        file_name = 'historical_vmmc_nchooser'
        self.save_json_no_exception(file_name)
        self.assertTrue(self.compare_json_files(file_name), f'{file_name}.json is not the same as the regression file.')


if __name__ == '__main__':
    unittest.main()
