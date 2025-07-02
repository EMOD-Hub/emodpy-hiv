import json
import unittest
import sys
import os
import time
from pathlib import Path
from emodpy.emod_task import logger
from emodpy.emod_task import EMODTask
from COMPS.Client import logger as comps_logger
from idmtools.core.platform_factory import Platform

# Add the parent directory to sys.path
manifest_directory = Path(__file__).resolve().parent
sys.path.append(str(manifest_directory))
import manifest
import helpers


class BaseSimTest(unittest.TestCase):

    def setUp(self) -> None:
        comps_logger.disabled = True
        self.task: EMODTask = None
        self.schema_path = manifest.schema_path
        self.eradication_path = manifest.eradication_path
        self.config_builder = helpers.config_builder
        self.demographics_builder = helpers.demographics_builder
        self.campaign_builder = helpers.campaign_builder
        self.sif_path = manifest.sif_path
        self.original_working_dir = os.getcwd()
        self.case_name = self._testMethodName
        print(f"\n{self.case_name}")
        helpers.create_failed_tests_folder()
        self.test_folder = os.path.join(manifest.failed_tests, f"{self.case_name}")
        if os.path.exists(self.test_folder):
            helpers.delete_existing_folder(self.test_folder)
        os.mkdir(self.test_folder)
        os.chdir(self.test_folder)# so EMODTask creates demographics folder here
        self.output_path = Path(self.test_folder).resolve()
        self.platform = Platform(manifest.container_platform_name)
        # self.platform = Platform("SLURMStage")  # "Calculon", node_group="idm_48cores", priority="Highest"

    def tearDown(self) -> None:
        # Check if the test failed and leave the data in the folder if it did
        helpers.close_idmtools_logger(logger.parent)
        if os.name == "nt":
            time.sleep(1)  # only needed for windows
        os.chdir(self.original_working_dir)

        delete_if_empty = any(error[1] for error in self._outcome.errors)
        helpers.delete_existing_folder(self.test_folder, must_be_empty=delete_if_empty)

    def compare_json(self, fn_exp, fn_act):
        with open(fn_exp, 'r') as f:
            json_exp = json.load(f)
        with open(fn_act, 'r') as f:
            json_act = json.load(f)

        if "Header" in json_exp.keys() and "DateTime" in json_exp["Header"].keys():
            json_exp["Header"]["DateTime"] = ""
            json_act["Header"]["DateTime"] = ""
        if "Header" in json_exp.keys() and "DTK_Version" in json_exp["Header"].keys():
            json_exp["Header"]["DTK_Version"] = ""
            json_act["Header"]["DTK_Version"] = ""
        if "Metadata" in json_exp.keys() and "DateCreated" in json_exp["Metadata"].keys():
            json_exp["Metadata"]["DateCreated"] = ""
            json_act["Metadata"]["DateCreated"] = ""
        if "Metadata" in json_exp.keys() and "Author" in json_exp["Metadata"].keys():
            json_exp["Metadata"]["Author"] = ""
            json_act["Metadata"]["Author"] = ""

        is_same = json_exp == json_act
        if is_same:
            helpers.delete_existing_file(fn_act)
        return is_same

