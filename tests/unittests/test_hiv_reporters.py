import json
import unittest
import pytest
import sys
import os
import time
from emodpy.emod_task import Reporters, logger
from emodpy.emod_task import EMODTask
from emodpy.utils.emod_constants import MAX_FLOAT, MIN_YEAR, MAX_YEAR, MAX_AGE_YEARS_EMOD
from emodpy_hiv.utils import targeting_config
from emodpy_hiv.reporters.reporters import (ReportEventRecorder,
                                            ReportNodeEventRecorder,  # for multi-reporter test only
                                            InsetChart,
                                            ReportHIVByAgeAndGender,
                                            ReportRelationshipStart,
                                            ReportCoitalActs,
                                            ReportRelationshipEnd,
                                            ReportTransmission,
                                            ReportHIVART,
                                            ReportHIVInfection,
                                            ReportHIVMortality,
                                            ReportRelationshipMigrationTracking,
                                            ReportPfaQueues,
                                            ReportRelationshipCensus,
                                            ReportFilter,
                                            RelationshipType)

from pathlib import Path
manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest, helpers


@pytest.mark.unit
class TestReportersHIV(unittest.TestCase):
    """
    This tests hiv-specific reporters
    """

    def setUp(self) -> None:
        self.task: EMODTask
        self.schema_path = manifest.schema_path
        self.eradication_path = manifest.eradication_path
        self.original_working_dir = os.getcwd()
        self.case_name = self._testMethodName
        print(f"\n{self.case_name}")
        helpers.create_failed_tests_folder()
        self.test_folder = os.path.join(manifest.failed_tests, f"{self.case_name}")
        if os.path.exists(self.test_folder):
            helpers.delete_existing_folder(self.test_folder)
        os.mkdir(self.test_folder)
        os.chdir(self.test_folder)
        self.add_test_values()

    def tearDown(self) -> None:
        # Check if the test failed and leave the data in the folder if it did
        if any(error[1] for error in self._outcome.errors):
            if hasattr(self, "task"):  # don't need to do this for error checking tests
                if self.task:
                    # writing data to be looked at in the failed_tests folder
                    if len(self.task.common_assets) > 0:
                        for asset in self.task.common_assets:
                            if asset.filename == "custom_reports.json":
                                with open(asset.filename, "w") as f:
                                    f.write(asset.content)
                    with open("config.json", "w") as f:
                        f.write(json.dumps(self.task.config, indent=4))
                helpers.close_idmtools_logger(logger.parent)
                os.chdir(self.original_working_dir)
            else:
                os.chdir(self.original_working_dir)
                # error checking doesn't make any files
                helpers.delete_existing_folder(self.test_folder)
        else:
            helpers.close_idmtools_logger(logger.parent)
            if os.name == "nt":
                time.sleep(1)  # only needed for windows
            os.chdir(self.original_working_dir)
            helpers.delete_existing_folder(self.test_folder)

    def add_test_values(self):
        self.reporter = Reporters(self.schema_path)
        self.custom_report = None
        self.start_day = 102.3
        self.end_day = 2348
        self.start_year = 1921
        self.end_year = 2113
        self.min_age_years = 0.34
        self.max_age_years = 98.7
        self.random_string1 = "Cisco"
        self.random_string2 = "Picard"
        self.random_string3 = "Dax"
        self.random_string4 = "Kira"
        self.random_string5 = "Janeway"
        self.event_list = ["HappyBirthday", "NewInfectionEvent"]
        self.individual_properties = ["Aliens"]
        self.property_change_ip_to_record = "Aliens"
        self.must_have_ip_key_value = "Aliens:Vulkan"
        self.must_have_intervention = "Vaccine"
        self.node_ids = [1241, 2342, 485]
        self.age_bins = [0, 5.6, 34, 70.1, 99]

    def create_final_task(self, reporters, builtin=False):
        task = EMODTask.from_defaults(schema_path=self.schema_path,
                                         report_builder=reporters)
        if task.reporters.builtin_reporters:
            task.config.parameters.Custom_Reports_Filename = "custom_reports.json"
        for reporter in task.reporters.config_reporters:
            for i in reporter.parameters:
                setattr(task.config.parameters, i, reporter.parameters[i])
        if builtin:
            task.gather_transient_assets()  # if there are built-in reporters, adds custom_reports.json as an asset
            self.custom_report = json.loads(task.transient_assets[1].content)["Reports"][0]
        self.task = task
        return task

    # ------------------------
    # config-defined reporters
    # ------------------------

    def test_report_event_recorder_no_filter(self):
        """
            updated for hiv (years instead of days)
        """

        def build_reports(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=self.event_list,
                                              individual_properties=self.individual_properties,
                                              property_change_ip_to_record=self.random_string1))
            return reporters

        task = self.create_final_task(reporters=build_reports)
        self.assertEqual(task.config.parameters.Report_Event_Recorder, 1)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "")
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Individual_Properties, self.individual_properties)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest,
                         self.random_string1)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Events, self.event_list)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List, 0)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Start_Year, MIN_YEAR)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_End_Year, MAX_YEAR)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest, [])
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value, "")
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_Intervention, "")
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Min_Age_Years, 0)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Max_Age_Years, MAX_AGE_YEARS_EMOD)

    def test_report_event_recorder_filter_custom(self):  # also tests ReportFilter for config-based reports
        """
            updated for hiv (years instead of days)
        """

        def build_reports(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=self.event_list,
                                              individual_properties=self.individual_properties,
                                              property_change_ip_to_record=self.property_change_ip_to_record,
                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                         end_year=self.end_year,
                                                                         node_ids=self.node_ids,
                                                                         min_age_years=self.min_age_years,
                                                                         max_age_years=self.max_age_years,
                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                         must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Individual_Properties, self.individual_properties)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest,
                         self.property_change_ip_to_record)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Events, self.event_list)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List, 0)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_End_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest, self.node_ids)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value,
                         self.must_have_ip_key_value)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_Intervention,
                         self.must_have_intervention)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Min_Age_Years, self.min_age_years)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Max_Age_Years, self.max_age_years)

    def test_report_event_recorder_filter_custom2(self):  # also tests ReportFilter for config-based reports
        """
            updated for hiv (years instead of days)
        """

        def build_reports(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=self.event_list,
                                              individual_properties=[],
                                              property_change_ip_to_record="",
                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                         end_year=self.end_year,
                                                                         node_ids=self.node_ids,
                                                                         min_age_years=self.min_age_years,
                                                                         max_age_years=self.max_age_years,
                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                         must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Individual_Properties, [])
        self.assertEqual(task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest, "")
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Events, self.event_list)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List, 0)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_End_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest, self.node_ids)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value,
                         self.must_have_ip_key_value)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_Intervention,
                         self.must_have_intervention)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Min_Age_Years, self.min_age_years)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Max_Age_Years, self.max_age_years)

    def test_report_event_recorder_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=[])
        self.assertTrue("event_list must be a list of strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=[""])
        self.assertTrue("event_list must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=self.event_list,
                                individual_properties=[""])
        self.assertTrue("individual_properties must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=self.event_list,
                                individual_properties=self.individual_properties,
                                property_change_ip_to_record=self.property_change_ip_to_record,
                                report_filter=ReportFilter(start_year=self.start_day))
        self.assertTrue(
            "start_year must be a float greater than or equal to 1900, got value = 102.3" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=self.event_list,
                                individual_properties=self.individual_properties,
                                property_change_ip_to_record=self.property_change_ip_to_record,
                                report_filter=ReportFilter(end_year=self.end_day))
        self.assertTrue(
            "end_year must be a float less than or equal to 2200, got value = 2348" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportEventRecorder(self.reporter,
                                event_list=self.event_list,
                                individual_properties=self.individual_properties,
                                property_change_ip_to_record=self.property_change_ip_to_record,
                                report_filter=ReportFilter(filename_suffix=self.random_string5))
        self.assertTrue("filename_suffix is not a valid parameter for Report_Event_Recorder" in str(context.exception),
                        msg=str(context.exception))

    def test_report_filter_error_checking(self):
        with self.assertRaisesRegex(ValueError,
                                    f"start_day = {self.end_day} must less than end_day = {self.start_day}."):
            ReportFilter(start_day=self.end_day, end_day=self.start_day)
        with self.assertRaisesRegex(ValueError, f"start_year = {self.end_year} must less"
                                                f" than end_year = {self.start_year}."):
            ReportFilter(start_year=self.end_year, end_year=self.start_year)
        with self.assertRaisesRegex(ValueError, f"min_age_years = {self.max_age_years} must less"
                                                f" than max_age_years = {self.min_age_years}."):
            ReportFilter(min_age_years=self.max_age_years, max_age_years=self.min_age_years)
        with self.assertRaises(ValueError) as context:
            ReportFilter(start_day=-4)
        self.assertTrue(
            "start_day must be a float greater than or equal to 0, got value = -4." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(end_day=-4)
        self.assertTrue("end_day must be a float greater than or equal to 0, got value = -4." in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(start_year=1200.5)
        self.assertTrue(
            "start_year must be a float greater than or equal to 1900, got value = 1200.5." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(start_year=2500)
        self.assertTrue(
            "start_year must be a float less than or equal to 2200, got value = 2500." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(end_year=1200)
        self.assertTrue(
            "end_year must be a float greater than or equal to 1900, got value = 1200." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(end_year=2202)
        self.assertTrue(
            "end_year must be a float less than or equal to 2200, got value = 2202." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(node_ids=[1200, 123.5])
        self.assertTrue("node_ids must be a list integers > 1 and 123.5 is not, but is float" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(node_ids=[1200, 0])
        self.assertTrue("node_ids must be a list of positive integers, but it contains 0." in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(min_age_years=-1)
        self.assertTrue("min_age_years must be a float greater than or equal to 0, got "
                        "value = -1." in str(context.exception), msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(min_age_years=14687)
        self.assertTrue(
            "min_age_years must be a float less than or equal to 1000, got value = 14687" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(max_age_years=-2)
        self.assertTrue(
            "max_age_years must be a float greater than or equal to 0, got value = -2." in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportFilter(max_age_years=2039)
        self.assertTrue(
            "max_age_years must be a float less than or equal to 1000, got value = 2039." in str(context.exception),
            msg=str(context.exception))

    def test_multiple_config_reports(self):
        def build_reports(reporters):
            reporters.add(ReportNodeEventRecorder(reporters_object=reporters,
                                                  event_list=self.event_list,
                                                  node_properties_to_record=[self.random_string1, self.random_string2],
                                                  stats_by_ips=self.individual_properties))
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=self.event_list,
                                              individual_properties=self.individual_properties,
                                              property_change_ip_to_record=self.property_change_ip_to_record,
                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                         end_year=self.end_year,
                                                                         node_ids=self.node_ids,
                                                                         min_age_years=self.min_age_years,
                                                                         max_age_years=self.max_age_years,
                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                         must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Individual_Properties, self.individual_properties)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest,
                         self.property_change_ip_to_record)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Events, self.event_list)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Ignore_Events_In_List, 0)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_End_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Node_IDs_Of_Interest, self.node_ids)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_IP_Key_Value,
                         self.must_have_ip_key_value)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Must_Have_Intervention,
                         self.must_have_intervention)
        self.assertIsNone(getattr(task.config, "Report_Event_Recorder_Filename_Suffix", None))
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Min_Age_Years, self.min_age_years)
        self.assertEqual(task.config.parameters.Report_Event_Recorder_Max_Age_Years, self.max_age_years)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "")
        self.assertEqual(task.config.parameters.Report_Node_Event_Recorder_Events, self.event_list)
        self.assertEqual(task.config.parameters.Report_Node_Event_Recorder_Ignore_Events_In_List, 0)
        self.assertEqual(task.config.parameters.Report_Node_Event_Recorder_Node_Properties,
                         [self.random_string1, self.random_string2])
        self.assertEqual(task.config.parameters.Report_Node_Event_Recorder_Stats_By_IPs, self.individual_properties)

    def test_inset_chart_default(self):
        def build_reports(reporters):
            reporters.add(InsetChart(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        self.assertEqual(task.config.parameters.Enable_Default_Reporting, 1)
        self.assertEqual(task.config.parameters.Inset_Chart_Has_IP, [])
        self.assertEqual(task.config.parameters.Inset_Chart_Has_Interventions, [])
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Pregnancies, 0)
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Coital_Acts, 1)
        self.assertEqual(task.config.parameters.Report_HIV_Event_Channels_List, [])

    def test_inset_chart_custom(self):
        def build_reports(reporters):
            reporters.add(InsetChart(reporters_object=reporters,
                                     has_ip=self.event_list,
                                     has_interventions=self.individual_properties,
                                     include_pregnancies=True,
                                     include_coital_acts=False,
                                     event_channels_list=[self.random_string1, self.random_string2]))
            return reporters

        task = self.create_final_task(build_reports)
        self.assertEqual(task.config.parameters.Enable_Default_Reporting, 1)
        self.assertEqual(task.config.parameters.Inset_Chart_Has_IP, self.event_list)
        self.assertEqual(task.config.parameters.Inset_Chart_Has_Interventions, self.individual_properties)
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Pregnancies, 1)
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Coital_Acts, 0)
        self.assertEqual(task.config.parameters.Report_HIV_Event_Channels_List,
                         [self.random_string1, self.random_string2])

    def test_inset_chart_custom2(self):
        def build_reports(reporters):
            reporters.add(InsetChart(reporters_object=reporters,
                                     has_ip=[],
                                     has_interventions=[],
                                     include_pregnancies=True,
                                     include_coital_acts=False,
                                     event_channels_list=[]))
            return reporters

        task = self.create_final_task(build_reports)
        self.assertEqual(task.config.parameters.Enable_Default_Reporting, 1)
        self.assertEqual(task.config.parameters.Inset_Chart_Has_IP, [])
        self.assertEqual(task.config.parameters.Inset_Chart_Has_Interventions, [])
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Pregnancies, 1)
        self.assertEqual(task.config.parameters.Inset_Chart_Include_Coital_Acts, 0)
        self.assertEqual(task.config.parameters.Report_HIV_Event_Channels_List,
                         [])

    def test_inset_chart_error_checking(self):
        with self.assertRaises(ValueError) as context:
            InsetChart(self.reporter,
                       has_ip=[""])
        self.assertTrue("has_ip must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            InsetChart(self.reporter,
                       has_interventions=[""])
        self.assertTrue("has_interventions must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            InsetChart(self.reporter,
                       event_channels_list=[""])
        self.assertTrue("event_channels_list must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))

    def test_multiple_of_same_report(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipMigrationTracking(reporters_object=reporters,
                                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                                         end_year=self.end_year,
                                                                                         filename_suffix=self.random_string3,
                                                                                         node_ids=self.node_ids,
                                                                                         min_age_years=self.min_age_years,
                                                                                         max_age_years=self.max_age_years,
                                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                                         must_have_intervention=self.must_have_intervention)))
            reporters.add(ReportRelationshipMigrationTracking(reporters_object=reporters,
                                                              report_filter=ReportFilter(start_year=2008,
                                                                                         end_year=2013)))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], 'ReportRelationshipMigrationTracking')
        self.assertEqual(self.custom_report["Start_Year"], self.start_year)
        self.assertEqual(self.custom_report["End_Year"], self.end_year)
        self.assertEqual(self.custom_report["Filename_Suffix"], self.random_string3)
        self.assertEqual(self.custom_report["Min_Age_Years"], self.min_age_years)
        self.assertEqual(self.custom_report["Max_Age_Years"], self.max_age_years)
        self.assertEqual(self.custom_report["Must_Have_IP_Key_Value"], self.must_have_ip_key_value)
        self.assertEqual(self.custom_report["Must_Have_Intervention"], self.must_have_intervention)
        self.assertEqual(self.custom_report["Node_IDs_Of_Interest"], self.node_ids)
        self.custom_report = json.loads(task.transient_assets[1].content)["Reports"][1]
        self.assertEqual(self.custom_report["class"], 'ReportRelationshipMigrationTracking')
        self.assertEqual(self.custom_report["Start_Year"], 2008)
        self.assertEqual(self.custom_report["End_Year"], 2013)

    def test_multiple_of_configreport_error_checking(self):
        with self.assertRaises(Exception) as context:
            def build_reports(reporters):
                reporters.add(InsetChart(reporters_object=reporters, has_interventions=["warp9"],
                                         include_coital_acts=False))
                reporters.add(InsetChart(reporters_object=reporters, has_ip=["test"]))
                return reporters

            task = self.create_final_task(build_reports, builtin=True)
        self.assertTrue("Reporter InsetChart is a ConfigReporter type and "
                        "cannot be added more than once and there is already one of these in the list."
                        "Please update to add only one"
                        " InsetChart to the Reporters object." in str(context.exception),
                        msg=str(context.exception))


    def test_report_hiv_by_age_and_gender_default(self):
        def build_reports(reporters):
            reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters))
            return reporters

        task = self.create_final_task(reporters=build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Concordant_Relationships, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Relationships, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Transmitters, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_On_Art_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Circumcision_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Gender_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_IP_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Intervention_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Event_Counter_List, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Targeting_Config_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_Period, 182.5 * 2)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Use_Old_Format, 0)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Start_Year, MIN_YEAR)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stop_Year, MAX_YEAR)

    def test_report_hiv_by_age_and_gender_custom(self):
        def build_reports(reporters):
            reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                                  collect_gender_data=True,
                                                  collect_age_bins_data=[],
                                                  collect_circumcision_data=True,
                                                  collect_hiv_data=True,
                                                  collect_hiv_stage_data=False,
                                                  collect_on_art_data=True,
                                                  collect_ip_data=[],
                                                  collect_intervention_data=[],
                                                  collect_targeting_config_data=[
                                                      targeting_config.HasIntervention(self.random_string1)],
                                                  add_transmitters=True,
                                                  stratify_infected_by_cd4=True,
                                                  event_counter_list=[],
                                                  add_relationships=True,
                                                  add_concordant_relationships=True,
                                                  reporting_period=38,
                                                  use_old_format=True,
                                                  report_filter=ReportFilter(start_year=self.start_year,
                                                                             end_year=self.end_year)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Concordant_Relationships, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Relationships, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Transmitters, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_On_Art_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Circumcision_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Gender_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_IP_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Intervention_Data, [])
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Event_Counter_List,
                         [])
        self.assertEqual(str(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Targeting_Config_Data),
                         str([targeting_config.HasIntervention(self.random_string1).to_schema_dict(self.reporter)]))
        # we validate that the targeting config converts and works correctly in test_sim_with_reporters.py
        self.assertEqual(task.config.parameters.Report_HIV_Period, 38 * 2) # see reporter for explanation
        # ReportFilter
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stop_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Use_Old_Format, 1)

    def test_report_hiv_by_age_and_gender_custom2(self):
        def build_reports(reporters):
            reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                                  collect_gender_data=True,
                                                  collect_age_bins_data=self.age_bins,
                                                  collect_circumcision_data=True,
                                                  collect_hiv_data=True,
                                                  collect_hiv_stage_data=False,
                                                  collect_on_art_data=True,
                                                  collect_ip_data=self.individual_properties,
                                                  collect_intervention_data=self.event_list,
                                                  collect_targeting_config_data=[
                                                      targeting_config.HasIntervention(self.random_string1)],
                                                  add_transmitters=True,
                                                  stratify_infected_by_cd4=True,
                                                  event_counter_list=self.event_list,
                                                  add_relationships=True,
                                                  add_concordant_relationships=True,
                                                  reporting_period=38,
                                                  report_filter=ReportFilter(start_year=self.start_year,
                                                                             end_year=self.end_year)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Concordant_Relationships, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Relationships, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Add_Transmitters, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_On_Art_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Circumcision_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Gender_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Data, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4, 1)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data, self.age_bins)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_IP_Data, self.individual_properties)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Intervention_Data, self.event_list)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Event_Counter_List,
                         self.event_list)
        self.assertEqual(str(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_Targeting_Config_Data),
                         str([targeting_config.HasIntervention(self.random_string1).to_schema_dict(self.reporter)]))
        # we validate that the targeting config converts and works correctly in test_sim_with_reporters.py
        self.assertEqual(task.config.parameters.Report_HIV_Period, 38 * 2) # see reporter for explanation
        # ReportFilter
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Stop_Year, self.end_year)

    def test_report_hiv_by_age_and_gender_custom3(self):
        def build_reports(reporters):
            reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                                  collect_hiv_stage_data=True))
            return reporters

        task = self.create_final_task(build_reports)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Data, 0)
        self.assertEqual(task.config.parameters.Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data, 1)

    def test_report_hiv_by_age_and_gender_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_age_bins_data=[0, 56, 34, 70.1, 99])
        self.assertTrue("collect_age_bins_data's bins must be in ascending order" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(TypeError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_age_bins_data=[0, "5", 34, 70.1, 99])
        self.assertTrue(
            "Each bin must be either int or float, got str for collect_age_bins_data index 1" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_ip_data=[""])
        self.assertTrue("collect_ip_data must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_intervention_data=[""])
        self.assertTrue("collect_intervention_data must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    event_counter_list=[""])
        self.assertTrue("event_counter_list must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_hiv_data=True,
                                    collect_hiv_stage_data=True)
        self.assertTrue("collect_hiv_stage_data cannot be used with collect_on_art_data or collect_hiv_data" in str(
            context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    collect_on_art_data=True,
                                    collect_hiv_stage_data=True)
        self.assertTrue("collect_hiv_stage_data cannot be used with collect_on_art_data or collect_hiv_data" in str(
            context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue("start_day is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue("end_day is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(filename_suffix=self.random_string4))
        self.assertTrue(
            "filename_suffix is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(node_ids=self.node_ids))
        self.assertTrue("node_ids is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(max_age_years=self.max_age_years))
        self.assertTrue(
            "max_age_years is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(min_age_years=self.min_age_years))
        self.assertTrue(
            "min_age_years is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(must_have_ip_key_value=self.must_have_ip_key_value))
        self.assertTrue(
            "must_have_ip_key_value is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVByAgeAndGender(reporters_object=self.reporter,
                                    report_filter=ReportFilter(must_have_intervention=self.must_have_intervention))
        self.assertTrue(
            "must_have_intervention is not a valid parameter for Report_HIV_ByAgeAndGender" in str(context.exception),
            msg=str(context.exception))

    def test_report_relationship_start_default(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipStart(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Relationship_Start, 1)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Include_HIV_Disease_Statistics, 1)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Include_Other_Relationship_Statistics, 1)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Individual_Properties, [])
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Start_Year, MIN_YEAR)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_End_Year, MAX_YEAR)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Node_IDs_Of_Interest, [])
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Must_Have_IP_Key_Value, "")
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Must_Have_Intervention, "")
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Min_Age_Years, 0)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Max_Age_Years, MAX_AGE_YEARS_EMOD)

    def test_report_relationship_start_custom(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipStart(reporters_object=reporters,
                                                  include_hiv_disease_statistics=False,
                                                  include_other_relationship_statistics=False,
                                                  individual_properties=self.individual_properties,
                                                  report_filter=ReportFilter(start_year=self.start_year,
                                                                             end_year=self.end_year,
                                                                             node_ids=self.node_ids,
                                                                             min_age_years=self.min_age_years,
                                                                             max_age_years=self.max_age_years,
                                                                             must_have_ip_key_value=self.must_have_ip_key_value,
                                                                             must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Relationship_Start, 1)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Include_HIV_Disease_Statistics, 0)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Include_Other_Relationship_Statistics, 0)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Individual_Properties,
                         self.individual_properties)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_End_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Node_IDs_Of_Interest, self.node_ids)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Must_Have_IP_Key_Value,
                         self.must_have_ip_key_value)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Must_Have_Intervention,
                         self.must_have_intervention)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Min_Age_Years, self.min_age_years)
        self.assertEqual(task.config.parameters.Report_Relationship_Start_Max_Age_Years, self.max_age_years)

    def test_report_relationship_start_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportRelationshipStart(self.reporter,
                                    individual_properties=[""])
        self.assertTrue("individual_properties must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipStart(reporters_object=self.reporter,
                                    report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue("start_day is not a valid parameter for Report_Relationship_Start" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipStart(reporters_object=self.reporter,
                                    report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue("end_day is not a valid parameter for Report_Relationship_Start" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipStart(reporters_object=self.reporter,
                                    report_filter=ReportFilter(filename_suffix=self.random_string4))
        self.assertTrue(
            "filename_suffix is not a valid parameter for Report_Relationship_Start" in str(context.exception),
            msg=str(context.exception))

    def test_report_coital_acts_default(self):
        def build_reports(reporters):
            reporters.add(ReportCoitalActs(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Coital_Acts, 1)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Partners_With_IP_Key_Value, [])
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Individual_Properties, [])
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Relationship_Type, "NA")
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Has_Intervention_With_Name, [])
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Start_Year, MIN_YEAR)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_End_Year, MAX_YEAR)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Node_IDs_Of_Interest, [])
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Must_Have_IP_Key_Value, "")
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Must_Have_Intervention, "")
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Min_Age_Years, 0)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Max_Age_Years, MAX_AGE_YEARS_EMOD)

    def test_report_coital_acts_custom(self):
        def build_reports(reporters):
            reporters.add(ReportCoitalActs(reporters_object=reporters,
                                           relationship_type=RelationshipType.COMMERCIAL,
                                           has_intervention_with_name=self.event_list,
                                           individual_properties=self.individual_properties,
                                           partners_with_ip_key_value=[f"{self.random_string4}:{self.random_string1}"],
                                           report_filter=ReportFilter(start_year=self.start_year,
                                                                      end_year=self.end_year,
                                                                      node_ids=self.node_ids,
                                                                      min_age_years=self.min_age_years,
                                                                      max_age_years=self.max_age_years,
                                                                      must_have_ip_key_value=self.must_have_ip_key_value,
                                                                      must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Coital_Acts, 1)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Partners_With_IP_Key_Value,
                         [f"{self.random_string4}:{self.random_string1}"])
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Individual_Properties, self.individual_properties)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Relationship_Type,
                         "COMMERCIAL")
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Has_Intervention_With_Name, self.event_list)
        # ReportFilter should be at defaults
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_End_Year, self.end_year)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Node_IDs_Of_Interest, self.node_ids)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Must_Have_IP_Key_Value, self.must_have_ip_key_value)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Must_Have_Intervention, self.must_have_intervention)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Min_Age_Years, self.min_age_years)
        self.assertEqual(task.config.parameters.Report_Coital_Acts_Max_Age_Years, self.max_age_years)

    def test_report_coital_acts_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             individual_properties=[""])
        self.assertTrue("individual_properties must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             has_intervention_with_name=[""])
        self.assertTrue("has_intervention_with_name must be a list of non-empty strings" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue("start_day is not a valid parameter for Report_Coital_Acts" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue("end_day is not a valid parameter for Report_Coital_Acts" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             report_filter=ReportFilter(filename_suffix=self.random_string4))
        self.assertTrue("filename_suffix is not a valid parameter for Report_Coital_Acts" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             partners_with_ip_key_value=[self.random_string1])
        self.assertTrue("Invalid key-value pair: Cisco" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             partners_with_ip_key_value=[""])
        self.assertTrue("The 'key:value' entries of argument 'partners_with_ip_key_value' cannot be empty string or None." in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportCoitalActs(reporters_object=self.reporter,
                             partners_with_ip_key_value=[None])
        self.assertTrue("The 'key:value' entries of argument 'partners_with_ip_key_value' cannot be empty string or None." in str(context.exception),
                        msg=str(context.exception))

    def test_report_relationship_end(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipEnd(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Relationship_End, 1)

    def test_report_transmission(self):
        def build_reports(reporters):
            reporters.add(ReportTransmission(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_Transmission, 1)

    def test_report_hivart(self):
        def build_reports(reporters):
            reporters.add(ReportHIVART(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_ART, 1)

    def test_report_hiv_infection_default(self):
        def build_reports(reporters):
            reporters.add(ReportHIVInfection(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_Infection, 1)
        # ReportFilter
        self.assertEqual(task.config.parameters.Report_HIV_Infection_Start_Year, MIN_YEAR)
        self.assertEqual(task.config.parameters.Report_HIV_Infection_Stop_Year, MAX_YEAR)

    def test_report_hiv_infection_custom(self):
        def build_reports(reporters):
            reporters.add(ReportHIVInfection(reporters_object=self.reporter,
                                             report_filter=ReportFilter(start_year=self.start_year,
                                                                        end_year=self.end_year)))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_Infection, 1)
        # ReportFilter
        self.assertEqual(task.config.parameters.Report_HIV_Infection_Start_Year, self.start_year)
        self.assertEqual(task.config.parameters.Report_HIV_Infection_Stop_Year, self.end_year)

    def test_report_hiv_infection_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue("start_day is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue("end_day is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(filename_suffix=self.random_string4))
        self.assertTrue("filename_suffix is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(node_ids=self.node_ids))
        self.assertTrue("node_ids is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(max_age_years=self.max_age_years))
        self.assertTrue("max_age_years is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(min_age_years=self.min_age_years))
        self.assertTrue("min_age_years is not a valid parameter for Report_HIV_Infection" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(must_have_ip_key_value=self.must_have_ip_key_value))
        self.assertTrue(
            "must_have_ip_key_value is not a valid parameter for Report_HIV_Infection" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportHIVInfection(reporters_object=self.reporter,
                               report_filter=ReportFilter(must_have_intervention=self.must_have_intervention))
        self.assertTrue(
            "must_have_intervention is not a valid parameter for Report_HIV_Infection" in str(context.exception),
            msg=str(context.exception))

    def test_report_hiv_mortality(self):
        def build_reports(reporters):
            reporters.add(ReportHIVMortality(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports)
        # verifying that the settings made it to the config
        self.assertEqual(task.config.parameters.Report_HIV_Mortality, 1)

    # ------------------------
    # built-in reporters
    # ------------------------

    def test_report_relationship_migration_tracking_default(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipMigrationTracking(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], 'ReportRelationshipMigrationTracking')
        # ReportFilter defaults
        self.assertEqual(self.custom_report["Start_Year"], MIN_YEAR)
        self.assertEqual(self.custom_report["End_Year"], MAX_YEAR)
        self.assertEqual(self.custom_report["Filename_Suffix"], "")
        self.assertEqual(self.custom_report["Min_Age_Years"], 0)
        self.assertEqual(self.custom_report["Max_Age_Years"], MAX_AGE_YEARS_EMOD)
        self.assertEqual(self.custom_report["Must_Have_IP_Key_Value"], "")
        self.assertEqual(self.custom_report["Must_Have_Intervention"], "")
        self.assertEqual(self.custom_report["Node_IDs_Of_Interest"], [])

    def test_report_relationship_migration_tracking_custom(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipMigrationTracking(reporters_object=reporters,
                                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                                         end_year=self.end_year,
                                                                                         filename_suffix=self.random_string3,
                                                                                         node_ids=self.node_ids,
                                                                                         min_age_years=self.min_age_years,
                                                                                         max_age_years=self.max_age_years,
                                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                                         must_have_intervention=self.must_have_intervention)))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], 'ReportRelationshipMigrationTracking')
        # ReportFilter custom
        self.assertEqual(self.custom_report["Start_Year"], self.start_year)
        self.assertEqual(self.custom_report["End_Year"], self.end_year)
        self.assertEqual(self.custom_report["Filename_Suffix"], self.random_string3)
        self.assertEqual(self.custom_report["Min_Age_Years"], self.min_age_years)
        self.assertEqual(self.custom_report["Max_Age_Years"], self.max_age_years)
        self.assertEqual(self.custom_report["Must_Have_IP_Key_Value"], self.must_have_ip_key_value)
        self.assertEqual(self.custom_report["Must_Have_Intervention"], self.must_have_intervention)
        self.assertEqual(self.custom_report["Node_IDs_Of_Interest"], self.node_ids)

    def test_report_relationship_migration_tracking_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportRelationshipMigrationTracking(reporters_object=self.reporter,
                                                report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue(
            "start_day is not a valid parameter for ReportRelationshipMigrationTracking" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipMigrationTracking(reporters_object=self.reporter,
                                                report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue(
            "end_day is not a valid parameter for ReportRelationshipMigrationTracking" in str(context.exception),
            msg=str(context.exception))

    def test_report_pfa_queues(self):
        def build_reports(reporters):
            reporters.add(ReportPfaQueues(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], 'ReportPfaQueues')

    def test_report_relationship_census_default(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipCensus(reporters_object=reporters))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], "ReportRelationshipCensus")
        self.assertEqual(self.custom_report["Report_File_Name"], "ReportRelationshipCensus.csv")
        self.assertEqual(self.custom_report["Reporting_Interval_Years"], 1)
        # ReportFilter defaults
        self.assertEqual(self.custom_report["Start_Year"], 0)
        self.assertEqual(self.custom_report["End_Year"], MAX_FLOAT)

    def test_report_relationship_census_custom(self):
        def build_reports(reporters):
            reporters.add(ReportRelationshipCensus(reporters_object=reporters,
                                                   report_filename=self.random_string4,
                                                   reporting_interval_years=12.3,
                                                   report_filter=ReportFilter(start_year=self.start_year,
                                                                              end_year=self.end_year)))
            return reporters

        task = self.create_final_task(build_reports, builtin=True)
        self.assertEqual(task.config.parameters.Custom_Reports_Filename, "custom_reports.json")
        self.assertEqual(self.custom_report["class"], 'ReportRelationshipCensus')
        self.assertEqual(self.custom_report["Report_File_Name"], self.random_string4)
        self.assertEqual(self.custom_report["Reporting_Interval_Years"], 12.3)
        # ReportFilter custom
        self.assertEqual(self.custom_report["Start_Year"], self.start_year)
        self.assertEqual(self.custom_report["End_Year"], self.end_year)

    def test_report_relationship_census_error_checking(self):
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     reporting_interval_years=-1)
        self.assertTrue("reporting_interval_years must be a float greater than or equal to 0, got value = -1" in str(
            context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     reporting_interval_years=120)
        self.assertTrue("reporting_interval_years must be a float less than or equal to 100, got value = 120" in str(
            context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(start_day=self.start_day))
        self.assertTrue("start_day is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(end_day=self.end_day))
        self.assertTrue("end_day is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(filename_suffix=self.random_string4))
        self.assertTrue(
            "filename_suffix is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(node_ids=self.node_ids))
        self.assertTrue("node_ids is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(max_age_years=self.max_age_years))
        self.assertTrue("max_age_years is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(min_age_years=self.min_age_years))
        self.assertTrue("min_age_years is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
                        msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(must_have_ip_key_value=self.must_have_ip_key_value))
        self.assertTrue(
            "must_have_ip_key_value is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
            msg=str(context.exception))
        with self.assertRaises(ValueError) as context:
            ReportRelationshipCensus(reporters_object=self.reporter,
                                     report_filter=ReportFilter(must_have_intervention=self.must_have_intervention))
        self.assertTrue(
            "must_have_intervention is not a valid parameter for ReportRelationshipCensus" in str(context.exception),
            msg=str(context.exception))


if __name__ == '__main__':
    unittest.main()
