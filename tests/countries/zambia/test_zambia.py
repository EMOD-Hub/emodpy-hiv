import json
import unittest
import sys
import os
import time
from pathlib import Path
from emodpy.emod_task import logger
from emodpy.emod_task import EMODTask
import emodpy_hiv.plotting.plot_inset_chart as pic
import emodpy_hiv.countries.zambia.zambia as cm
from idmtools.entities.experiment import Experiment
from idmtools.core import ItemType

# Add the parent directory to sys.path
manifest_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(manifest_directory))

test_directory = Path(__file__).resolve().parent

import manifest
import helpers
from base_sim_test import BaseSimTest


class TestZambia(BaseSimTest):
    """
    The goal of this test is to keep the Zambia model up to date.  If this test fails,
    something has changed and the developer needs to know what changed what its impact
    is on this model.

    It is recommended that if things change and you aren't sure about the impact to this
    model that you run this with a larger x_Base_Population value to ensure that you get
    infection in all nodes.  You will need to run before and after the change.
    """

    def test_zambia(self):
        zambia = cm.Zambia

        def config_setter(config):
            config = zambia.build_config(config)
            config.parameters.x_Base_Population = 0.002  # 0.05
            config.parameters.Simulation_Duration = 80 * 365
            return config

        def campaign_builder(campaign):
            return zambia.build_campaign(campaign)

        self.task = EMODTask.from_defaults(
            eradication_path=self.eradication_path,
            schema_path=self.schema_path,
            config_builder=config_setter,
            campaign_builder=campaign_builder,
            demographics_builder=zambia.build_demographics,
            report_builder=zambia.build_reports
        )

        self.task.set_sif(self.sif_path, platform=self.platform)
        experiment = Experiment.from_task(task=self.task,
                                          name=self.case_name)

        # The last step is to call run() on the ExperimentManager to run the simulations.
        experiment.run(wait_until_done=True, platform=self.platform)

        self.assertTrue(experiment.succeeded, f"Experiment {self.case_name} failed.")

        this_sim = experiment.simulations[0]

        expected_reporter_files = ["InsetChart.json",
                                   "ReportHIVByAgeAndGender.csv", "RelationshipStart.csv",
                                   "TransmissionReport.csv",
                                   "ReportHIVART.csv", "ReportHIVInfection.csv", "HIVMortality.csv"]

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

        with self.assertRaises(RuntimeError) as context:
            not_expected_files = ["DemographicsSummary.json"]
            not_expected_files_with_path = [os.path.join("output", file) for file in not_expected_files]
            self.platform.get_files(this_sim, files=not_expected_files_with_path)
        print(str(context.exception))
        self.assertTrue(f"Couldn't find file for path '{not_expected_files_with_path[0]}'" in str(context.exception),
                        msg=str(context.exception))
        
        # Now verify that the InsetChart.json produced is what we expect
        filenames = ["output/InsetChart.json"]
        output_path = Path(self.test_folder).resolve()
        self.platform.get_files_by_id(this_sim.id, item_type=ItemType.SIMULATION, files=filenames,
                                      output=output_path)
        
        if os.name == "nt":
            time.sleep(1)  # only needed for windows

        inset_chart_path_exp = test_directory / "inputs" / "test_zambia_sim_InsetChart.json"
        inset_chart_path_act = output_path / str(this_sim.uid) / 'output' / 'InsetChart.json'

        self.assertTrue(inset_chart_path_exp.is_file())
        self.assertTrue(inset_chart_path_act.is_file())
        is_same = self.compare_json(inset_chart_path_exp, inset_chart_path_act)

        if not is_same:
            pic.plot_inset_chart(dir_name=None,
                                 reference=str(inset_chart_path_exp),
                                 comparison1=str(inset_chart_path_act),
                                 comparison2=None,
                                 comparison3=None,
                                 title="test_zambia",
                                 include_filenames_in_title=True,
                                 output=output_path)
        self.assertTrue(is_same)


if __name__ == '__main__':
    unittest.main()
