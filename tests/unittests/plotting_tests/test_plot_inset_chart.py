import unittest
import pytest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.plotting.plot_inset_chart as pic

@pytest.mark.unit
class TestPlottingInsetChart(PlotTestBase):

    def test_plot_inset_chart(self):
        input_dir   = os.path.join(self.test_folder,"testdata/InsetChart_data/")
        ref_file  = os.path.join(self.test_folder,"testdata/InsetChart_data/InsetChart_baseline.json")
        com_file  = os.path.join(self.test_folder,"testdata/InsetChart_data/InsetChart_seed_csw_coinf.json")
        exp_img_dir = os.path.join(self.test_folder,"testdata/test_plot_inset_chart/images_exp")
        act_img_dir = os.path.join(self.test_folder,"testdata/test_plot_inset_chart/images_act")

        pic.plot_inset_chart(dir_name=input_dir,
                             reference=None,
                             comparison1=None,
                             comparison2=None,
                             comparison3=None,
                             title="plot_directory",
                             include_filenames_in_title=False,
                             output=act_img_dir)
        
        pic.plot_inset_chart(dir_name=None,
                             reference=ref_file,
                             comparison1=com_file,
                             comparison2=None,
                             comparison3=None,
                             title="plot_two_files",
                             include_filenames_in_title=False,
                             output=act_img_dir)
        
        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

if __name__ == '__main__':
    unittest.main()
