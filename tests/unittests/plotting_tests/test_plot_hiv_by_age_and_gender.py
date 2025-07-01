import unittest
import os
from importlib import resources
from pathlib import Path
import sys

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

from plot_test_base import PlotTestBase

import emodpy_hiv.countries.un_world_pop_data as un_data
import emodpy_hiv.plotting.plot_hiv_by_age_and_gender as pang

pang.TEST_include_dir_or_filename = False

SKIP_TESTS = True

class TestPlottingFromHivByAgeAndGender(PlotTestBase):

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_risk_zambia(self):
            input_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
            input_dir      = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
            exp_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_risk_zambia/images_exp")
            act_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_risk_zambia/images_act")

            pang.plot_risk_zambia(dir_or_filename=input_filename,
                                  age_bin_list=[15,35,55],
                                  show_avg_per_run=True,
                                  show_fraction=True,
                                  show_expected=True,
                                  img_dir=act_img_dir)

            pang.plot_risk_zambia(dir_or_filename=input_dir,
                                  age_bin_list=[15,35,55],
                                  show_avg_per_run=True,
                                  show_fraction=False,
                                  show_expected=False,
                                  img_dir=act_img_dir)
            
            self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_population_by_gender(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_population_by_gender/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_population_by_gender/images_act")

        pang.plot_population_by_gender(filename=input_dir_filename, img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_population_by_age(self):
        input_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        input_dir      = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_population_by_age/images_exp")
        act_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_population_by_age/images_act")

        pang.plot_population_by_age(dir_or_filename=input_filename,
                                    gender="Male",
                                    age_bin_list=[0,15,50,75,100],
                                    img_dir=act_img_dir)
        
        pang.plot_population_by_age(dir_or_filename=input_filename,
                                    gender="Female",
                                    age_bin_list=[0,15,50,75,100],
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender=None,
                                    age_bin_list=None,
                                    show_avg_per_run=False,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender=None,
                                    age_bin_list=None,
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=3,
                                    gender=None,
                                    age_bin_list=None,
                                    show_avg_per_run=False,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=3,
                                    gender=None,
                                    age_bin_list=None,
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender="Female",
                                    age_bin_list=None,
                                    show_avg_per_run=False,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender="Female",
                                    age_bin_list=None,
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=3,
                                    gender="Female",
                                    age_bin_list=None,
                                    show_avg_per_run=False,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=3,
                                    gender="Female",
                                    age_bin_list=None,
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=3,
                                    gender="Female",
                                    age_bin_list=[0,15,50,100],
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender=None,
                                    age_bin_list=[0,15,25,50,75,100],
                                    show_avg_per_run=True,
                                    img_dir=act_img_dir)

        pang.plot_population_by_age(dir_or_filename=input_dir,
                                    node_id=None,
                                    gender=None,
                                    age_bin_list=[0,15],
                                    show_avg_per_run=False,
                                    img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_population_by_ip(self):
        input_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        input_dir      = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_population_by_ip/images_exp")
        act_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_population_by_ip/images_act")

        pang.plot_population_by_ip(dir_or_filename=input_dir,
                                   ip_key="CascadeState",
                                   show_avg_per_run=False,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_dir,
                                   ip_key="CascadeState",
                                   show_avg_per_run=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_dir,
                                   ip_key="Accessibility",
                                   show_avg_per_run=False,
                                   show_fraction=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_dir,
                                   ip_key="Risk",
                                   gender="Male",
                                   show_avg_per_run=False,
                                   show_fraction=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_dir,
                                   ip_key="Risk",
                                   gender="Female",
                                   age_bin_list=[15,35,50],
                                   show_avg_per_run=True,
                                   show_fraction=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_filename,
                                   ip_key="CascadeState",
                                   show_avg_per_run=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_filename,
                                   ip_key="Accessibility",
                                   show_avg_per_run=True,
                                   show_fraction=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_filename,
                                   ip_key="Risk",
                                   gender="Male",
                                   show_avg_per_run=True,
                                   show_fraction=True,
                                   img_dir=act_img_dir)

        pang.plot_population_by_ip(dir_or_filename=input_filename,
                                   ip_key="Risk",
                                   gender="Female",
                                   age_bin_list=[15,50],
                                   show_avg_per_run=True,
                                   show_fraction=False,
                                   img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    # not skipping this one because it is fast and tests some of the logic.
    def test_plot_columns(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_columns/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_columns/images_act")

        pang.plot_columns(filename=input_dir_filename,
                          title="Death",
                          y_axis_name="Number of People",
                          column_names=[" Died", " Died_from_HIV" ],
                          img_dir=act_img_dir)
        
        pang.plot_columns(filename=input_dir_filename,
                          title="Newly Infected",
                          y_axis_name="Number of People",
                          column_names=[" Newly Infected" ],
                          img_dir=act_img_dir)
        
        pang.plot_columns(filename=input_dir_filename,
                          title="Prevalence",
                          y_axis_name="Fraction of Population",
                          column_names=[" Infected" ],
                          fraction_of_population=True,
                          img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_circumcision(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_circumcision/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_circumcision/images_act")

        pang.plot_circumcision_by_age(filename=input_dir_filename,
                                      age_bin_list=[10,15,20,25,30,35,40,45,50,55,60,100],
                                      fraction_of_total=True,
                                      img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_onART(self):
        input_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        input_dir      = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_onART/images_exp")
        act_img_dir    = os.path.join(self.test_folder,"testdata/test_plot_onART/images_act")

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender=None,
                               age_bin_list=None,
                               show_avg_per_run=False,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender=None,
                               age_bin_list=None,
                               show_avg_per_run=True,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender="Female",
                               age_bin_list=None,
                               show_avg_per_run=True,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender=None,
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender=None,
                               age_bin_list=None,
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender=None,
                               age_bin_list=None,
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=True,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender="Female",
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=True,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_dir,
                               gender="Male",
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=True,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_filename,
                               gender=None,
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=True,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_filename,
                               gender="Female",
                               age_bin_list=[0,15,50,75,100],
                               #age_bin_list=[15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_filename,
                               gender="Male",
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=False,
                               fraction_of_infected=False,
                               img_dir=act_img_dir)

        pang.plot_onART_by_age(dir_or_filename=input_filename,
                               gender="Male",
                               age_bin_list=[0,15,50,75,100],
                               show_avg_per_run=True,
                               show_fraction=True,
                               fraction_of_infected=True,
                               img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_population_vs_world_pop(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data/ReportHIVByAgeAndGender_sample00000_run00001.csv")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_population_vs_world_pop/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_population_vs_world_pop/images_act")

        un_data_root = resources.files(un_data)
        unworld_pop_fn = Path(un_data_root, "WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx") # noqa: E221
        pang.plot_population_by_age_vs_unworld_pop(filename=input_dir_filename,
                                                   x_base_population=0.001,
                                                   unworld_pop_filename=unworld_pop_fn,
                                                   #age_bin_list=[0,5,10,15,20,25,30,35,40,45,50,55,60,65,70,75,80,85,90,95,100],
                                                   age_bin_list=[25,30,35,40],
                                                   country="Zambia",
                                                   version="2024",
                                                   img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_population_by_dir(self):
        input_dir   = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir = os.path.join(self.test_folder,"testdata/test_plot_population_by_dir/images_exp")
        act_img_dir = os.path.join(self.test_folder,"testdata/test_plot_population_by_dir/images_act")

        unworld_pop_fn_male   = Path(self.test_folder,"testdata/unwp", "WPP2015_POP_F15_2_ANNUAL_POPULATION_BY_AGE_MALE.XLS"  ) # noqa: E221
        unworld_pop_fn_female = Path(self.test_folder,"testdata/unwp", "WPP2015_POP_F15_3_ANNUAL_POPULATION_BY_AGE_FEMALE.XLS") # noqa: E221
        for age_bin in [0,10,70,80]:
            pang.plot_population_for_dir(dir_or_filename=input_dir,
                                         unworld_pop_filename=unworld_pop_fn_male,
                                         country="Zambia",
                                         version="2015",
                                         x_base_population=0.001,
                                         gender="Male",
                                         age_bin=age_bin,
                                         img_dir=act_img_dir)
            pang.plot_population_for_dir(dir_or_filename=input_dir,
                                         unworld_pop_filename=unworld_pop_fn_female,
                                         country="Zambia",
                                         version="2015",
                                         x_base_population=0.001,
                                         gender="Female",
                                         age_bin=age_bin,
                                         img_dir=act_img_dir)
            
        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_vmmc(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_vmmc/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_vmmc/images_act")

        for node_index in range(3):
            pang.plot_vmmc_for_dir(dir_or_filename=input_dir_filename,
                                   node_id=node_index+1,
                                   age_bin_list=[15,20,25,30,35,40,45,50,55],
                                   show_expected=True,
                                   show_avg_per_run=True,
                                   img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_vmmc_by_age(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_vmmc_by_age/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_vmmc_by_age/images_act")

        pang.plot_vmmc_by_age(dir_or_filename=input_dir_filename,
                              exp_dir_or_filename=None,
                              node_id=None,
                              age_bin_list=[15,20,25,30,35,40,45,50,55],
                              show_avg_per_run=True,
                              img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

    @unittest.skipIf(SKIP_TESTS, "Disabling for time - run tests manually if editing plotting code.")
    def test_plot_prevalence(self):
        input_dir_filename = os.path.join(self.test_folder,"testdata/ReportHIVAgeAndGender_data")
        exp_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_prevalence/images_exp")
        act_img_dir        = os.path.join(self.test_folder,"testdata/test_plot_prevalence/images_act")

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=None,
                                     gender=None,
                                     age_bin_list=None,
                                     show_avg_per_run=False,
                                     show_fraction=False,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=None,
                                     gender=None,
                                     age_bin_list=None,
                                     show_avg_per_run=True,
                                     show_fraction=False,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=None,
                                     gender=None,
                                     age_bin_list=None,
                                     show_avg_per_run=False,
                                     show_fraction=True,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=None,
                                     gender="Male",
                                     age_bin_list=None,
                                     show_avg_per_run=True,
                                     show_fraction=True,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=None,
                                     gender="Male",
                                     age_bin_list=[15,20,25,30,35,40,45,50,55],
                                     show_avg_per_run=True,
                                     show_fraction=True,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=3,
                                     gender=None,
                                     age_bin_list=None,
                                     show_avg_per_run=False,
                                     show_fraction=False,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=3,
                                     gender="Female",
                                     age_bin_list=None,
                                     show_avg_per_run=False,
                                     show_fraction=False,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=3,
                                     gender="Female",
                                     age_bin_list=None,
                                     show_avg_per_run=True,
                                     show_fraction=False,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=3,
                                     gender="Female",
                                     age_bin_list=None,
                                     show_avg_per_run=True,
                                     show_fraction=True,
                                     img_dir=act_img_dir)

        pang.plot_prevalence_for_dir(dir_or_filename=input_dir_filename,
                                     node_id=3,
                                     gender="Female",
                                     age_bin_list=[15,20,25,30,35,40,45,50,55],
                                     show_avg_per_run=True,
                                     show_fraction=True,
                                     img_dir=act_img_dir)

        self.compare_files(exp_dir=exp_img_dir, act_dir=act_img_dir, file_extension=".png")

if __name__ == '__main__':
    unittest.main()
