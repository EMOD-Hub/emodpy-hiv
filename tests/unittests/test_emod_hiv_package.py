import emod_hiv.bootstrap as dtk

import os
import unittest
import pytest
from unittest import TestSuite
from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
import helpers


def skip_load_tests(loader, standard_tests, pattern):
    """
    Customize how tests are loaded from them during normal test runs or test discovery.
    The test in this file will be skipped in normal test load and will be loaded as the first test in the test suite in the test_a_pre_test.py file.
    See load_tests Protocol in: https://docs.python.org/3.7/library/unittest.html#load-tests-protocol
    """
    suite = TestSuite()
    return suite


load_tests = skip_load_tests


@pytest.mark.unit
class TestDownloadFromPackage(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        helpers.delete_existing_file(manifest.eradication_path)
        helpers.delete_existing_file(manifest.schema_path)
        dtk.setup(manifest.package_folder)
        pass

    def setUp(self):
        print(f"running test: {self._testMethodName}:")

    def test_eradication(self):
        target_path = manifest.eradication_path
        self.assertTrue(os.path.exists(target_path), msg=f"Failed to get {target_path}")

    def test_schema(self):
        target_path = manifest.schema_path
        self.assertTrue(os.path.exists(target_path), msg=f"Failed to get {target_path}")


if __name__ == '__main__':
    unittest.main()
