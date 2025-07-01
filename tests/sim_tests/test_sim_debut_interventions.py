from functools import partial
import unittest
import sys
from pathlib import Path
import os
import json
import pandas as pd
import datetime as datetime
from idmtools.core import ItemType
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task
from emodpy_hiv.demographics.hiv_demographics import HIVDemographics

from emodpy_hiv.campaign.individual_intervention import OutbreakIndividual, SetSexualDebutAge
from emodpy_hiv.campaign.common import TargetDemographicsConfig, TargetGender, ValueMap
from emodpy_hiv.campaign.distributor import add_intervention_scheduled, add_intervention_reference_tracking

from emodpy_hiv.reporters.reporters import ReportFilter, ReportEventRecorder, ReportHIVByAgeAndGender, DemographicsReport
from emodpy_hiv.utils.emod_enum import SettingType
from emodpy_hiv.utils.targeting_config import IsPostDebut

manifest_directory = Path(__file__).resolve().parent.parent
sys.path.append(str(manifest_directory))
import manifest
from base_sim_test import BaseSimTest


class TC:
    # Test Case parameters - generic
    Start_Year = 1950.5
    End_Year = 2050.0
    Target_Age_Max = None  # This is user specified, it should not be provided??
    Target_Age_Min = None  # This is user specified, it should not be provided??
    Update_Period = 30.416667
    Distributed_Event_Trigger = "Setting_Age_Sexual_Debut"


class Files():
    config = "config.json"
    campaign = "campaign.json"
    ReportEventRecorder = "output/ReportEventRecorder.csv"
    ReportHIVByAgeAndGender = "output/ReportHIVByAgeAndGender.csv"


files = Files()

filenames = [files.config,
             files.campaign,
             files.ReportEventRecorder,
             files.ReportHIVByAgeAndGender]


class TestDebutInterventions(BaseSimTest):
    def update_sim_random_seed(self, simulation, value):
        simulation.task.config.parameters.Run_Number = value
        return {"Run_Number": value}

    def update_demographic_filename(self, simulation, value):
        filename = f"demographics_{value}_PFARates.json"
        simulation.task.config.parameters.Demographics_Filenames = [filename]
        return {"PFA_RelForm_Case": value}

    def global_build_demog_from_template_node(self):
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=1000, name="1", forced_id=1,
                                                   default_society_template="PFA-Southern-Africa")
        return demog

    @staticmethod
    def global_set_param_fn(config, duration=24000, timestep=30):
        config.parameters.Simulation_Type = "HIV_SIM"  # this should be set in the package.
        config.parameters.Simulation_Duration = duration  # maybe this should be a team-wide default?
        config.parameters.Simulation_Timestep = timestep
        # config hacks until schema fixes arrive
        config.parameters.Male_To_Female_Relative_Infectivity_Ages = [15, 25, 35]
        config.parameters.Male_To_Female_Relative_Infectivity_Multipliers = [5, 1, 0.5]
        config.parameters.Maternal_Infection_Transmission_Probability = 0
        config.parameters['logLevel_default'] = "WARNING"  # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys
        config.parameters.Incubation_Period_Distribution = "CONSTANT_DISTRIBUTION"
        config.parameters.Custom_Individual_Events = [
            "Setting_Age_Sexual_Debut"
        ]
        config.parameters.Base_Year = 1950

        return config

    @staticmethod
    def report_builder(reporters, age_bins=None):
        if not age_bins:
            age_bins = [0, 12, 13, 15, 16, 17, 18, 19, 20, 25, 30]
        reporters.add(ReportEventRecorder(reporters_object=reporters,
                                          event_list=[
                                              "Setting_Age_Sexual_Debut",
                                              "STIDebut"
                                          ]))
        reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                              report_filter=ReportFilter(start_year=1960, end_year=2100),
                                              reporting_period=30.416667,
                                              collect_gender_data=True,
                                              collect_age_bins_data=age_bins,
                                              add_relationships=True,
                                              add_concordant_relationships=False))
        reporters.add(DemographicsReport(reporters_object=reporters))
        return reporters

    # --------------------------------------------
    # Tests sex debut with a WEIBULL distribution
    # --------------------------------------------
    def test_sexualdebut_WEIBULL(self):
        start_day = 2
        test_name = self.id().split('.')[-1]

        def setParamfn(config, duration):
            # uses the global set_param_fn to set parameters
            config = self.global_set_param_fn(config)

            return config

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.global_build_demog_from_template_node,
            report_builder=self.report_builder
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))
        experiment = Experiment.from_builder(builder, task, name=F"HIV {test_name}")
        experiment.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = [files.ReportEventRecorder, files.ReportHIVByAgeAndGender, files.config]
        sims = self.platform.get_children_by_object(experiment)

        testtime = datetime.datetime.now().strftime("%d_%H%M%S")  # To create a unique folder name (for plotting)
        output_path = Path(os.path.join(self.test_folder, testtime)).resolve()

        for simulation in sims:
            # download files from simulation
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            local_path = output_path / str(simulation.uid)
            self.validate_reports_basics(local_path, [files.ReportEventRecorder, files.ReportHIVByAgeAndGender])
            self.validate_ReportEventRecorder(local_path)
            self.validate_simulation_config_file(local_path, "WEIBULL")

    # ------------------------------------------------------------
    # SETSEXUALDEBUT test with StandardEventCoordinator  --- 
    # ------------------------------------------------------------

    def test_setsexualdebut_New_intervention_event_w_DEFAULTS(self):
        start_day = 2
        test_name = self.id().split('.')[-1]

        def build_camp(camp):
            """ DEFAULT VALUES...
            Testing:  Base case campaign with 1 intervention and 1 event
            Values:     Default values
            Method Signature: 
                    new_intervention_event( camp, 
                                            start_day=1, 
                                            coverage=1.0,
                                            target_gender="All",
                                            target_demographic="Everyone",
                                            node_ids=None):
            """
            outbreak_event = OutbreakIndividual(campaign=camp)
            target_demographics_config = TargetDemographicsConfig(demographic_coverage=0.4)
            add_intervention_scheduled(camp,
                                       intervention_list=[outbreak_event],
                                       start_day=start_day - 2,
                                       target_demographics_config=target_demographics_config)

            debut_event = SetSexualDebutAge(campaign=camp, setting_type=SettingType.CURRENT_AGE,
                                            distributed_event_trigger="Setting_Age_Sexual_Debut")
            add_intervention_scheduled(camp,
                                       intervention_list=[debut_event],
                                       start_day=1)
            return camp

        def setParamfn(config, duration):
            # uses the global set_param_fn to set parameters
            config = self.global_set_param_fn(config)
            config.parameters.Sexual_Debut_Age_Setting_Type = "FROM_INTERVENTION"
            return config

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.global_build_demog_from_template_node,
            report_builder=self.report_builder
        )

        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))
        experiment = Experiment.from_builder(builder, task, name=f"HIV {test_name}")
        experiment.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        filenames = [files.ReportEventRecorder,
                     files.ReportHIVByAgeAndGender,
                     files.config,
                     files.campaign]

        sims = self.platform.get_children_by_object(experiment)

        testtime = datetime.datetime.now().strftime("%d_%H%M%S")  # Adding a more intuitive folder name.
        output_path = Path(os.path.join(self.test_folder, testtime)).resolve()

        for simulation in sims:
            # download simulation's output files from COMPS 
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            local_path = output_path / str(simulation.uid)
            self.validate_reports_basics(local_path, [files.ReportEventRecorder, files.ReportHIVByAgeAndGender])
            self.validate_ReportEventRecorder(local_path)
            self.validate_simulation_config_file(local_path, "FROM_INTERVENTION")

    # ------------------------------------------------------------

    def test_track_sexual_debut_intervention_CURRENTAGE(self):
        # TODO: Bugs logged: 1) - Wrong Start and End Year data type, 2)- Target_Age_Max not used. 

        start_day = 2
        test_name = self.id().split('.')[-1]
        args = [[1, ValueMap(times=[1960, 1970, 1980], values=[0.1, 0.1, 0.1])],
                [2, ValueMap(times=[1960, 1970, 1980], values=[0.3, 0.3, 0.3])],
                [3, ValueMap(times=[1960, 1970, 1980], values=[0.8, 0.5, 0.2])]]

        def build_camp(camp, xtra_args=None):
            """
            -- DEFAULTS--
            Start_Year = 1960.5,          
            End_Year = 2050,             
            node_ids = None,
            Target_Age_Max = 125,
            Target_Age_Min = 0,
            Target_Demographic = "Everyone",
            Target_Gender = "All",
            Update_Period = 30.416667,
            Distributed_Event_Trigger = "Setting_Age_Sexual_Debut",
            Setting_Type = "CURRENT_AGE",
            Age_Years = None
            """
            if not xtra_args:
                xtra_args = [0, ValueMap(times=[1960, 1970, 1980], values=[0.1, 0.1, 0.1])]
            sexdeb_iv_event = SetSexualDebutAge(camp, setting_type=SettingType.CURRENT_AGE,
                                                distributed_event_trigger="Setting_Age_Sexual_Debut")

            add_intervention_reference_tracking(camp,
                                                intervention_list=[sexdeb_iv_event],
                                                time_value_map=xtra_args[1],
                                                tracking_config=IsPostDebut(),
                                                update_period=30.416667,
                                                start_year=TC.Start_Year,
                                                end_year=TC.End_Year
                                                )
            return camp

        def setParamfn(config, duration):
            # uses the global set_param_fn to set parameters
            config = self.global_set_param_fn(config)
            config.parameters.Sexual_Debut_Age_Setting_Type = "FROM_INTERVENTION"
            # config.parameters.Demographics_Filenames = [ "demographics_Normal_PFARates.json" ]
            return config

        def update_campaign(simulation, args):
            #   This callback function updates the coverage of the campaign. Function: "build_camp02"
            build_campaign_partial = partial(build_camp, xtra_args=args)
            simulation.task.create_campaign_from_callback(build_campaign_partial)
            tag_value = {time:value for (time, value) in zip(args[1]._times, args[1]._values)}
            # Return a tag that will be added to the simulation run.
            return {"Test_Case": tag_value}

        task = emod_task.EMODTask.from_defaults(
            eradication_path=str(self.eradication_path),
            campaign_builder=partial(build_camp),
            schema_path=str(self.schema_path),
            config_builder=partial(setParamfn, duration=(start_day + 1)),
            demographics_builder=self.global_build_demog_from_template_node,
            report_builder=self.report_builder
        )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string
        # get the path of this script
        CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
        INPUT_DEMOG_PATH = os.path.join(CURRENT_DIRECTORY, "inputs", "demographic_files")
        demog_files = [os.path.join(INPUT_DEMOG_PATH, "demographics_Normal_PFARates.json"),
                       os.path.join(INPUT_DEMOG_PATH, "demographics_Low_PFARates.json"),
                       os.path.join(INPUT_DEMOG_PATH, "demographics_High_PFARates.json")]

        task.demographics.clear()  # First it Clears the demographics from the task
        for demog in demog_files:
            task.simulation_demographics.add_demographics_from_files(demog)

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))  # Runs
        builder.add_sweep_definition(self.update_demographic_filename, ["Normal", "Low", "High"])  # Demographics
        builder.add_sweep_definition(update_campaign, args=[a for a in args])  # Campaign - Year-SexualDebut-Ratios

        experiment = Experiment.from_builder(builder, task, name=f"HIV {test_name}")
        experiment.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")
        sims = self.platform.get_children_by_object(experiment)

        testtime = datetime.datetime.now().strftime("%d_%H%M%S")  # To create a unique folder name (for plotting)
        output_path = Path(os.path.join(self.test_folder, testtime)).resolve()

        for simulation in sims:
            # download simulation's output files from COMPS 
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            local_path = output_path / str(simulation.uid)
            self.validate_tracker_events_report_output_file(local_path)
            self.validate_HIVByAgegender_CurrentAge(local_path, genders=[0, 1])
            self.validate_simulation_config_file(local_path, "FROM_INTERVENTION")

    def test_track_sexual_debut_intervention_CURRENTAGE_STAGGERED(self):
        # local_path = Path(r"E:\GIT\emodpy-hiv\tests\sim_tests\inputs\28_154125\1ce3f49a-478e-ee11-92fe-f0921c167864")

        start_day = 2
        test_name = self.id().split('.')[-1]

        def build_camp(camp):
            ysdr1 = ValueMap(times=[2000, 2001, 2003, 2004, 2005, 2007, 2009, 2010, 2012, 2014, 2016, 2017],
                             values=[0.7, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1])
            sexdeb_iv_event_female = SetSexualDebutAge(camp, setting_type=SettingType.CURRENT_AGE,
                                                distributed_event_trigger="Setting_Age_Sexual_Debut")

            add_intervention_reference_tracking(camp,
                                                intervention_list=[sexdeb_iv_event_female],
                                                time_value_map=ysdr1,
                                                tracking_config=IsPostDebut(),
                                                update_period=30.416667,
                                                start_year=1960.5,
                                                end_year=2050,
                                                target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.FEMALE,
                                                                                                    demographic_coverage=None)
                                                )

            ysdr2 = ValueMap(times=[2000, 2001, 2003, 2004, 2005, 2007, 2009, 2010, 2012, 2014, 2016, 2017],
                             values=[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1])

            sexdeb_iv_event_male = SetSexualDebutAge(camp, setting_type=SettingType.CURRENT_AGE,
                                                     distributed_event_trigger="Setting_Age_Sexual_Debut")

            add_intervention_reference_tracking(camp,
                                                intervention_list=[sexdeb_iv_event_male],
                                                time_value_map=ysdr2,
                                                tracking_config=IsPostDebut(),
                                                update_period=30.416667,
                                                start_year=1960.5,
                                                end_year=2050,
                                                target_demographics_config=TargetDemographicsConfig(target_gender=TargetGender.MALE,
                                                                                                    demographic_coverage=None)
                                                )
            return camp

        # def build_demog(self, case="Normal"):
        #     demog = HIVDemographics.from_file(f"demographics_{case}_PFARates.json")
        #
        #     # print(demog.to_dict())
        #     return demog

        def setParamfn(config, duration):
            # uses the global set_param_fn to set parameters
            config = self.global_set_param_fn(config)
            config.parameters.Sexual_Debut_Age_Setting_Type = "FROM_INTERVENTION"
            return config

        task = emod_task.EMODTask.from_defaults(eradication_path=str(self.eradication_path),
                                                   campaign_builder=partial(build_camp),
                                                   schema_path=str(self.schema_path),
                                                   config_builder=partial(setParamfn, duration=(start_day + 1)),
                                                   demographics_builder=self.global_build_demog_from_template_node,
                                                   report_builder=partial(self.report_builder, age_bins=[13, 15, 16, 17, 18, 19, 20, 25, 30])
                                                   )
        task.set_sif(str(manifest.sif_path), platform=self.platform)  # set_sif() expects a string

        builder = SimulationBuilder()
        builder.add_sweep_definition(self.update_sim_random_seed, range(1))
        experiment = Experiment.from_builder(builder, task, name=f"HIV {test_name}")
        experiment.run(wait_until_done=True, platform=self.platform)
        self.assertTrue(experiment.succeeded, msg=f"Experiment {experiment.uid} failed.\n")

        print(f"Experiment {experiment.uid} succeeded.")

        sims = self.platform.get_children_by_object(experiment)

        testtime = datetime.datetime.now().strftime("%d_%H%M%S")  # To create a unique folder name (for plotting)
        output_path = Path(os.path.join(self.test_folder, testtime)).resolve()

        for simulation in sims:
            # download simulation's output files from COMPS 
            self.platform.get_files_by_id(simulation.id, item_type=ItemType.SIMULATION, files=filenames,
                                          output=output_path)
            local_path = output_path / str(simulation.uid)
            self.validate_tracker_events_report_output_file(local_path)
            self.validate_HIVByAgegender_CurrentAge(local_path, genders=[0, 1])
            self.validate_simulation_config_file(local_path, "FROM_INTERVENTION")

    # ------------------ Utility functions ------------------

    def validate_reports_basics(self, local_path, reports=[]):
        for filename in reports:
            if filename == files.config:
                continue
            file_path = local_path / filename
            self.assertTrue(file_path.is_file(), msg=f'Test failed: {filename} is not generated.')
            report_df = pd.read_csv(file_path)
            self.assertGreater(len(report_df), 0, msg=f'Test failed: {filename} report should not be empty.')
        return

    def validate_ReportEventRecorder(self, local_path):
        # validate Report Event Recorder file exist
        file_path = local_path / files.ReportEventRecorder

        # validate Report Evenet Recorder contents
        report_df = pd.read_csv(file_path)
        sti_debut_df = report_df[report_df['Event_Name'] == 'STIDebut']

        # validate if STIDebut event is recorded
        self.assertGreater(len(sti_debut_df), 0, msg='Test failed: there are should be some STIDebut events.')
        return

    def validate_HIVByAgegender_CurrentAge(self, local_path, genders=[]):
        # validate if 'ReportHIVByAgeAndGender.csv' is generated
        file_path = local_path / files.ReportHIVByAgeAndGender
        report_df = pd.read_csv(file_path)

        for gender in genders:
            # create a subset of the report_df for the given case
            df = report_df[(report_df[' Gender'] == gender)]

            hasdeb_mean = df['Has Debuted'].mean()
            hadfirst_mean = df['Had First Coital Act'].mean()
            print(
                f"Gender: {gender}: Mean of Has Debuted: {hasdeb_mean}, Mean of Had First Coital Act: {hadfirst_mean}\n\n")

            # print(df['Has Debuted'].to_list(),  df['Had First Coital Act'].to_list())
            self.assertGreater(hasdeb_mean, 0,
                               f'Test failed: "Has Debuted" should not be 0 \n\n Age: CurrentAge Gender: {gender} file: {file_path}')
            self.assertGreater(hadfirst_mean, 0,
                               f'Test failed: "Had First Coital Act" should Not be 0 \n\n Age: CurrentAge Gender: {gender} file: {file_path}')
        return

    def validate_HIVByAgegender_UserSpecified(self, local_path, target_gender=['Male', 'Female']):
        # TODO: IMPLEMENT THIS - THIS IS a copy of the 'current age' function

        # validate if 'ReportHIVByAgeAndGender.csv' is generated
        report_path = local_path / files.ReportHIVByAgeAndGender
        report_df = pd.read_csv(report_path)

        campaign_path = local_path / files.campaign
        report_df['Gender'] = report_df[' Gender'].replace({0: 'Male', 1: 'Female'})

        # Validate information is present per gender.
        for case in target_gender:
            gender = case

            # create a subset of the report_df for the given case
            df = report_df[(report_df['Gender'] == gender)]

            hasdeb_mean = df['Has Debuted'].mean()
            hadfirst_mean = df['Had First Coital Act'].mean()
            print(
                f"Gender: {gender}: Mean of Has Debuted: {hasdeb_mean}, Mean of Had First Coital Act: {hadfirst_mean}\n\n")

            # print(df['Has Debuted'].to_list(),  df['Had First Coital Act'].to_list())
            self.assertGreater(hasdeb_mean, 0,
                               f'Test failed: "Has Debuted" should not be 0 \n\n Age: CurrentAge Gender: {gender}')
            self.assertGreater(hadfirst_mean, 0,
                               f'Test failed: "Had First Coital Act" should Not be 0 \n\n Age: CurrentAge Gender: {gender}')

            # Validate directly against the campaign configuration
        campaign_obj = pd.read_json(campaign_path)
        events = campaign_obj['Events']

        for event in events:
            target_age = event['Event_Coordinator_Config']['Intervention_Config']['Age_Years']
            gender = event['Event_Coordinator_Config']['Target_Gender']

            start_day = event['Start_Day']
            print(f"Target Age: {target_age}, Gender: {gender} start_day: {start_day}")

            # Create a subset of the report_df looking for Male/Females younger than Age_Years who have debuted
            df = report_df[
                (report_df[' Age'] < target_age) & (report_df[' Gender'] == gender) & (report_df['Has Debuted'] > 0)]

            # Assert if is not empty )there should not be any
            self.assertEqual(len(df), 0,
                             f'Test failed: No {gender} younger than min age should have debuted \n\n Age: {target_age}')
        return

    def validate_simulation_config_file(self, local_path, setting_type):
        # validate if config.json is generated
        file_path = local_path / files.config
        self.assertTrue(file_path.is_file(), msg='Test failed: config.json is not generated.')
        # validate result
        with open(file_path) as f:
            config = json.load(f)
        self.assertEqual(config['parameters']['Sexual_Debut_Age_Setting_Type'],
                         setting_type,
                         msg='Test failed: Sexual_Debut_Age_Setting_Type should be FROM_INTERVENTION.')
        return

    def validate_tracker_events_report_output_file(self, local_path):
        # validate files exist
        file_path = local_path / 'output' / 'ReportEventRecorder.csv'
        self.assertTrue(file_path.is_file(), msg='Test failed: ReportEventRecorder.csv is not generated.')

        # validate Report Evenet Recorder contents
        report_df = pd.read_csv(file_path)
        sti_debut_df = report_df[report_df['Event_Name'] == 'STIDebut']
        self.assertGreater(len(sti_debut_df), 0, msg='Test failed: there are should be some STIDebut events.')
        # validate the existance of Setting_Age_Sexual_Debut events in report_df
        sasd_debut_df = report_df[report_df['Event_Name'] == 'Setting_Age_Sexual_Debut']
        self.assertGreater(len(sasd_debut_df), 0,
                           msg='Test failed: there are should be some Setting_Age_Sexual_Debut events.')

    def validate_tracker_HIVByAgegender_UserSpecified(self, local_path, cases):
        # validate if 'ReportHIVByAgeAndGender.csv' is generated
        report_path = local_path / files.ReportHIVByAgeAndGender
        report_df = pd.read_csv(report_path)

        for case in cases:
            gender = case[0]
            specified_age = case[1]

            # create a subset of the report_df for the given case
            df = report_df[(report_df[' Age'] == specified_age) & (report_df[' Gender'] == gender)]
            # print(df['Has Debuted'].to_list(),  df['Had First Coital Act'].to_list())
            hasdeb_mean = df['Has Debuted'].mean()
            hadfirst_mean = df['Had First Coital Act'].mean()
            self.assertNotEqual(hasdeb_mean, 0,
                                f'Test failed: "Has Debuted" should not be 0 \n\n Age: {specified_age} Gender: {gender}')
            self.assertNotEqual(hadfirst_mean, 0,
                                f'Test failed: "Had First Coital Act" should not be 0 \n\n Age: {specified_age} Gender: {gender}')
            print(
                f"For Gender: {gender} & Age {specified_age}: Mean of Has Debuted: {hasdeb_mean}, Mean of Had First Coital Act: {hadfirst_mean}\n\n")

            df = report_df[(report_df[' Age'] < specified_age) & (report_df[' Gender'] == gender)]
            hasdeb_mean = df['Has Debuted'].mean()
            hadfirst_mean = df['Had First Coital Act'].mean()
            # print(df['Has Debuted'].to_list(),  df['Had First Coital Act'].to_list())
            self.assertEqual(hasdeb_mean, 0,
                             f'Test failed: "Has Debuted" should be 0 \n\n For age less than: {specified_age} and Gender: {gender}')
            self.assertEqual(hadfirst_mean, 0,
                             f'Test failed: "Had First Coital Act" should be 0 \n\n For age less than: {specified_age} and Gender: {gender}')
        return


if __name__ == '__main__':
    unittest.main()
