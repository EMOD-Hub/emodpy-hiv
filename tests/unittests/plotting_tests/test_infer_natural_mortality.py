import unittest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.demographics.infer_natural_mortality as infer



class TestInferNaturalMortality(PlotTestBase):

    def test_infer_natural_mortality(self):
        exp_img_dir = os.path.join(self.test_folder,"testdata/test_infer_natural_mortality/images_exp")
        act_img_dir = os.path.join(self.test_folder,"testdata/test_infer_natural_mortality/images_act")

        infer.mortality_read_infer_plot_app(country="Zambia", 
                                            version="2015",
                                            gender="male",
                                            min_year=1950,
                                            max_year=1975,
                                            save_data=False,
                                            other_csv_filename=None,
                                            img_dir=act_img_dir)
        
        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")
