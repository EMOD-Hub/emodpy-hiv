import unittest
import pytest
from typing import List
from pathlib import Path
import sys
import json
import os

from emodpy_hiv.countries.zambia import Zambia
from emod_api import campaign as api_campaign
from emodpy_hiv.campaign import cascade_of_care as coc
from emodpy_hiv.campaign.common import TargetGender
from emodpy_hiv.parameterized_call import ParameterizedCall


manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
import helpers


class CountrySubClass(Zambia):
    """
    This is a class used for testing the Country class in the emodpy_hiv package.
    """
    country_name = "CountrySubClass"

    @classmethod
    def add_seed_infections_parameterized_calls(cls) -> List[ParameterizedCall]:
        """
        Override the default method to have two outbreak individual interventions with
        coverage 0.1 in Risk:HIGH poeple for all nodes, but one is for everyone while
        the other is for Male individuals aged 15-24.
        """
        parameterized_calls = []

        # add outbreak individual interventions with coverage 0.1 to all nodes with Risk:HIGH
        hp = {'seeding_start_year': 1982, 'seeding_coverage': 0.1}
        nhp = {}
        pc = ParameterizedCall(func=cls.seed_infections,
                                non_hyperparameters=nhp,
                                hyperparameters=hp,
                                label="_1")
        parameterized_calls.append(pc)
        
        # add outbreak individual interventions with coverage 0.1 to all nodes with Risk:HIGH
        # and Male individuals aged 15-24.
        hp = {'seeding_start_year': 1981, 'seeding_coverage': 0.1}
        nhp = {'seeding_target_gender': TargetGender.MALE,
               'seeding_target_min_age': 15,
               'seeding_target_max_age': 24}
        pc = ParameterizedCall(func=cls.seed_infections,
                                non_hyperparameters=nhp,
                                hyperparameters=hp,
                                label="_2")
        parameterized_calls.append(pc)

        return parameterized_calls

    @classmethod
    def add_state_LinkingToART(cls,
                               campaign: api_campaign,
                               start_year: float,
                               sigmoid_min: float = 0.0,
                               sigmoid_max: float = 0.8507390283,
                               sigmoid_midyear: float = 1997.4462231708,
                               sigmoid_rate: float = 1.0,
                               node_ids: List[int] = None):
        """
        Override the default LinkingToART state to have a ramp_max of 0.95 and ramp_midyear of 2004.
        """
        node_ids = None
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER, coc.CascadeState.ON_ART]
        coc.add_state_LinkingToART(campaign=campaign,
                                   node_ids=node_ids,
                                   disqualifying_properties=disqualifying_properties,
                                   start_year=start_year,
                                   sigmoid_min=sigmoid_min,
                                   sigmoid_max=0.95,
                                   sigmoid_midyear=2004,
                                   sigmoid_rate=sigmoid_rate)


@pytest.mark.unit
class TestCountrySubClass(unittest.TestCase):
    def setUp(self):
        self.country_subclass = CountrySubClass
        self.country_subclass.base_year = 1960.5

        output_path = Path(__file__).parent.joinpath("outputs")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            
        print(f"running test: {self._testMethodName}")

    def tearDown(self):
        pass

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def count_string_in_json(self, obj, target_string):
        """Recursively count occurrences of target_string in the JSON object."""
        count = 0

        if isinstance(obj, dict):
            for key, value in obj.items():
                count += self.count_string_in_json(key, target_string)
                count += self.count_string_in_json(value, target_string)
        elif isinstance(obj, list):
            for item in obj:
                count += self.count_string_in_json(item, target_string)
        elif isinstance(obj, str):
            if obj == target_string:
                count += 1

        return count

    def search_key_value_pair(self, json_obj, target_key, target_value):
        """Recursively search for a key-value pair in the JSON object."""
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == target_key and value == target_value:
                    return True
                if self.search_key_value_pair(value, target_key, target_value):
                    return True
        elif isinstance(json_obj, list):
            for item in json_obj:
                if self.search_key_value_pair(item, target_key, target_value):
                    return True
        return False
    
    def test_country_subclass_build_campaign(self):
        fn_exp  = Path(__file__).parent.joinpath('inputs', 'test_country_subclass_build_campaign_expected.json')
        fn_act  = Path(__file__).parent.joinpath('outputs', 'test_country_subclass_build_campaign_actual.json')

        api_campaign.schema_path = manifest.schema_path
        camp = self.country_subclass.build_campaign(campaign=api_campaign)
        camp.save(fn_act)

        json_exp = self.load_json(fn_exp)
        json_act = self.load_json(fn_act)

        self.assertDictEqual(json_exp, json_act,
                             f"The {fn_act} did not match the"
                             f" {fn_exp} file.")
        helpers.delete_existing_file(fn_act)

    def test_override_seed_infections(self):
        fn_zambia  = Path(__file__).parent.joinpath('outputs', 'zambia_campaign_2.json')
        fn_subclass  = Path(__file__).parent.joinpath('outputs', 'country_subclass_campaign_2.json')

        zambia = Zambia
        api_campaign.schema_path = manifest.schema_path
        zambia_campaign = zambia.build_campaign(campaign=api_campaign)
        zambia_campaign.save(fn_zambia)

        country_subclass = CountrySubClass
        country_subclass_campaign = country_subclass.build_campaign(campaign=api_campaign)
        country_subclass_campaign.save(fn_subclass)

        zambia_json = self.load_json(fn_zambia)
        country_subclass_json = self.load_json(fn_subclass)

        # Assert that the campaigns are not the same
        self.assertNotEqual(zambia_json, country_subclass_json, "The campaigns are the same, but they should not be.")

        # Assert the number of OutbreakIndividuals in the campaigns
        outbreak_count_country_subclass = self.count_string_in_json(country_subclass_json, "OutbreakIndividual")
        self.assertEqual(outbreak_count_country_subclass, 2, "The country_subclass campaign should contain 2 instances of 'OutbreakIndividual'.")
        outbreak_count_zambia = self.count_string_in_json(zambia_json, "OutbreakIndividual")
        self.assertEqual(outbreak_count_zambia, 10, "The zambia campaign should contain 10 instances of 'OutbreakIndividual'.")

        helpers.delete_existing_file(fn_zambia)
        helpers.delete_existing_file(fn_subclass)

    def test_override_add_state_LinkingToART(self):
        country_subclass = CountrySubClass
        api_campaign.schema_path = manifest.schema_path
        country_subclass_campaign = country_subclass.build_campaign(campaign=api_campaign)
        self.assertTrue(self.search_key_value_pair(country_subclass_campaign.campaign_dict, "Ramp_Max", 0.95),
                        'The campaign should contain a HIVSigmoidByYearAndSexDiagnostic with "Ramp_Max": 0.95')
        self.assertTrue(self.search_key_value_pair(country_subclass_campaign.campaign_dict, "Ramp_MidYear", 2004),
                        'The campaign should contain a HIVSigmoidByYearAndSexDiagnostic with "Ramp_MidYear": 2004')
        self.assertFalse(self.search_key_value_pair(country_subclass_campaign.campaign_dict, "Ramp_Max", 0.8507390283),
                         'The campaign should not contain a HIVSigmoidByYearAndSexDiagnostic with "Ramp_Max": 0.8507390283')
        self.assertFalse(self.search_key_value_pair(country_subclass_campaign.campaign_dict, "Ramp_MidYear", 1997.4462231708),
                         'The campaign should not contain a HIVSigmoidByYearAndSexDiagnostic with "Ramp_MidYear": 1997.4462231708')


if __name__ == '__main__':
    unittest.main()
