import sys
import unittest
from pathlib import Path
import pytest

# tests/ must be in sys.path before tutorials/ so tutorial modules get tests/manifest
# (which points to tests/executables/ rather than tutorials/executables/)
_tests_dir = str(Path(__file__).resolve().parents[1])
_tutorials_dir = str(Path(__file__).resolve().parents[2] / "tutorials")
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)

import manifest  # cache tests/manifest before tutorial modules are imported
import helpers
from base_sim_test import BaseSimTest

if _tutorials_dir not in sys.path:
    sys.path.append(_tutorials_dir)

import tutorial_1_intro as t1
import tutorial_2_reports as t2
import tutorial_3_build_functions as t3
import tutorial_4_overriding_coc as t4


@pytest.mark.tutorial
class TestTutorials(BaseSimTest):

    def test_tutorial_1_intro(self):
        experiment = t1.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 1 experiment failed.")

    def test_tutorial_2_reports(self):
        experiment = t2.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 2 experiment failed.")
        self._assert_reports_and_plots("tutorial_2_results")

    def test_tutorial_3_build_functions(self):
        experiment = t3.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 3 experiment failed.")
        self._assert_reports_and_plots("tutorial_3_results")

    def test_tutorial_4_overriding_coc(self):
        experiment = t4.run_experiment()
        self.assertTrue(experiment.succeeded, "Tutorial 4 experiment failed.")
        self._assert_reports_and_plots("tutorial_4_results")

    def _assert_reports_and_plots(self, output_path):
        results = Path(output_path)

        # Downloaded report files (nested under exp_uid/sim_uid/output/ by DownloadAnalyzer)
        inset_charts = list(results.rglob("InsetChart.json"))
        self.assertGreater(len(inset_charts), 0,
                           f"InsetChart.json not found under {output_path}")

        hiv_reports = list(results.rglob("ReportHIVByAgeAndGender.csv"))
        self.assertGreater(len(hiv_reports), 0,
                           f"ReportHIVByAgeAndGender.csv not found under {output_path}")

        # Plot PNGs saved at the top of the results directory
        pngs = list(results.glob("*.png"))
        self.assertGreater(len(pngs), 0,
                           f"No PNG plots found in {output_path}")


if __name__ == '__main__':
    unittest.main()
