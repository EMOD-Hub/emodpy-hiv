import unittest

from pathlib import Path
import sys
import json
import os

from emodpy_hiv.countries.zambia import Zambia
from emodpy.emod_task import EMODTask

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

    def tearDown(self):
        return

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)


    def test_zambia_build_config(self):
        filename_exp = Path(__file__).parent.joinpath('inputs', 'zambia_config_expected.json')
        filename_act = Path(__file__).parent.joinpath('outputs', "zambia_config_act.json")

        # this is usually done by task inside from_defaults and then when creating the sim/experiment,
        # but we need to do this explicitly here
        default_config = EMODTask.build_default_config(schema_path=manifest.schema_path)
        config = Zambia.build_config(default_config)
        config.parameters.to_file(filename_act)

        zambia_regression_json = self.load_json(filename_exp)
        zambia_json = self.load_json(filename_act)

        # Assert that the campaigns match the regression file
        self.assertDictEqual(zambia_regression_json, zambia_json,
                             f"The {filename_act} did not match the"
                             f" {filename_exp} file.")
        helpers.delete_existing_file(filename_act)


if __name__ == '__main__':
    unittest.main()
