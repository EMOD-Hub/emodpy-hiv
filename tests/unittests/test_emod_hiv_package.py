import emod_hiv.bootstrap as dtk

import os
import unittest
import pytest
from pathlib import Path
import sys

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
import helpers



@pytest.mark.unit
@pytest.mark.container
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
