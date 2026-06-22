import pytest

import os
import shutil

import numpy as np

import emodpy_hiv.demographics.infer_natural_mortality as infer

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.getcwd()

@pytest.mark.unit
class TestInferNaturalMortality():

    def test_infer_natural_mortality(self):

        os.chdir(TEST_DIR)

        exp_dir = "testdata/test_infer_natural_mortality"
        img_dir = "testdata/test_infer_natural_mortality/temp"

        fname01 = 'mortality_minus_hiv_year_age_rate.csv'
        fname02 = 'raw_mortality_year_age_rate.csv'

        expected01 = os.path.join(exp_dir, fname01)
        expected02 = os.path.join(exp_dir, fname02)

        infer.mortality_read_infer_plot_app(country="Zambia",
                                            version="2015",
                                            gender="male",
                                            min_year=1950,
                                            max_year=1975,
                                            save_data=True,
                                            other_csv_filename=None,
                                            img_dir=img_dir)

        out1 = np.loadtxt(fname01, delimiter=',', skiprows=1)
        out2 = np.loadtxt(fname02, delimiter=',', skiprows=1)

        ref1 = np.loadtxt(expected01, delimiter=',', skiprows=1)
        ref2 = np.loadtxt(expected02, delimiter=',', skiprows=1)

        assert((out1 == ref1).all())
        assert((out2 == ref2).all())

        shutil.rmtree(img_dir)
        os.remove(fname01)
        os.remove(fname02)
        os.chdir(WORK_DIR)

