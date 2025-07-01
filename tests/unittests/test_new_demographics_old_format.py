import unittest

from pathlib import Path
import json
import sys
import os

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

import emodpy_hiv.countries.converting.new_demographics_old_format as ndof

class TestNewDemographicsOldFormat(unittest.TestCase):
    def setUp(self):
        self.output_dir = Path(__file__).parent.joinpath('outputs')
        print(f"running test: {self._testMethodName}")

    def tearDown(self):
        old_filenames = ndof.get_old_demographic_filenames(add_extension=False)
        for old_name in old_filenames:
            act_path = self.output_dir.joinpath(old_name + "_actual.json")
            if os.path.exists(act_path):
                os.remove(act_path)
        return

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def test_new_demographics_old_format(self):
        input_dir  = Path(__file__).parent.joinpath('inputs/test_new_demographics_old_format')

        ndof.create_old_demographic_files(country_name="Zambia",
                                          output_dir=self.output_dir,
                                          suffix="actual")
        
        old_filenames = ndof.get_old_demographic_filenames(add_extension=False)
        for old_name in old_filenames:
            exp_path =       input_dir.joinpath(old_name + "_expected.json")
            act_path = self.output_dir.joinpath(old_name + "_actual.json")

            exp_json = self.load_json(exp_path)
            act_json = self.load_json(act_path)

            # erase the date so we don't compare that
            if "Metadata" in exp_json.keys():
                exp_json["Metadata"] = {}
                act_json["Metadata"] = {}

            self.assertDictEqual(exp_json, act_json, f"\nFailed comparing: {old_name}")


if __name__ == '__main__':
    unittest.main()
