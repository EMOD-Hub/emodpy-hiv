import unittest
import pytest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.plotting.plot_inset_chart_mean_compare as picmc

@pytest.mark.unit
class TestPlottingInsetChart(PlotTestBase):

    def test_plot_inset_chart_mean_compare(self):
        input_dir   = os.path.join(self.test_folder,"testdata/InsetChart_data/")
        exp_img_dir = os.path.join(self.test_folder,"testdata/test_plot_inset_chart_mean_compare/images_exp")
        act_img_dir = os.path.join(self.test_folder,"testdata/test_plot_inset_chart_mean_compare/images_act")

        picmc.plot_mean(dir1=input_dir,
                        dir2=None,
                        dir3=None,
                        title="test_plot_inset_chart_mean_compare",
                        show_raw_data=True,
                        subplot_index_min=15,
                        subplot_index_max=19,
                        output=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

if __name__ == '__main__':
    unittest.main()
