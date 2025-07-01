import json
import unittest
import sys
import os
import time
from pathlib import Path
from emodpy.emod_task import Reporters, logger
from emodpy.emod_task import EMODTask
from idmtools.entities.experiment import Experiment
from emodpy_hiv.utils.targeting_config import HasIntervention
from emodpy_hiv.reporters.reporters import (ReportNodeDemographics,
                                            ReportSimulationStats,
                                            ReportHumanMigrationTracking,
                                            ReportEventCounter,
                                            ReportEventRecorder,
                                            ReportPluginAgeAtInfection,
                                            ReportPluginAgeAtInfectionHistogram,
                                            SqlReport,
                                            ReportNodeEventRecorder,
                                            ReportCoordinatorEventRecorder,
                                            ReportSurveillanceEventRecorder,
                                            InsetChart,
                                            SpatialReport,
                                            ReportInfectionDuration,
                                            DemographicsReport,
                                            PropertyReport,
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
                                            SpatialReportChannels,
                                            RelationshipType)

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
import manifest
import helpers
from base_sim_test import BaseSimTest


class TestReportersHIV(BaseSimTest):

    def setUp(self) -> None:
        super().setUp()
        self.add_test_values()

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
        self.must_have_ip_key_value = "Aliens:Vulcan"
        self.must_have_intervention = "Vaccine"
        self.node_ids = [1]
        self.age_bins = [0, 5.6, 34, 70.1, 99]

    def test_report_hiv_run_it_all_on_comps_are_files_generated(self):
        def build_reports(reporters):
            report_filter = ReportFilter(start_day=0, end_day=600)
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=self.event_list))
            reporters.add(ReportEventCounter(reporters_object=reporters,
                                             event_list=self.event_list,
                                             report_filter=report_filter))
            reporters.add(ReportNodeEventRecorder(reporters_object=reporters,
                                                  event_list=self.event_list,
                                                  stats_by_ips=self.individual_properties))
            reporters.add(ReportInfectionDuration(reporters_object=reporters,
                                                  report_filter=report_filter))
            reporters.add(ReportPluginAgeAtInfection(reporters_object=reporters))
            reporters.add(SqlReport(reporters_object=reporters,
                                    include_health_table=True,
                                    include_individual_properties=True,
                                    include_infection_data_table=True,
                                    report_filter=report_filter))
            reporters.add(ReportPluginAgeAtInfectionHistogram(reporters_object=reporters,
                                                              age_bin_upper_edges=self.age_bins,
                                                              reporting_interval=self.start_day))
            reporters.add(ReportHumanMigrationTracking(reporters_object=reporters))
            reporters.add(ReportNodeDemographics(reporters_object=reporters,
                                                 age_bins=self.age_bins,
                                                 ip_key_to_collect=self.property_change_ip_to_record,
                                                 stratify_by_gender=False))
            reporters.add(ReportSimulationStats(reporters_object=reporters))
            reporters.add(PropertyReport(reporters_object=reporters))
            reporters.add(DemographicsReport(reporters_object=reporters))
            reporters.add(InsetChart(reporters_object=reporters,
                                     has_ip=self.individual_properties,
                                     has_interventions=self.individual_properties,
                                     include_pregnancies=True))
            reporters.add(SpatialReport(reporters_object=reporters,
                                        spatial_output_channels=[SpatialReportChannels.Births,
                                                                 SpatialReportChannels.Campaign_Cost]))
            reporters.add(ReportSurveillanceEventRecorder(reporters_object=reporters,
                                                          event_list=self.event_list,
                                                          stats_by_ips=self.individual_properties))
            reporters.add(ReportCoordinatorEventRecorder(reporters_object=reporters,
                                                         event_list=self.event_list))
            reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                                  reporting_period=30,
                                                  collect_targeting_config_data=[
                                                      HasIntervention(intervention_name="Vaccine")]))
            reporters.add(ReportRelationshipStart(reporters_object=reporters))
            reporters.add(ReportCoitalActs(reporters_object=reporters,
                                           relationship_type=RelationshipType.COMMERCIAL,
                                           has_intervention_with_name=self.event_list,
                                           individual_properties=self.individual_properties,
                                           partners_with_ip_key_value=[self.must_have_ip_key_value],
                                           report_filter=ReportFilter(start_year=self.start_year,
                                                                      end_year=self.end_year,
                                                                      node_ids=self.node_ids,
                                                                      min_age_years=self.min_age_years,
                                                                      max_age_years=self.max_age_years,
                                                                      must_have_ip_key_value=self.must_have_ip_key_value,
                                                                      must_have_intervention=self.must_have_intervention)))
            reporters.add(ReportRelationshipEnd(reporters_object=reporters))
            reporters.add(ReportTransmission(reporters_object=reporters))
            reporters.add(ReportHIVART(reporters_object=reporters))
            reporters.add(ReportHIVInfection(reporters_object=reporters))
            reporters.add(ReportHIVMortality(reporters_object=reporters))
            reporters.add(ReportRelationshipMigrationTracking(reporters_object=reporters,
                                                              report_filter=ReportFilter(start_year=self.start_year,
                                                                                         end_year=self.end_year,
                                                                                         node_ids=self.node_ids,
                                                                                         min_age_years=self.min_age_years,
                                                                                         max_age_years=self.max_age_years,
                                                                                         must_have_ip_key_value=self.must_have_ip_key_value,
                                                                                         must_have_intervention=self.must_have_intervention)))
            reporters.add(ReportPfaQueues(reporters_object=reporters))
            reporters.add(ReportRelationshipCensus(reporters_object=reporters,
                                                   report_filter=ReportFilter(start_year=self.start_year,
                                                                              end_year=self.end_year)))
            return reporters

        self.task = EMODTask.from_defaults(eradication_path=self.eradication_path,
                                              schema_path=self.schema_path,
                                              campaign_builder=self.campaign_builder,
                                              config_builder=self.config_builder,
                                              report_builder=build_reports,
                                              demographics_builder=self.demographics_builder)

        self.task.set_sif(self.sif_path, platform=self.platform)
        self.task.config.parameters.Custom_Coordinator_Events = self.event_list
        self.task.config.parameters.Custom_Node_Events = self.event_list

        experiment = Experiment.from_task(task=self.task,
                                          name=self.case_name)

        # The last step is to call run() on the ExperimentManager to run the simulations.
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, f"Experiment {self.case_name} failed.")

        this_sim = experiment.simulations[0]

        expected_reporter_files = ["AgeAtInfectionHistogramReport.json", "AgeAtInfectionReport.json",
                                   "BinnedReport.json", "DemographicsSummary.json",
                                   "PropertyReport.json", "ReportCoordinatorEventRecorder.csv",
                                   "ReportEventCounter.json", "ReportEventRecorder.csv",
                                   "ReportHumanMigrationTracking.csv", "ReportInfectionDuration.csv",
                                   "ReportNodeDemographics.csv", "ReportNodeEventRecorder.csv",
                                   "ReportSimulationStats.csv", "ReportSurveillanceEventRecorder.csv",
                                   "SpatialReport_Births.bin", "SpatialReport_Campaign_Cost.bin", "InsetChart.json",
                                   "SqlReport.db", "ReportHIVByAgeAndGender.csv", "RelationshipStart.csv",
                                   "RelationshipConsummated.csv", "RelationshipEnd.csv", "TransmissionReport.csv",
                                   "ReportHIVART.csv", "ReportHIVInfection.csv", "HIVMortality.csv",
                                   "ReportRelationshipMigrationTracking.csv", "ReportPfaQueues.csv",
                                   "ReportRelationshipCensus.csv"]
        expected_files_with_path = [os.path.join("output", file) for file in expected_reporter_files]

        # this will error out if any of the files are missing
        all_good = True
        exception = ""
        try:
            self.platform.get_files(this_sim, files=expected_files_with_path)
        except Exception as e:
            all_good = False
            exception = e

        self.assertTrue(all_good, f"Error: {exception}")


if __name__ == '__main__':
    unittest.main()
