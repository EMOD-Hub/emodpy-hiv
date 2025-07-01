from functools import partial
import unittest
import sys
from pathlib import Path
import json
import pandas as pd
from idmtools.core import ItemType
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.campaign.individual_intervention import (OutbreakIndividual, AntiretroviralTherapy, ARTDropout,
                                                         ARTMortalityTable, HIVARTStagingCD4AgnosticDiagnostic, HIVARTStagingByCD4Diagnostic,
                                                         HIVDrawBlood, MaleCircumcision, ModifyStiCoInfectionStatus,
                                                         PMTCT, ControlledVaccine, HIVRandomChoice, HIVRapidHIVDiagnostic,
                                                         HIVSigmoidByYearAndSexDiagnostic, Sigmoid, STIIsPostDebut,
                                                         HIVPiecewiseByYearAndSexDiagnostic, BroadcastEvent)
from emodpy_hiv.campaign.distributor import add_intervention_scheduled, add_intervention_triggered
from emodpy_hiv.campaign.common import TargetDemographicsConfig as TDC, ValueMap, TargetGender
from emodpy_hiv.campaign.waning_config import MapPiecewise
from emodpy_hiv.utils.distributions import ConstantDistribution
from emodpy_hiv.reporters.reporters import ReportEventRecorder

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
from base_sim_test import BaseSimTest


class TestSimulation(BaseSimTest):

    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def build_demog_from_template_node(self):
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=1000, name="1", forced_id=1,
                                                   default_society_template="PFA-Southern-Africa")
        return demog

    # def build_demog_from_pop_csv(self):
    #     pop_filename_in = parent.parent / 'unittests' / 'inputs' / 'tiny_facebook_pop_clipped.csv'
    #     pop_filename_out = parent.parent / "spatial_gridded_pop_dir"
    #     site = "No_Site"
    #
    #     demog = HIVDemographics.from_pop_csv(pop_filename_in, pop_filename_out=pop_filename_out, site=site)
    #     return demog

    # def build_demog_from_params(self):
    #     totpop = 9876
    #     num_nodes = 199
    #     frac_rural = 0.3
    #     demog = HIVDemographics.from_params(tot_pop=totpop, num_nodes=num_nodes, frac_rural=frac_rural)
    #     return demog

    def build_outbreak_campaign(self, camp, timestep):
        ob = OutbreakIndividual(campaign=camp)
        add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=timestep)
        return camp

    @staticmethod
    def set_param_fn(config, duration):  # from start here example
        config.parameters.Simulation_Type = "HIV_SIM"  # this should be set in the package.
        config.parameters.Simulation_Duration = duration
        config.parameters.Base_Infectivity = 3.5
        config.parameters.Enable_Demographics_Reporting = 0  # just because I don't like our default for this
        config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
        # This one is crazy! :(
        config.parameters.Maternal_Infection_Transmission_Probability = 0
        config.parameters[
            'logLevel_default'] = "WARNING"  # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys_

        return config

    def set_param_fn_buildin_demog(self, config):  # buildin demographics is not working for hiv
        config = self.set_param_fn(config, 10)
        config.parameters.Enable_Demographics_Builtin = 1
        return config

    def test_outbreak_and_demog_from_template_node(self):
        start_day = 5
        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(self.build_outbreak_campaign, timestep=start_day),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog_from_template_node,
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_outbreak_demographics_from_template_node")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/InsetChart.json"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'InsetChart.json'
            self.assertTrue(file_path.is_file())
            # validate result
            with file_path.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['New Infections']['Data']
            self.assertEqual(sum(new_infection[:start_day - 1]), 0,
                             msg='Test failed: expected no new infection before outbreak start day.')
            self.assertGreater(new_infection[start_day - 1], 0,
                               msg='Test failed: expected new infection at outbreak start day.')

            total_pop = inset_chart['Channels']['Statistical Population']['Data'][0]
            self.assertEqual(total_pop, 1000,
                             msg=f"Expected 1000 population, got {total_pop}, please check demographics "
                                 f"for sim: {simulation.id}.")

    # def test_demog_from_pop_csv(self):
    #     task = emod_task.EMODTask.from_defaults(
    #         eradication_path=str(self.eradication_path),
    #         campaign_builder=None,
    #         schema_path=str(self.schema_path),
    #         config_builder=partial(self.set_param_fn, duration=60),
    #         demographics_builder=self.build_demog_from_pop_csv
    #     )
    #     task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string
    #
    #     builder = SimulationBuilder()
    #     builder.add_sweep_definition(self.update_sim_random_seed, range(1))
    #
    #     experiment = Experiment.from_builder(builder, task, name="HIV Test_demographics_from_pop_csv")
    #
    #     experiment.run(wait_until_done=True, platform=self.platform)
    #
    #     self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")
    #
    #     print(f"Experiment {experiment.uid} succeeded.")
    #
    #     filenames = ["output/InsetChart.json"]
    #
    #     sims = self.platform.get_children_by_object(experiment)
    #     output_path = parent / "inputs"
    #     for simulation in sims:
    #         # download files from simulation
    #         self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
    #                                       output=self.output_path)
    #         # validate files exist
    #         local_path = self.output_path / str(simulation.uid)
    #         file_path = local_path / 'output' / 'InsetChart.json'
    #         self.assertTrue(file_path.is_file())
    #         # validate result
    #         with file_path.open(mode='r') as json_file:
    #             inset_chart = json.load(json_file)
    #
    #         total_pop = inset_chart['Channels']['Statistical Population']['Data'][0]
    #         self.assertEqual(total_pop, 42, msg=f"Expected 42 population, got {total_pop}, please check demographics "
    #                                             f"for sim: {simulation.id}.")

    # def test_demog_from_param(self):
    #     task = emod_task.EMODTask.from_default2(
    #         config_path="config_pop_csv.json",
    #         eradication_path=str(self.eradication_path),
    #         campaign_builder=None,
    #         schema_path=str(self.schema_path),
    #         config_builder=partial(self.set_param_fn, duration=5),
    #         ep4_custom_cb=None,
    #         demographics_builder=self.build_demog_from_params,
    #         plugin_report=None
    #     )
    #     task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string
    #
    #     builder = SimulationBuilder()
    #     builder.add_sweep_definition(self.update_sim_random_seed, range(1))
    #
    #     experiment = Experiment.from_builder(builder, task, name="HIV Test_demographics_from_params")
    #
    #     experiment.run(wait_until_done=True, platform=self.platform)
    #
    #     self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")
    #
    #     print(f"Experiment {experiment.uid} succeeded.")
    #
    #     filenames = ["output/InsetChart.json"]
    #
    #     sims = self.platform.get_children_by_object(experiment)
    #     output_path = parent / "inputs"
    #     for simulation in sims:
    #         # download files from simulation
    #         self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
    #                                       output=self.output_path)
    #         # validate files exist
    #         local_path = self.output_path / str(simulation.uid)
    #         file_path = local_path / 'output' / 'InsetChart.json'
    #         self.assertTrue(file_path.is_file())
    #         # validate result
    #         with file_path.open(mode='r') as json_file:
    #             inset_chart = json.load(json_file)
    #
    #         total_pop = inset_chart['Channels']['Statistical Population']['Data'][0]
    #         # https://github.com/InstituteforDiseaseModeling/emod-api/issues/112
    #         self.assertAlmostEqual(total_pop, 9876, delta=15, msg=f"Expected about 9876 population, got {total_pop}, "
    #                                                               f"please check demographics for sim: {simulation.id}.")

    def test_art(self):
        startday = 5
        cov = 0.7

        def build_camp(campaign, start_day, coverage):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day - 1)

            art = AntiretroviralTherapy(campaign=campaign)
            add_intervention_scheduled(intervention_list=[art], campaign=campaign, start_day=start_day, node_ids=None,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday, coverage=cov),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_art")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/InsetChart.json"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'InsetChart.json'
            self.assertTrue(file_path.is_file())
            # validate result
            with file_path.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['Number of Individuals on ART']['Data']
            self.assertEqual(sum(new_infection[:startday - 1]), 0,
                             msg='Test failed: expected no Individuals on ART before ART start day.')
            self.assertAlmostEqual(new_infection[startday - 1], 1000 * cov, delta=30,
                                   msg=f'Test failed: expected {1000 * cov} Individuals on ART at ART start day.')

    def test_artdropout(self):
        startday = 3
        cov = 0.6

        def build_camp(campaign, start_day, coverage):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day - 2)

            art = AntiretroviralTherapy(campaign=campaign)
            add_intervention_scheduled(intervention_list=[art], campaign=campaign, start_day=start_day - 1, node_ids=None,
                                       target_demographics_config=TDC(demographic_coverage=1))

            artdropout = ARTDropout(campaign=campaign)
            add_intervention_scheduled(intervention_list=[artdropout], campaign=campaign, start_day=start_day,
                                       node_ids=None,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday, coverage=cov),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1, 3))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_artdropout")  # "HIV Test_artdropout"

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/InsetChart.json"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'InsetChart.json'
            self.assertTrue(file_path.is_file())
            # validate result
            with file_path.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['Number of ART dropouts (cumulative)']['Data']
            self.assertEqual(sum(new_infection[:startday - 1]), 0,
                             msg='Test failed: expected no ART dropouts before artdropout start day.')
            self.assertAlmostEqual(new_infection[startday - 1], 1000 * cov, delta=30.36,  # 95% confidence interval
                                   msg=f'Test failed: expected {1000 * cov} ART dropouts at artdropout start day.')

    def test_artmortalitytable(self):
        startday = 5
        cov = 0.8

        def build_camp(campaign, start_day, coverage):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day - 4)

            art = AntiretroviralTherapy(campaign=campaign)
            add_intervention_scheduled(intervention_list=[art], campaign=campaign, start_day=start_day - 3,
                                       node_ids=None,
                                       target_demographics_config=TDC(demographic_coverage=1))

            # Define mortality table with realistic values showing decreasing mortality over time
            mortality_table = [
                [  # Duration bin 0 (0-6 months)
                    [0.2015, 0.2015, 0.1128, 0.0625, 0.0312, 0.0206, 0.0162],  # Age 0-40
                    [0.0875, 0.0875, 0.0490, 0.0271, 0.0136, 0.0062, 0.0041]   # Age 40+
                ],
                [  # Duration bin 1 (6-12 months)
                    [0.0271, 0.0271, 0.0184, 0.0149, 0.0074, 0.0048, 0.0048],
                    [0.0171, 0.0171, 0.0116, 0.0094, 0.0047, 0.0030, 0.0030]
                ],
                [  # Duration bin 2 (12+ months)
                    [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026],
                    [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026]
                ]
            ]

            art_mortality = ARTMortalityTable(
                campaign=campaign,
                mortality_table=mortality_table,
                art_duration_days_bins=[0, 30, 45],  # 0, 1mo, 1.5mo
                age_years_bins=[0, 40],                # Under 40, 40+
                cd4_count_bins=[0, 25, 74.5, 149.5, 274.5, 424.5, 624.5],  # CD4 count thresholds
                days_to_achieve_viral_suppression=183.0,
                art_multiplier_on_transmission_prob_per_act=0.08,
                art_is_active_against_mortality_and_transmission=True
            )
            add_intervention_scheduled(intervention_list=[art_mortality], campaign=campaign, start_day=start_day, node_ids=None,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday, coverage=cov),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=60),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_ARTMortalityTable")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        # only validate that the experiment ran successfully, as the mortality table is complex and hard to validate.

    def test_artstageagnosticdiag(self):
        startday = 180
        pos_event = "positive_event"
        neg_event = "negative_event"
        abp_tvmap = ValueMap(times=[2015, 2016], values=[100, 1])
        abt_tvmap = ValueMap(times=[2015, 2016], values=[0, 0.05])
        abw_tvmap = ValueMap(times=[2015], values=[10])
        cua_tvmap = ValueMap(times=[2015], values=[1])
        cbt_tvmap = ValueMap(times=[2015, 2016], values=[0.1, 1.4])
        cbw_tvmap = ValueMap(times=[2015], values=[4])

        def build_camp(campaign, start_day = 0):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day - 150,
                                       target_demographics_config=TDC(demographic_coverage=0.2))

            artstageagnosticdiag = HIVARTStagingCD4AgnosticDiagnostic(campaign=campaign,
                                                                      positive_diagnosis_event=pos_event,
                                                                      negative_diagnosis_event=neg_event,
                                                                      child_treat_under_age_in_years_threshold=cua_tvmap,
                                                                      child_by_who_stage=cbw_tvmap,
                                                                      child_by_tb=cbt_tvmap,
                                                                      adult_by_pregnant=abp_tvmap,
                                                                      adult_by_tb=abt_tvmap,
                                                                      adult_by_who_stage=abw_tvmap)
            add_intervention_scheduled(intervention_list=[artstageagnosticdiag], campaign=campaign, start_day=start_day)
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters, event_list):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=event_list))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=730),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=partial(build_reporters, event_list=[pos_event, neg_event])
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_artstageagnosticdiag")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        # Todo: find a way to test artstageagnosticdiag.

    def test_artstage4diag(
            self):  # todo: pending on https://github.com/InstituteforDiseaseModeling/emodpy-hiv/issues/39
        startday = 180
        pos_event = "positive_event"
        neg_event = "negative_event"
        threshold_tvmap = ValueMap(times=[2015, 2016], values=[800, 10000000])
        pregnant_tvmap = ValueMap(times=[2015, 2016], values=[600, 10000000])
        tb_tvmap = ValueMap(times=[2015, 2016], values=[500, 10000000])

        def build_camp(camp, start_day):
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=start_day - 150,
                                       target_demographics_config=TDC(demographic_coverage=0.2))

            artstage4diag = HIVARTStagingByCD4Diagnostic(campaign=camp,
                                                         positive_diagnosis_event=pos_event,
                                                         negative_diagnosis_event=neg_event,
                                                         cd4_threshold=threshold_tvmap,
                                                         if_pregnant=pregnant_tvmap,
                                                         if_active_tb=tb_tvmap)

            add_intervention_scheduled(intervention_list=[artstage4diag], campaign=camp, start_day=start_day)
            add_intervention_scheduled(intervention_list=[artstage4diag], campaign=camp, start_day=start_day + 365)
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event, neg_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=730),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_artstage4diag")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        # Todo: find a way to test artstage4diag.

    def test_drawblood(self):
        startday = 3
        coverage = 0.3
        pos_event = "positive_event"

        def build_camp(camp, start_day):
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=start_day - 2,
                                       target_demographics_config=TDC(demographic_coverage=0.3))
            drawblood = HIVDrawBlood(campaign=camp,
                                     positive_diagnosis_event=pos_event)
            add_intervention_scheduled(intervention_list=[drawblood], campaign=camp, start_day=start_day,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=10),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1, 3))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_drawblood")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)
        
        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            positive_event_count = len(report_df[report_df['Event_Name'] == pos_event])
            self.assertAlmostEqual(positive_event_count, 1000 * coverage, delta=28.4,
                                   msg=f'Test failed: expected {1000 * coverage} {pos_event} events.')

    def test_malecirc(self):
        start_day = 3
        coverage = 0.6

        def build_camp(camp):
            mc = MaleCircumcision(campaign=camp)
            add_intervention_scheduled(intervention_list=[mc], campaign=camp, start_day=start_day,
                                       target_demographics_config=TDC(demographic_coverage=coverage,
                                                                      target_gender=TargetGender.MALE))
            return camp

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=10),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_malecirc")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/InsetChart.json"]

        sims = self.platform.get_children_by_object(experiment)
        
        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'InsetChart.json'
            self.assertTrue(file_path.is_file())
            # validate result
            with file_path.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['Number of Circumcised Males']['Data']
            self.assertEqual(sum(new_infection[:start_day - 1]), 0,
                             msg='Test failed: expected no Circumcised Males before intervention start day.')
            self.assertAlmostEqual(new_infection[start_day - 1], 500 * coverage, delta=30,
                                   msg=f'Test failed: expected {500 * coverage} '
                                       f'Circumcised Males at intervention start day.')

    def test_modcoinf(self):
        start_day = 180
        coverage = 0.9

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=1)

            mc = MaleCircumcision(campaign=campaign)
            add_intervention_scheduled(intervention_list=[mc], campaign=campaign, start_day=start_day,
                                        target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(self.set_param_fn, duration=365),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_modcoinf")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        # Todo: find a way to test the STI coinfection status.

    def Skip_test_pmtct(self):
        start_day = 365
        coverage = 1

        def build_demog_with_fertelity():
            demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=1000, name=1, forced_id=1)
            path_to_csv = parent.parent / 'unittests' / 'inputs' / 'Malawi_Fertility_Historical.csv'
            demog.set_fertility(path_to_csv=path_to_csv)
            return demog

        def build_camp(camp):
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=1)

            pmtct = PMTCT(campaign=camp)
            add_intervention_scheduled(intervention_list=[pmtct], campaign=camp, start_day=start_day,
                                        target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            config.parameters.x_Birth = 1000
            # config.parameters.Enable_Maternal_Infection_Transmission = 1
            config.parameters.Maternal_Infection_Transmission_Probability = 1
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=['Births', 'NewInfectionEvent']))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            # This looks like a rounding error, the report saves time stamps with two digits after the point.
            # When 40 is used (Simulation_Duration = = 645) then the sim will end after day 645, in year 2,016.767123
            # In the last time step (645) before the sim ends there are NewInfectionEvents in year 2016.77 what let's the test fail.
            # see https://comps2.idmod.org/#explore/Simulations?filters=ExperimentId=00b0c26a-aeee-ec11-92ea-f0921c167864
            # Using 39.999 reduces the duration to 644 time steps and the test passes.
            config_builder=partial(setParamfn, duration=start_day + 39.999 * 7),  # Simulation_Duration = = 645
            demographics_builder=build_demog_with_fertelity,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_pmtct")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)
        
        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            new_infection = report_df[(report_df['Event_Name'] == 'NewInfectionEvent') & (report_df['Year'] != 2015)]

            m_t_c_t_before_intervention = new_infection[
                (new_infection['Year'] <= 2015 + start_day / 365) &  # noqa: W504
                (new_infection['Age'] == 1)]
            m_t_c_t__after_intervention = new_infection[(new_infection['Year'] > 2015 + start_day / 365) &  # noqa: W504
                                                        (new_infection['Age'] == 1)]

            self.assertGreater(len(m_t_c_t_before_intervention), 0,
                               msg='Test failed: There are no mother to child transmission before PMTCT intervention '
                                   'start day.')
            self.assertTrue(m_t_c_t__after_intervention.empty,
                            msg=f'Test failed: There are should not be any mother to child transmission after PMTCT'
                                f' intervention start day. Got {len(m_t_c_t__after_intervention)} MTCT events.')

    def test_prep(self):  # ControlledVaccine
        start_day = 1
        prep_events_list = ["PrEPDistributed", "STIDebut"]

        args = [[True, TargetGender.ALL],  # True = Baseline
                [False, TargetGender.ALL],  # False = PrEP iv, All
                [False, TargetGender.MALE],  # False = PrEP iv, Male
                [False, TargetGender.FEMALE]]  # False = PrEP iv, Female
        num_runs = 2
        ages = [15, 60]
        duration = 365 * 20

        def build_camp02(camp, args=[True, TargetGender.ALL]):

            baseline = args[0]
            gender = args[1]

            # OUTBREAK (baseline) for each simulation
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=1000,
                                       target_demographics_config=TDC(demographic_coverage=0.05))
            print(baseline, gender)

            # PrEPDistributed: Event signal registration.
            broadcast_event = BroadcastEvent(camp, "PrEPDistributed")

            if baseline:
                return camp  # This case will leave PrEPDistributed interventions out.

            efficacy_times = [0, 3650, 3651]  # 0 : 365 - 10 years of efficacy
            # NOTE !!! efficacies seems to have to be almost 1 in this sim for things to work.
            efficacy_values = [0.99, 0.99, 0]  # 90% : 100% 

            # PrEP INTERVENTION
            prep = ControlledVaccine(campaign=camp,
                                     waning_config=MapPiecewise(days=efficacy_times, effects=efficacy_values))

            for PrEPCampaign_Round in range(10):
                # Fixed  coverage
                prep_start_day = 500 + 365 * (PrEPCampaign_Round)
                prep_coverage = 0.1 * (PrEPCampaign_Round + 1)

                print(
                    f"Delivery step time:  {prep_start_day},  Start Year(campaign round):  {PrEPCampaign_Round}, Coverage: {prep_coverage}")
                add_intervention_scheduled(intervention_list=[prep, broadcast_event], campaign=camp, start_day=prep_start_day,
                                           target_demographics_config=TDC(demographic_coverage=prep_coverage,
                                                                          target_age_min=ages[0],
                                                                          target_age_max=ages[1],
                                                                          target_gender=gender))
            return camp

        def update_campaign(simulation, args):
            #   This callback function updates the coverage of the campaign. Function: "build_camp02"
            build_campaign_partial = partial(build_camp02, args=args)
            simulation.task.create_campaign_from_callback(build_campaign_partial)
            tag_value = str(args[1])
            if args[0]:
                tag_value = "BASELINE: " + tag_value

            # Return a tag that will be added to the simulation run.
            return {"Test_Case": tag_value}

        def setPrEPParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters, watched_events):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=watched_events))
            return reporters

        task = emod_task.EMODTask.from_defaults(eradication_path=str(self.eradication_path),
                                                   campaign_builder=partial(build_camp02),
                                                   schema_path=str(self.schema_path),
                                                   config_builder=partial(setPrEPParamfn, duration=duration),
                                                   demographics_builder=self.build_demog_from_template_node,
                                                   report_builder=partial(build_reporters,
                                                                          watched_events=prep_events_list)
                                                   )
        task.set_sif(str(manifest.sif_path), platform=self.platform)

        builder = SimulationBuilder()
        # Add SWEEP definitions to the builder. RUNS:
        builder.add_sweep_definition(self.update_sim_random_seed, range(num_runs))

        # Add SWEEP definitions to the builder. TEST CASES
        builder.add_sweep_definition(update_campaign, args=[a for a in args])

        # With the simulation builder and the task, we can create an EXPERIMENT.
        experiment = Experiment.from_builder(builder, task, name="HIV Test_prep_updated")

        # Run the experiment.
        experiment.run(wait_until_done=True, platform=self.platform)

        # Check that the experiment succeeded.
        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")

        import datetime as datetime
        prefix = datetime.datetime.now().strftime("%d_%H%M%S")  # To create a unique folder name (for plotting)

        # Specify the files to download.
        filenames = ["output/InsetChart.json", "output/ReportEventRecorder.csv", "campaign.json"]

        # Get the SIMULATIONS from the experiment.
        sims = self.platform.get_children_by_object(experiment)

        output_path = self.output_path / prefix / experiment.id
        all_reference = []
        all_test = []

        for idx, simulation in enumerate(sims):
            # DOWNLOAD files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            sim_path = str(simulation.uid)

            # VALIDATE files exist
            ins_chart_file = output_path / sim_path / 'output' / 'InsetChart.json'
            csv_filename = output_path / sim_path / 'output' / 'ReportEventRecorder.csv'
            campaign_file = output_path / sim_path / 'campaign.json'

            self.assertTrue(ins_chart_file.is_file())
            self.assertTrue(csv_filename.is_file())
            self.assertTrue(campaign_file.is_file())

            # VALIDATE result
            with ins_chart_file.open(mode='r') as json_file:
                inset_chart = json.load(json_file)

            new_infection = inset_chart['Channels']['New Infections']['Data']
            self.assertEqual(sum(new_infection[:start_day]), 0,
                             msg='Test failed: expected no new infection before outbreak start day.')

            if simulation.tags[
                'Test_Case'] != "BASELINE: TargetGender.ALL":  # If is not the baseline it will check the presence of PrEPDistributed events
                df = pd.read_csv(csv_filename)
                gender = [simulation.tags['Test_Case']]
                if gender[0] == 'TargetGender.ALL':
                    gender = ['M', 'F']  # Converts "All" to ["M", "F"] to be used in the query
                    all_test.append(ins_chart_file)  # Save the InsetChart.json file name to be used later
                elif gender[0] == 'TargetGender.FEMALE':
                    gender = ['F']
                else:
                    gender = ['M']

                print(f"\n\nSimulation: {sim_path}, Gender {gender}")
                prep_events = df[(df['Event_Name'] == "PrEPDistributed") & (df['Gender'].isin(gender))]

                # VALIDATE if there are PrEPDistributed events for expected Gender
                self.assertGreater(len(prep_events), 0, msg='Test failed: There are no PrEPDistributed events.')

                # VALIDATE  if the mininum and maximum ages of the PrEPDistributed events are within the expected range
                self.assertGreater(prep_events['Age'].min(), 365 * ages[0],
                                   msg=f'Test failed: PrEPDistributed events were distributed to individuals younger than {ages[0]} {prep_events["Age"].min()}')
                self.assertLess(prep_events['Age'].max(), 365 * ages[1],
                                msg=f'Test failed: PrEPDistributed events were distributed to individuals older than {ages[1]} {prep_events["Age"].max()}')
            else:
                # If is the baseline it will just save the reference InsetChart.json to be used later
                all_reference.append(ins_chart_file)

        # PROCEED TO VALIDATE THE PREVALENCE OF THE BASELINE AND TEST      
        channels_subset = ["Prevalence (Females, 15-49)",
                           "Prevalence (Males, 15-49)",
                           "Prevalence among Sexually Active"]

        run = 0

        with all_reference[run].open(mode='r') as json_file:
            baseline = json.load(json_file)

        with all_test[run].open(mode='r') as json_file:
            test = json.load(json_file)

        # VALIDATE the Prevalence of the baseline and Test, the PREVALENCE should be lower for the Test
        for channel in channels_subset:
            if baseline is not None and test is not None:
                a = pd.DataFrame(baseline['Channels'][channel]['Data']).mean()
                b = pd.DataFrame(test['Channels'][channel]['Data']).mean()
                print(f"\n\n{channel}:\t Reference: {a.min()}\n\nTest: {b.min()}")
                self.assertGreater(a.min(),
                                   b.min(),
                                   msg=f'Test failed: {channel} \nThe resulting Prevalence is expected to be '
                                       f'lower WITH the intervention, but it was not: \n'
                                       f'Without Intervention (baseline): {a.min()}, \n'
                                       f'With Intervention: {b.min()}')
            else:
                self.assertIsNotNone(test, msg='Test failed: There are no PrEPDistributed events.')

    def test_random(self):
        start_day = 1
        coverage = 1
        choice_1 = 'OnArt1'
        choice_2 = 'OnArt2'
        choice_1_p = 0.1
        choice_2_p = 0.9

        def build_camp(camp):
            randomchoice = HIVRandomChoice(campaign=camp,
                                           choice_names=[choice_1, choice_2],
                                           choice_probabilities=[choice_1_p, choice_2_p])
            add_intervention_scheduled(intervention_list=[randomchoice],
                                       campaign=camp,
                                       start_day=start_day,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[choice_1, choice_2]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_random")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            choice_1_count = len(report_df[report_df['Event_Name'] == choice_1])
            choice_2_count = len(report_df[report_df['Event_Name'] == choice_2])

            self.assertAlmostEqual(choice_1_count / choice_2_count, choice_1_p / choice_2_p, delta=0.01,
                                   msg=f'Test failed: the ratio of {choice_1} / {choice_2} should be about {choice_1_p}'
                                       f' / {choice_2_p}, got {choice_1_count / choice_2_count}.')

    def test_rapiddiag(self):
        start_day = 2
        coverage = 1
        ob_coverage = 0.8
        pos_event = 'HIV_positive'
        neg_event = 'HIV_negative'

        def build_camp(camp):
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=start_day - 1,
                                        target_demographics_config=TDC(demographic_coverage=ob_coverage))

            rapid_diag = HIVRapidHIVDiagnostic(campaign=camp,
                                               positive_diagnosis_event=pos_event,
                                               negative_diagnosis_event=neg_event,
                                               base_sensitivity=1)
            add_intervention_scheduled(intervention_list=[rapid_diag], campaign=camp, start_day=start_day,
                                        target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event, neg_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_rapiddiag")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            pos_event_count = len(report_df[report_df['Event_Name'] == pos_event])
            neg_event_count = len(report_df[report_df['Event_Name'] == neg_event])

            self.assertAlmostEqual(pos_event_count, 1000 * ob_coverage, delta=20,
                                   msg=f'Test failed: expected about {1000 * ob_coverage} {pos_event} events, '
                                       f'got {pos_event_count}.')
            self.assertAlmostEqual(neg_event_count, 1000 * (1 - ob_coverage), delta=20,
                                   msg=f'Test failed: expected about {1000 * (1 - ob_coverage)} {neg_event} events, '
                                       f'got {neg_event_count}.')

    def test_sigmoiddiag(self):
        total_year = 4
        start_day = 2
        coverage = 1
        ob_coverage = 1
        pos_event = 'HIV_positive'
        neg_event = 'HIV_negative'
        ramp_min = 0.1
        ramp_max = 0.9
        ramp_midyear = 2017
        ramp_rate = 2

        def build_camp(camp):
            first = True
            for half_year in range(total_year * 2 + 1):
                ob = OutbreakIndividual(campaign=camp)
                add_intervention_scheduled(intervention_list=[ob], campaign=camp,
                                           start_day=start_day + half_year * 182 - 1,
                                           target_demographics_config=TDC(demographic_coverage=ob_coverage))
                sigmoiddiag = HIVSigmoidByYearAndSexDiagnostic(campaign=camp,
                                                               positive_diagnosis_event=pos_event,
                                                               negative_diagnosis_event=neg_event,
                                                               year_sigmoid=Sigmoid(ramp_min, ramp_max, ramp_midyear, ramp_rate))
                add_intervention_scheduled(intervention_list=[sigmoiddiag], campaign=camp,
                                           start_day=start_day + half_year * 182,
                                           target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event, neg_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=365 * total_year + 1),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed,
                                     range(1, 2))  # different Run_Number makes the test pass

        experiment = Experiment.from_builder(builder, task, name="HIV Test_sigmoiddiag")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            base_year = 2015
            test_years = []
            positive_probability = []
            for half_year in range(total_year * 2 + 1):
                current_year = base_year + round((half_year * 182 + start_day) / 365, 2)
                pos_event_count = len(report_df[(report_df['Event_Name'] == pos_event)
                                                & (report_df['Year'] == current_year)])
                neg_event_count = len(report_df[(report_df['Event_Name'] == neg_event)
                                                & (report_df['Year'] == current_year)
                                                & (report_df['HasHIV'] == 'Y')])
                test_years.append(current_year)
                positive_probability.append(pos_event_count / (pos_event_count + neg_event_count))

            self.assertTrue(all(positive_probability[i] <= positive_probability[i + 1] for i in
                                range(len(positive_probability) - 1)),
                            msg=f"Test failed: positive probability should be in ascending order, got {positive_probability}.")
            # we are linearly ramping FROM 0.1 upward, so the first value should be 0.1 (hence, >= in the test)
            self.assertGreaterEqual(min(positive_probability), ramp_min,
                                    msg=f'Test failed: positive probability should not be less than ramp_min = {ramp_min}, '
                                        f'got min(positive_probability) = {min(positive_probability)}.')
            # we are ramping up to 0.9, so 0.9 is the maximum value we could achieve (hence <= in the test)
            self.assertLessEqual(max(positive_probability), ramp_max,
                                 msg=f'Test failed: positive probability should not be greater than ramp_max = {ramp_max}, '
                                     f'got max(positive_probability) = {max(positive_probability)}.')

            self.assertAlmostEqual(positive_probability[0], ramp_min, delta=0.05,
                                   msg=f'Test failed: expected positive probability about {ramp_min} at year '
                                       f'{test_years[0]}, got {positive_probability[0]}.')
            self.assertAlmostEqual(positive_probability[-1], ramp_max, delta=0.05,
                                   msg=f'Test failed: expected positive probability about {ramp_max} at year '
                                       f'{test_years[-1]}, got {positive_probability[-1]}.')
            self.assertAlmostEqual(positive_probability[4], (ramp_min + ramp_max) / 2, delta=0.05,
                                   msg=f'Test failed: expected positive probability about {(ramp_min + ramp_max) / 2} '
                                       f'at year {test_years[4]}, got {positive_probability[4]}.')

    def test_stipostdebut(self):
        start_day = 2
        coverage = 1
        ob_coverage = 1
        pos_event = 'PostDebut'
        neg_event = 'PreDebut'

        def build_camp(camp):
            ob = OutbreakIndividual(campaign=camp)
            add_intervention_scheduled(intervention_list=[ob], campaign=camp, start_day=1,
                                       target_demographics_config=TDC(demographic_coverage=ob_coverage))
            stipostdebut = STIIsPostDebut(campaign=camp,
                                          positive_diagnosis_event=pos_event,
                                          negative_diagnosis_event=neg_event)
            add_intervention_scheduled(intervention_list=[stipostdebut], campaign=camp, start_day=start_day,
                                        target_demographics_config=TDC(demographic_coverage=coverage))
            return camp

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            config.parameters.Report_Event_Recorder_Events = [pos_event, neg_event]
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event, neg_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_stipostdebut")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            pos_event_df = report_df[report_df['Event_Name'] == pos_event]
            neg_event_df = report_df[report_df['Event_Name'] == neg_event]

            toddler = pos_event_df[pos_event_df['Age'] < 365 * 5]
            self.assertTrue(toddler.empty, msg=f'Test failed: there are should not be any toddler with {pos_event} '
                                               f'event.')

            self.assertGreater(len(neg_event_df), 0,
                               msg=f'Test failed: there are should be some {neg_event} events.')

    def test_yearandsexdiag(self):
        total_year = 4
        start_day = 2
        coverage = 1
        ob_coverage = 1
        pos_event = 'HIV_positive'
        neg_event = 'HIV_negative'
        tvmap = ValueMap(times=[2015, 2016, 2017, 2018], values=[0.2, 0.75, 0, 1])

        def build_camp(campaign):
            first = True
            for year in range(total_year + 1):
                ob = OutbreakIndividual(campaign=campaign)
                add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day + year * 365 - 1,
                                           target_demographics_config=TDC(demographic_coverage=ob_coverage))

                yearandsexdiag = HIVPiecewiseByYearAndSexDiagnostic(campaign=campaign,
                                                                    positive_diagnosis_event=pos_event,
                                                                    negative_diagnosis_event=neg_event,
                                                                    time_value_map=tvmap)
                add_intervention_scheduled(intervention_list=[yearandsexdiag], campaign=campaign,
                                            start_day=start_day + year * 365,
                                            target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[pos_event, neg_event]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=365 * total_year + 2),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_yearandsexdiag")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            base_year = 2015
            test_years = []
            positive_probabilities = []
            for year in range(total_year + 1):
                current_year = base_year + round((year * 365 + start_day) / 365, 2)
                pos_event_count = len(report_df[(report_df['Event_Name'] == pos_event)
                                                & (report_df['Year'] == current_year)])
                neg_event_count = len(report_df[(report_df['Event_Name'] == neg_event)
                                                & (report_df['Year'] == current_year)
                                                & (report_df['HasHIV'] == 'Y')])
                test_years.append(current_year)
                positive_probability = pos_event_count / (pos_event_count + neg_event_count)
                positive_probabilities.append(positive_probability)

                def get_expected_probability(time, vm):
                    def get_index_from_list_value():
                        for i, v in enumerate(vm._times):
                            if time <= v:
                                return i
                        return len(vm._times) - 1
                    i = get_index_from_list_value()
                    return vm._values[i]

                if int(current_year) in tvmap._times:
                    expected_probability = get_expected_probability(int(current_year), tvmap)
                elif int(current_year) > max(tvmap._times):
                    expected_probability = get_expected_probability(max(tvmap._times), tvmap)
                else:
                    expected_probability = get_expected_probability(min(tvmap._times), tvmap)

                self.assertAlmostEqual(positive_probability, expected_probability, delta=0.05,
                                       msg=f'Test failed: expected positive_probability about {expected_probability}'
                                           f' at year {current_year}, got {positive_probability}')

    def test_cascade_triggered_event_common(self):
        startday = 2
        in_trigger = "NewInfectionEvent"
        event_name = "I_am_infected"

        def build_camp(campaign, start_day):
            broadcast_event = BroadcastEvent(campaign, event_name)
            add_intervention_triggered(intervention_list=[broadcast_event], campaign=campaign, start_day=start_day - 1,
                                       triggers_list=[in_trigger])
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=start_day,
                                       target_demographics_config=TDC(demographic_coverage=1))
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[event_name]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp, start_day=startday),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=10),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_cascade_triggered_event_common")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_count = len(report_df[report_df['Event_Name'] == event_name])
            self.assertAlmostEqual(event_count, 1000, delta=10,
                                   msg=f'Test failed: expected about {1000} {event_count} events.')

    def test_cascade_add_choice(self):
        ob_start_day = 2
        sympto_signal = "NewInfectionEvent"
        get_tested_signal = 'get_tested_signal'

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)
            choice = HIVRandomChoice(campaign=campaign, choice_names=[get_tested_signal, "Ignore"],
                                     choice_probabilities=[0.4, 0.6])
            add_intervention_triggered(intervention_list=[choice], campaign=campaign, start_day=1,
                                       triggers_list=[sympto_signal], event_name="Decide_On_Testing")
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[get_tested_signal]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=10),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_add_choice")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_df = report_df[report_df['Event_Name'] == get_tested_signal]
            base_year = 2015
            trigger_year = base_year + round(ob_start_day / 365, 2)
            count = len(event_df[event_df['Year'] == trigger_year])
            self.assertAlmostEqual(count, 1000 * 0.4, delta=30,
                                   msg=f'Test failed: expected about {1000 * 0.5} {get_tested_signal} events at year '
                                       f'{trigger_year}, got {count}.')

    def test_cascade_add_test(self):
        ob_start_day = 2
        get_tested_signal = "NewInfectionEvent"
        builtin_pos_event = "HIVPositiveTest"
        builtin_delay = 30

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

            test = HIVRapidHIVDiagnostic(campaign=campaign, positive_diagnosis_event=builtin_pos_event,
                                         negative_diagnosis_event="HIVNegativeTest", base_sensitivity=1)
            add_intervention_triggered(intervention_list=[test], campaign=campaign, start_day=1,
                                       delay_distribution=ConstantDistribution(builtin_delay),
                                       triggers_list=[get_tested_signal], event_name="Test")

            return campaign

        def setParamfn(config, duration, event_list):
            self.set_param_fn(config, duration)
            # leaving manual Report_Event_Recorder_Events setting for this test
            config.parameters.Report_Event_Recorder_Events = event_list
            return config

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=35, event_list=[builtin_pos_event]),
            demographics_builder=self.build_demog_from_template_node
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_add_test")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_df = report_df[report_df['Event_Name'] == builtin_pos_event]
            base_year = 2015
            trigger_year = base_year + round((ob_start_day + builtin_delay) / 365, 2)
            count = len(event_df[event_df['Year'] == trigger_year])
            self.assertAlmostEqual(count, 1000, delta=50,
                                   msg=f'Test failed: expected about {1000} {builtin_pos_event} events at year '
                                       f'{trigger_year}, got {count}.')

    def test_cascade_trigger_art_from_pos_test(self):
        ob_start_day = 2
        input_signal = "NewInfectionEvent"
        output_signal = "StartTreatment"
        delay = 15

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

            broadcast_event = BroadcastEvent(campaign, output_signal)
            add_intervention_triggered(intervention_list=[broadcast_event], campaign=campaign, start_day=1,
                                       delay_distribution=ConstantDistribution(delay),
                                       triggers_list=[input_signal], event_name="NeedTreatment")

            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[output_signal]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=35),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_cascade_trigger_art_from_pos_test")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_df = report_df[report_df['Event_Name'] == output_signal]
            base_year = 2015
            trigger_year = base_year + round((ob_start_day + delay) / 365, 2)
            count = len(event_df[event_df['Year'] == trigger_year])
            self.assertAlmostEqual(count, 1000, delta=50,
                                   msg=f'Test failed: expected about {1000} {output_signal} events at year '
                                       f'{trigger_year}, got {count}.')

    def test_cascade_add_art_from_trigger(self):
        ob_start_day = 20
        signal = "NewInfectionEvent"
        builtin_output_signal = 'StartedART'

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

            art = AntiretroviralTherapy(campaign=campaign)
            add_intervention_triggered(intervention_list=[art], campaign=campaign, start_day=1,
                                       triggers_list=[signal], event_name="ART on trigger")
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[builtin_output_signal]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=25),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_cascade_add_art_from_trigger")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_df = report_df[report_df['Event_Name'] == builtin_output_signal]
            base_year = 2015
            trigger_year = base_year + round(ob_start_day / 365, 2)
            count = len(event_df[event_df['Year'] == trigger_year])
            self.assertAlmostEqual(count, 1000, delta=50,
                                   msg=f'Test failed: expected about {1000} {builtin_output_signal} events at year '
                                       f'{trigger_year}, got {count}.')

    def test_cascade_trigger_art(self):
        timestep = 10
        coverage = 0.7
        trigger = "ARTTriggerSignal"

        def build_camp(campaign):
            broadcast_event = BroadcastEvent(campaign, trigger)
            add_intervention_scheduled(intervention_list=[broadcast_event], campaign=campaign, start_day=timestep,
                                       target_demographics_config=TDC(demographic_coverage=coverage))
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[trigger]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=35),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_cascade_trigger_art")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            event_df = report_df[report_df['Event_Name'] == trigger]
            base_year = 2015
            trigger_year = base_year + round(timestep / 365, 2)
            count = len(event_df[event_df['Year'] == trigger_year])
            self.assertAlmostEqual(count, 1000 * coverage, delta=50,
                                   msg=f'Test failed: expected about {1000 * coverage} {trigger} events at year '
                                       f'{trigger_year}, got {count}.')

    def test_cascade_helper_logic(self):
        ob_timestep = 1
        ob_coverage = 1

        default_delay = 30
        base_year = 2015
        duration = 365
        # new_infection_event = "NewInfectionEvent"
        start_treatment = "StartTreatment"
        started_ART = "StartedART"
        positive_test = "HIVPositiveTest"
        negative_test = "HIVNegativeTest"
        get_tested = "GetTested"
        ignore = "Ignore"
        symptomatic = "NewlySymptomatic"
        disease_deaths = "DiseaseDeaths"
        non_disease_deaths = "NonDiseaseDeaths"

        def build_camp(campaign):
            ob = OutbreakIndividual(campaign=campaign)
            add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_timestep,
                                       target_demographics_config=TDC(demographic_coverage=ob_coverage))
            choice = HIVRandomChoice(campaign=campaign, choice_names=["GetTested", "Ignore"],
                                     choice_probabilities=[0.5, 0.5])
            add_intervention_triggered(intervention_list=[choice], campaign=campaign, start_day=1,
                                       triggers_list=["NewlySymptomatic"], event_name="Decide_On_Testing")
            test = HIVRapidHIVDiagnostic(campaign=campaign, positive_diagnosis_event="HIVPositiveTest",
                                         negative_diagnosis_event="HIVNegativeTest", base_sensitivity=1)
            add_intervention_triggered(intervention_list=[test], campaign=campaign, start_day=1,
                                       delay_distribution=ConstantDistribution(30),
                                       triggers_list=["GetTested"], event_name="Test")
            broadcast_event = BroadcastEvent(campaign, "StartTreatment")
            add_intervention_triggered(intervention_list=[broadcast_event], campaign=campaign, start_day=1,
                                       delay_distribution=ConstantDistribution(30),
                                       triggers_list=["HIVPositiveTest"], event_name="NeedTreatment")
            art = AntiretroviralTherapy(campaign=campaign)
            add_intervention_triggered(intervention_list=[art], campaign=campaign, start_day=1,
                                       triggers_list=["StartTreatment"], event_name="ART on trigger")
            return campaign

        def setParamfn(config, duration):
            self.set_param_fn(config, duration)
            return config

        def is_dead(event):
            return event in [disease_deaths, non_disease_deaths]

        def build_reporters(reporters):
            reporters.add(ReportEventRecorder(reporters_object=reporters,
                                              event_list=[start_treatment, started_ART,  # new_infection_event,
                                                          positive_test, negative_test, get_tested,
                                                          symptomatic, ignore,
                                                          disease_deaths, non_disease_deaths]))
            return reporters

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=duration),
            demographics_builder=self.build_demog_from_template_node,
            report_builder=build_reporters
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))

        experiment = Experiment.from_builder(builder, task, name="HIV Test_cascade_helper_logic")

        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = ["output/ReportEventRecorder.csv"]

        sims = self.platform.get_children_by_object(experiment)

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=self.output_path)
            # validate files exist
            local_path = self.output_path / str(simulation.uid)
            file_path = local_path / 'output' / 'ReportEventRecorder.csv'
            self.assertTrue(file_path.is_file())
            # validate result
            report_df = pd.read_csv(file_path)

            symptomatic_df = self.check_event_counts(symptomatic, get_tested, ignore, positive_test, report_df,
                                                     started_ART)

            for ind_id, year in zip(symptomatic_df['Individual_ID'], symptomatic_df['Year']):
                df = report_df[report_df['Individual_ID'] == ind_id]
                if not is_dead(df["Event_Name"].iloc[0]):

                    self.assertEqual(df["Event_Name"].iloc[0], symptomatic)

                    # test add_choice
                    self.check_add_choice(df, disease_deaths, get_tested, ignore, ind_id, non_disease_deaths)

                    if df["Event_Name"].iloc[1] == get_tested and \
                            year + round(default_delay / 365, 2) < base_year + duration / 365 and \
                            not is_dead(df["Event_Name"].iloc[2]):

                        # test add_test
                        self.check_add_test(default_delay, df, ind_id, positive_test, year)
                        if year + round(2 * default_delay / 365, 2) < base_year + duration / 365 and \
                                not is_dead(df["Event_Name"].iloc[3]):
                            # test trigger_art_from_pos_test
                            self.check_trigger_art_from_pos_test(default_delay, df, ind_id, positive_test,
                                                                 start_treatment, year)

                            # test add_art_from_trigger
                            self.check_add_art_from_trigger(df, ind_id, start_treatment, started_ART)
        pass

    def check_add_art_from_trigger(self, df, ind_id, start_treatment, started_ART):
        self.assertEqual(df["Event_Name"].iloc[4], started_ART,
                         msg=f"Test failed: individual {ind_id} should receive {started_ART} "
                             f"event at the same day when they receive {start_treatment} "
                             f"event, got {df['Event_Name'].iloc[4]}."
                         )
        self.assertEqual(df["Year"].iloc[4], df["Year"].iloc[3],
                         msg=f"Test failed: individual {ind_id} should receive {started_ART} "
                             f"event at the same day {df['Year'].iloc[3]} when they receive "
                             f"{start_treatment} event, got {df['Year'].iloc[4]}."
                         )

    def check_trigger_art_from_pos_test(self, default_delay, df, ind_id, positive_test, start_treatment, year):
        self.assertEqual(df["Event_Name"].iloc[3], start_treatment,
                         msg=f"Test failed: individual {ind_id} should receive {start_treatment} "
                             f"event {default_delay} days after they receive {positive_test} "
                             f"event, got {df['Event_Name'].iloc[3]}."
                         )
        self.assertAlmostEqual(df["Year"].iloc[3], year + round(2 * default_delay / 365, 2),
                               delta=0.02,
                               msg=f"Test failed: individual {ind_id} should receive "
                                   f"{start_treatment} event at year "
                                   f"{year + round(2 * default_delay / 365, 2)}, got "
                                   f"{df['Year'].iloc[3]}."
                               )

    def check_add_test(self, default_delay, df, ind_id, positive_test, year):
        self.assertEqual(df["Event_Name"].iloc[2], positive_test,
                         msg=f"Test failed: individual {ind_id} should receive {positive_test} "
                             f"event {default_delay} days after they become symptomatic, got "
                             f"{df['Event_Name'].iloc[2]}."
                         )
        self.assertAlmostEqual(df["Year"].iloc[2], year + round(default_delay / 365, 2), delta=0.02,
                               msg=f"Test failed: individual {ind_id} should receive {positive_test} "
                                   f"event at year {year + round(default_delay / 365, 2)}, got "
                                   f"{df['Year'].iloc[2]}.")

    def check_add_choice(self, df, disease_deaths, get_tested, ignore, ind_id, non_disease_deaths):
        self.assertIn(df["Event_Name"].iloc[1], [get_tested, ignore, disease_deaths, non_disease_deaths],
                      msg=f"Test failed: individual {ind_id} should receive only one of the 4 events after "
                          f"they become symptomatic: {get_tested}, {ignore}, {disease_deaths}, "
                          f"{non_disease_deaths}, got {df['Event_Name'].iloc[1]}.")
        self.assertEqual(df["Year"].iloc[1], df["Year"].iloc[0],
                         msg=f"Test failed: individual {ind_id} should receive {df['Event_Name'].iloc[1]} "
                             f"event at the same day when they become symptomatic {df['Year'].iloc[0]}: got"
                             f" {df['Year'].iloc[1]}.")

    def check_event_counts(self, symptomatic, get_tested, ignore, positive_test, report_df, started_ART):
        symptomatic_df = report_df[(report_df['Event_Name'] == symptomatic) & (report_df["OnART"] == "N")]
        symptomatic_count = len(symptomatic_df)
        # test_symptomatic_df = report_df[(report_df['Event_Name'] == HIV_symptomatic)]
        # test_symptomatic_df = test_symptomatic_df[test_symptomatic_df.duplicated(['Individual_ID'])]
        self.assertGreater(symptomatic_count, 0,
                           msg=f'Test failed: expected some {symptomatic} events, got {symptomatic_count}.')
        get_tested_count = len(report_df[report_df['Event_Name'] == get_tested])
        self.assertAlmostEqual(get_tested_count, symptomatic_count * 0.5, delta=10,  # random choice
                               msg=f'Test failed: expected about {symptomatic_count * 0.5} {get_tested} '
                                   f'events, got {get_tested_count}.')
        ignore_count = len(report_df[report_df['Event_Name'] == ignore])
        self.assertAlmostEqual(ignore_count, symptomatic_count - get_tested_count, delta=5,  # death
                               msg=f'Test failed: expected about {symptomatic_count - get_tested_count} {ignore} '
                                   f'events, got {ignore_count}.')
        positive_test_count = len(report_df[report_df['Event_Name'] == positive_test])
        self.assertAlmostEqual(positive_test_count, get_tested_count, delta=40,  # delayed
                               msg=f'Test failed: expected about {get_tested_count} {positive_test} '
                                   f'events, got {positive_test_count}.')
        started_ART_count = len(report_df[report_df['Event_Name'] == started_ART])
        self.assertAlmostEqual(started_ART_count, positive_test_count, delta=20,  # delayed
                               msg=f'Test failed: expected about {positive_test_count} {started_ART} '
                                   f'events, got {started_ART_count}.')
        return symptomatic_df


if __name__ == '__main__':
    unittest.main()
