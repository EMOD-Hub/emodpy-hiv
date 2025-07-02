import unittest
import pytest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.plotting.plot_a_vs_b as pab

@pytest.mark.unit
class TestPlottingAvsB(PlotTestBase):

    def test_plot_csv_a_vs_b(self):
        input_dir_filename_a = os.path.join(self.test_folder,"testdata/test_plot_csv_a_vs_b/INFORMAL-MEDIUM.csv")
        input_dir_filename_b = os.path.join(self.test_folder,"testdata/test_plot_csv_a_vs_b/MARITAL-MEDIUM.csv")
        exp_img_dir          = os.path.join(self.test_folder,"testdata/test_plot_csv_a_vs_b/images_exp")
        act_img_dir          = os.path.join(self.test_folder,"testdata/test_plot_csv_a_vs_b/images_act")

        pab.plot_csv_a_vs_b(a_filename=input_dir_filename_a,
                            b_filename=input_dir_filename_b,
                            a_column_prefix="A",
                            b_column_prefix="B",
                            title="Informal-Male-Medium vs Marital-Male-Medium",
                            y_axis_name="Fraction of New Relationships Started",
                            img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")


if __name__ == '__main__':
    unittest.main()
