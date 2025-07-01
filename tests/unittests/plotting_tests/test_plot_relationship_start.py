import unittest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.plotting.plot_relationship_start as prs

class TestPlottingFromRelationshipStart(PlotTestBase):

    @unittest.skip("Disabling for time - run tests manually if editing plotting code.")
    def test_plot_relationship_assortivity_risk_all(self):
        input_dir   = os.path.join(self.test_folder,"testdata/RelationshipStart_data/")
        exp_img_dir = os.path.join(self.test_folder,"testdata/test_plot_relationship_assortivity_risk_all/images_exp")
        act_img_dir = os.path.join(self.test_folder,"testdata/test_plot_relationship_assortivity_risk_all/images_act")
        exp_reg_dir = os.path.join(self.test_folder,"testdata/test_plot_relationship_assortivity_risk_all/regression_exp")
        act_reg_dir = os.path.join(self.test_folder,"testdata/test_plot_relationship_assortivity_risk_all/regression_act")

        prs.plot_relationship_assortivity_risk_all(dir_or_filename=input_dir,
                                                   regression_dir=act_reg_dir,
                                                   img_dir=act_img_dir)
        
        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")
        self.compare_files(exp_dir=exp_reg_dir, act_dir=act_reg_dir, file_extension=".csv")

if __name__ == '__main__':
    unittest.main()
