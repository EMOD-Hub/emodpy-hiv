import unittest
import pytest
import os
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.plotting.plot_relationship_end as pre

@pytest.mark.unit
class TestPlottingFromRelationshipEnd(PlotTestBase):

    def test_plot_relationship_duration(self):
        input_filename = os.path.join(self.test_folder,"testdata/RelationshipEnd_data/RelationshipEnd_sample00000_run00001.csv")
        input_dir      = os.path.join(self.test_folder,"testdata/RelationshipEnd_data")
        exp_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_relationship_duration/images_exp")
        act_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_relationship_duration/images_act")

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_filename,
                                                               relationship_type="transitory",
                                                               show_avg_per_run=True,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_dir,
                                                               relationship_type="informal",
                                                               show_avg_per_run=True,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_filename,
                                                               relationship_type="marital",
                                                               show_avg_per_run=True,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_filename,
                                                               relationship_type="commercial",
                                                               show_avg_per_run=True,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_dir,
                                                               relationship_type="transitory",
                                                               show_avg_per_run=False,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_dir,
                                                               relationship_type="informal",
                                                               show_avg_per_run=False,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_dir,
                                                               relationship_type="marital",
                                                               show_avg_per_run=False,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        pre.plot_relationship_duration_histogram_with_expected(dir_or_filename=input_dir,
                                                               relationship_type="commercial",
                                                               show_avg_per_run=False,
                                                               show_expected=True,
                                                               img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")


if __name__ == '__main__':
    unittest.main()
