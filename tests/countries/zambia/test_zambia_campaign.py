import unittest

from pathlib import Path
import sys
import json
import os

from emodpy_hiv.countries.zambia import Zambia
from emod_api import campaign as api_campaign


manifest_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(manifest_directory))

import manifest
import helpers


class TestZambia(unittest.TestCase):
    def setUp(self):
        output_path = Path(__file__).parent.joinpath("outputs")
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        print(f"running test: {self._testMethodName}")

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def test_zambia_build_campaign(self):
        filename_exp = Path(__file__).parent.joinpath('inputs', 'zambia_campaign_regression.json')
        filename_act = Path(__file__).parent.joinpath('outputs', "zambia_campaign.json")

        api_campaign.schema_path = manifest.schema_path
        camp = Zambia.build_campaign(campaign=api_campaign)
        camp.save(filename_act)

        zambia_regression_json = self.load_json(filename_exp)
        zambia_json = self.load_json(filename_act)

        # Assert that the campaigns match the regression file
        self.assertDictEqual(zambia_regression_json, zambia_json,
                             "The campaign did not match the regression file.")
        helpers.delete_existing_file(filename_act)


if __name__ == '__main__':
    unittest.main()
