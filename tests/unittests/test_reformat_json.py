import unittest

from pathlib import Path
import json
import sys
import os

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

import emodpy_hiv.countries.converting.reformat_json as rj

class TestReformatJson(unittest.TestCase):
    def setUp(self):
        self.output_filename = Path(__file__).parent.joinpath('outputs/test_reformat_json_actual.json')
        print(f"running test: {self._testMethodName}")

    def tearDown(self):
        if self.output_filename and os.path.exists(self.output_filename):
            os.remove(self.output_filename)

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def test_reformat_json(self):
        filename_to_format = Path(__file__).parent.joinpath('inputs/test_reformat_json_to_format.json')
        filename_to_expect = Path(__file__).parent.joinpath('inputs/test_reformat_json_to_expect.json')

        rj.format_sort_round_json(filename_to_format, self.output_filename)

        act_json = self.load_json(self.output_filename)
        exp_json = self.load_json(filename_to_expect)

        # erase the date so we don't compare that
        if "Metadata" in exp_json.keys():
            exp_json["Metadata"] = {}
            act_json["Metadata"] = {}

        self.assertDictEqual(exp_json, act_json)


if __name__ == '__main__':
    unittest.main()
