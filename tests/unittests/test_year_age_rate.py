import unittest
import pytest
from pathlib import Path
import sys

from emodpy_hiv.demographics.year_age_rate import YearAgeRate

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

EPSILON = 0.000001


@pytest.mark.unit
class TestYearAgeRate(unittest.TestCase):
    """
    Verify that the functionality of the YearAgeRate class.  This class is used as a standard
    format for inputing CSV data for demographics - age distribution, fertility rates, and
    mortality rates.
    """
    def setUp(self):
        pass

    def test_from_csv(self):
        """
        Verify that the data in the csv file is read correctly
        """
        csv_filename = Path(__file__).parent.joinpath('inputs/test_year_age_rate/test_from_csv.csv')
        test_yar = YearAgeRate( df=None, csv_filename=csv_filename )

        self.assertEqual(17, len(test_yar.df.index))

        column_names_expected = YearAgeRate.COL_NAMES
        column_names_actual = test_yar.df.columns.tolist()
        self.assertListEqual(column_names_expected, column_names_actual)

        node_id_expected = [0]
        node_id_actual = test_yar.df[YearAgeRate.COL_NAME_NODE_ID].unique().tolist()
        self.assertListEqual(node_id_expected, node_id_actual)

        min_year_expected = [1960]
        min_year_actual = test_yar.df[YearAgeRate.COL_NAME_MIN_YEAR].unique().tolist()
        self.assertListEqual(min_year_expected, min_year_actual)

        min_age_expected = [ 0,  5, 10, 15, 20, # noqa: E241
                            25, 30, 35, 40, 45, # noqa: E128
                            50, 55, 60, 65, 70, # noqa: E128
                            75, 80]             # noqa: E128
        min_age_actual = test_yar.df[YearAgeRate.COL_NAME_MIN_AGE].tolist()
        self.assertListEqual(min_age_expected, min_age_actual)

        rate_expected = [ 0.163250120, 0.135184835, 0.110994842, 0.096159790, 0.082972611,
                          0.073886576, 0.064505480, 0.055915065, 0.050518306, 0.042692190,
                          0.035725678, 0.027597084, 0.021945329, 0.016495398, 0.011207397,
                          0.006504519, 0.004444779 ]
        rate_actual = test_yar.df[YearAgeRate.COL_NAME_RATE].tolist()
        self.assertEqual( len(rate_expected), len(rate_actual))
        for i in range(len(rate_expected)):
            val_exp = rate_expected[i]
            val_act = rate_actual[i]
            self.assertAlmostEqual(val_exp, val_act, delta=0.000001)

    def test_to_age_distributions(self):
        """
        Verify that the age distribution data is read correctly and transformed
        into age distribution data usable by EMOD
        """
        csv_filename = Path(__file__).parent.joinpath('inputs/test_year_age_rate/test_to_age_distributions.csv')

        age_yar = YearAgeRate( df=None, csv_filename=csv_filename )

        node_id_age_dist_list = age_yar.to_age_distributions()

        # ------------------------------------------------------------------------------------
        # --- Verify that there is age distribution data for the two nodes defined in the CSV.
        # --- It returns a list of tuples where the first value in the tuple is the Node ID.
        # ------------------------------------------------------------------------------------
        self.assertEqual( 2, len(node_id_age_dist_list     ))
        self.assertEqual( 1,     node_id_age_dist_list[0][0]) # noqa: E241
        self.assertEqual( 2,     node_id_age_dist_list[1][0]) # noqa: E241

        # ----------------------------------------------------------------------------------
        # --- Verify that the first value is 0 and the last value is 1 for each cummulative
        # --- distribution function.
        # --- NOTE: The second object in the tuple is an AgeDistribution object.
        # ----------------------------------------------------------------------------------
        self.assertEqual(0.0, node_id_age_dist_list[0][1].cumulative_population_fraction[0])
        self.assertEqual(0.0, node_id_age_dist_list[1][1].cumulative_population_fraction[0])
        self.assertEqual(1.0, node_id_age_dist_list[0][1].cumulative_population_fraction[-1])
        self.assertEqual(1.0, node_id_age_dist_list[1][1].cumulative_population_fraction[-1])

        # ------------------------------------------------------------------------------
        # --- Verify that the ages have been converted correctly from minimum age values
        # --- to maximum age values.
        # ------------------------------------------------------------------------------
        ages_node_1 = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75,  80, 125] # noqa: E241
        ages_node_2 = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100, 125]

        self.assertEqual(len(ages_node_1), len(node_id_age_dist_list[0][1].ages_years))
        self.assertEqual(len(ages_node_2), len(node_id_age_dist_list[1][1].ages_years))
        self.assertEqual(len(ages_node_1), len(ages_node_2))
        for i in range(len(ages_node_1)):
            exp_age_1 = ages_node_1[i]
            exp_age_2 = ages_node_2[i]
            act_age_1 = node_id_age_dist_list[0][1].ages_years[i]
            act_age_2 = node_id_age_dist_list[1][1].ages_years[i]
            self.assertEqual(exp_age_1, act_age_1)
            self.assertEqual(exp_age_2, act_age_2)

    def test_to_fertility_distributions(self):
        """
        Verify that the fertility rate data is read correctly and transformed
        into data usable by EMOD
        """
        # Node 1 data is from Zimbabwe 2019
        # Node 2 data is from XXX 2024
        csv_filename = Path(__file__).parent.joinpath('inputs/test_year_age_rate/test_to_fertility_distributions.csv')

        fertility_yar = YearAgeRate( df=None, csv_filename=csv_filename )

        node_id_fertility_dist_list = fertility_yar.to_fertility_distributions()

        # ------------------------------------------------------------------------------------
        # --- Verify that there is fertility data for the two nodes defined in the CSV.
        # --- It returns a list of tuples where the first value in the tuple is the Node ID.
        # ------------------------------------------------------------------------------------
        self.assertEqual( 2, len(node_id_fertility_dist_list     ))
        self.assertEqual( 1,     node_id_fertility_dist_list[0][0]) # noqa: E241
        self.assertEqual( 2,     node_id_fertility_dist_list[1][0]) # noqa: E241

        # -------------------------------
        # --- Verify the data for Node 1
        # -------------------------------
        fert_dist_1 = node_id_fertility_dist_list[0][1]

        self.assertEqual(2, len(fert_dist_1._axis_scale_factors())) # age-years, simulation time - years
        self.assertEqual(365, fert_dist_1._axis_scale_factors()[0]) # noqa: E241 - 365 converts years to days
        self.assertEqual(1, fert_dist_1._axis_scale_factors()[1]) # noqa: E241 - 1 converts years to years

        self.assertEqual(2, len(fert_dist_1._population_groups)) # one for age and one for simulation time
        self.assertEqual(14, len(fert_dist_1._population_groups[0])) # node 1 had 7 ages that gets converted to 14 for the plateau
        self.assertEqual(60, len(fert_dist_1._population_groups[1])) # node 1 has 30 years that gets converted to 60 for the plateau

        # 2.74-e06 ~ 1/365 * 1/1000
        self.assertAlmostEqual(2.74e-06, fert_dist_1._rate_scale_factor(), delta=EPSILON)

        self.assertEqual(14, len(fert_dist_1.pregnancy_rate_matrix)) # one for each age
        self.assertEqual(60, len(fert_dist_1.pregnancy_rate_matrix[0])) # one for each year

        # -------------------------------------------------------------------------------------------
        # --- Verify that the result values have plateaus so that the linear interpolation in EMOD
        # --- doesn't do anything.  The idea is to match what we know from the input data versus
        # --- using linear interpolation and adding something that we don't really know.
        # ---
        # --- Notice that the both the columns and the rows have duplicates.  These duplicates are
        # --- on purpose so that you get one value for the full range ages & years for that bin.
        # --- Assume our x-y data is
        # --- ages  = [15.0, 19.999, 20.0, 24.999, 25.0, 29.999, 30.0, 34.999, 35.0, 39.999, 40.0, 44.999, 45.0, 125.0]
        # --- years = [1950.0, 1954.999, 1955.0, 1959.999, 1960.0, ..., 2090.0, 2094.999, 2095.0, 2101.0]
        # --- If the women is 26 years old and it is 1954, then the EMOD algorithm will draw the values
        # ---  X      Y         Z        age_index  year_index
        # --- 25      1950      171.7       4           0
        # --- 25      1954.999  171.7       4           1
        # --- 29.999  1950      171.7       5           0
        # --- 29.999  1954.999  171.7       5           1
        # -------------------------------------------------------------------------------------------

        self.assertAlmostEqual(25.000, fert_dist_1._population_groups[0][4], delta=EPSILON)
        self.assertAlmostEqual(29.999, fert_dist_1._population_groups[0][5], delta=EPSILON)
        self.assertAlmostEqual(1950.000, fert_dist_1._population_groups[1][0], delta=EPSILON)
        self.assertAlmostEqual(1954.999, fert_dist_1._population_groups[1][1], delta=EPSILON)

        self.assertAlmostEqual(171.7, fert_dist_1.pregnancy_rate_matrix[0][4], delta=EPSILON)
        self.assertAlmostEqual(171.7, fert_dist_1.pregnancy_rate_matrix[0][5], delta=EPSILON)
        self.assertAlmostEqual(171.7, fert_dist_1.pregnancy_rate_matrix[1][4], delta=EPSILON)
        self.assertAlmostEqual(171.7, fert_dist_1.pregnancy_rate_matrix[1][5], delta=EPSILON)

        # ----------------------------------------------------------------------
        # --- Continue the verification that the result values have plateaus by
        # --- showing how the rows and columns are duplicated
        # ----------------------------------------------------------------------
        fert_1_result_values_row_1n2 = [
            159.9, 159.9, 164.6, 164.6, 171.7, 171.7, 174.0, 174.0, 174.0, 174.0, # noqa: E241, E131
            171.7, 171.7, 127.9, 127.9, 110.6, 110.6, 102.7, 102.7, 100.1, 100.1, # noqa: E241, E131
            100.4, 100.4, 111.1, 111.1, 108.8, 108.8,  86.1,  86.1,  71.7,  71.7, # noqa: E241, E131
             60.2,  60.2,  51.0,  51.0,  43.6,  43.6,  37.4,  37.4,  32.3,  32.3, # noqa: E241, E131
             28.0,  28.0,  24.5,  24.5,  21.5,  21.5,  19.1,  19.1,  17.1,  17.1, # noqa: E241, E131
             15.4,  15.4,  14.0,  14.0,  12.8,  12.8,  11.7,  11.7,  10.8,  10.8  # noqa: E241, E131
        ]
        fert_1_result_values_row_13n14 = [
            40.4, 40.4, 41.6, 41.6, 43.4, 43.4, 44.0, 44.0, 44.0, 44.0,  # noqa: E241, E131, E126
            43.4, 43.4, 34.9, 34.9, 25.2, 25.2, 19.0, 19.0, 14.1, 14.1,  # noqa: E241, E131
            11.3, 11.3, 9.1, 9.1, 7.1, 7.1, 5.3, 5.3, 3.9, 3.9,  # noqa: E241, E131
            2.9, 2.9, 2.2, 2.2, 1.7, 1.7, 1.4, 1.4, 1.1, 1.1,  # noqa: E241, E131
            0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6, 0.5, 0.5,  # noqa: E241, E131
            0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.4, 0.4, 0.4  # noqa: E241, E131
        ]

        self.assertListEqual(fert_1_result_values_row_1n2, fert_dist_1.pregnancy_rate_matrix[ 0]) # noqa: E241
        self.assertListEqual(fert_1_result_values_row_1n2, fert_dist_1.pregnancy_rate_matrix[ 1]) # noqa: E241
        self.assertListEqual(fert_1_result_values_row_13n14, fert_dist_1.pregnancy_rate_matrix[12])
        self.assertListEqual(fert_1_result_values_row_13n14, fert_dist_1.pregnancy_rate_matrix[13])

        # -------------------------------
        # --- Verify the data for Node 2
        # -------------------------------
        fert_dist_2 = node_id_fertility_dist_list[1][1]

        self.assertEqual(2, len(fert_dist_2._axis_scale_factors())) # age-years, simulation time - years
        self.assertEqual(365, fert_dist_2._axis_scale_factors()[0]) # noqa: E241 - 365 converts years to days
        self.assertEqual(1, fert_dist_2._axis_scale_factors()[1]) # noqa: E241 - 1 converts years to years

        self.assertEqual(2, len(fert_dist_2._population_groups)) # one for age and one for simulation time
        # node 2 had 9 ages that gets converted to 18 for the plateau
        self.assertEqual(18, len(fert_dist_2._population_groups[0]))
        self.assertEqual(50, len(fert_dist_2._population_groups[1])) # node 2 has 25 years that gets converted to 50 for the plateau

        # 2.74-e06 ~ 1/365 * 1/1000
        self.assertAlmostEqual(2.74e-06, fert_dist_2._rate_scale_factor(), delta=EPSILON)

        self.assertEqual(18, len(fert_dist_2.pregnancy_rate_matrix)) # one for each age
        self.assertEqual(50, len(fert_dist_2.pregnancy_rate_matrix[0])) # one for each year

    def test_to_mortality_distributions(self):
        """
        Verify that the mortality rate data is read correctly and transformed
        into data usable by EMOD
        """
        # Node 1 data is from Zimbabwe 2019
        # Node 2 data is from XXX 2024
        csv_filename = Path(__file__).parent.joinpath('inputs/test_year_age_rate/test_to_mortality_distributions.csv')

        mortality_yar = YearAgeRate( df=None, csv_filename=csv_filename )

        node_id_mortality_dist_list = mortality_yar.to_mortality_distributions()

        # ------------------------------------------------------------------------------------
        # --- Verify that there is fertility data for the two nodes defined in the CSV.
        # --- It returns a list of tuples where the first value in the tuple is the Node ID.
        # ------------------------------------------------------------------------------------
        self.assertEqual( 2, len(node_id_mortality_dist_list     ))
        self.assertEqual([1, 2], sorted(node_id_mortality_dist_list.keys()))

        # -------------------------------
        # --- Verify the data for Node 1
        # -------------------------------
        node_id = 1
        mort_dist_1 = node_id_mortality_dist_list[node_id]

        self.assertEqual(2, len(mort_dist_1._axis_scale_factors())) # age-years, simulation time - years
        self.assertEqual(365, mort_dist_1._axis_scale_factors()[0]) # 365 converts years to days
        self.assertEqual(1, mort_dist_1._axis_scale_factors()[1]) # 1 converts years to years

        self.assertEqual(2, len(mort_dist_1._population_groups)) # one for age and one for simulation time
        self.assertEqual(44, len(mort_dist_1._population_groups[0])) # node 1 had 22 ages that gets converted to 44 for the plateau
        self.assertEqual(60, len(mort_dist_1._population_groups[1])) # node 1 has 30 years that gets converted to 60 for the plateau

        # 2.74-e03 ~ 1/365
        self.assertAlmostEqual(2.74e-03, mort_dist_1._rate_scale_factor(), delta=EPSILON)

        self.assertEqual(44, len(mort_dist_1.mortality_rate_matrix)) # one for each age
        self.assertEqual(60, len(mort_dist_1.mortality_rate_matrix[0])) # one for each year

        # -------------------------------------------------------------------------------------------
        # --- Continue the verification that the result values have plateaus by
        # --- showing how the rows and columns are duplicated
        # -------------------------------------------------------------------------------------------

        mort_1_result_values_row_1n2 = [
            0.112310010, 0.112310010, 0.101274200, 0.101274200, 0.088659640, 
            0.088659640, 0.076791620, 0.076791620, 0.072054510, 0.072054510, 
            0.067966733, 0.067966733, 0.061368500, 0.061368500, 0.051687570, 
            0.051687570, 0.053422340, 0.053422340, 0.049302061, 0.049302061, 
            0.045499565, 0.045499565, 0.041990342, 0.041990342, 0.038751773, 
            0.038751773, 0.035762984, 0.035762984, 0.030993030, 0.030993030, 
            0.027492770, 0.027492770, 0.024383070, 0.024383070, 0.021627460, 
            0.021627460, 0.019183420, 0.019183420, 0.017062210, 0.017062210, 
            0.015258630, 0.015258630, 0.013761950, 0.013761950, 0.012460210,
            0.012460210, 0.011573250, 0.011573250, 0.010856060, 0.010856060,
            0.010287420, 0.010287420, 0.009895590, 0.009895590, 0.009639410, 
            0.009639410, 0.009405560, 0.009405560, 0.009202170, 0.009202170
        ]
        mort_1_result_values_row_42n43 = [  
            0.78318134, 0.78318134, 0.81491078, 0.81491078, 0.84491151, 
            0.84491151, 0.87027173, 0.87027173, 0.88053655, 0.88053655, 
            0.88055605, 0.88055605, 0.88025302, 0.88025302, 0.85360182, 
            0.85360182, 0.68678036, 0.68678036, 0.45033440, 0.45033440, 
            0.38316446, 0.38316446, 0.41721346, 0.41721346, 0.66212252, 
            0.66212252, 0.65500522, 0.65500522, 0.65298059, 0.65298059, 
            0.64603177, 0.64603177, 0.63871537, 0.63871537, 0.63073142, 
            0.63073142, 0.62222871, 0.62222871, 0.61332866, 0.61332866, 
            0.60386309, 0.60386309, 0.59405529, 0.59405529, 0.58394566, 
            0.58394566, 0.57278791, 0.57278791, 0.56145306, 0.56145306, 
            0.55028269, 0.55028269, 0.53839314, 0.53839314, 0.52651700, 
            0.52651700, 0.51440266, 0.51440266, 0.50229072, 0.50229072
        ]

        self.assertListEqual(mort_1_result_values_row_1n2, mort_dist_1.mortality_rate_matrix[ 0]) # noqa: E241
        self.assertListEqual(mort_1_result_values_row_1n2, mort_dist_1.mortality_rate_matrix[ 1]) # noqa: E241
        self.assertListEqual(mort_1_result_values_row_42n43, mort_dist_1.mortality_rate_matrix[42])
        self.assertListEqual(mort_1_result_values_row_42n43, mort_dist_1.mortality_rate_matrix[43])

        # -------------------------------
        # --- Verify the data for Node 2
        # -------------------------------
        node_id = 2
        mort_dist_2 = node_id_mortality_dist_list[node_id]

        self.assertEqual(2, len(mort_dist_2._axis_scale_factors())) # age-years, simulation time - years
        self.assertEqual(365, mort_dist_2._axis_scale_factors()[0]) # noqa: E241 - 365 converts years to days
        self.assertEqual(1, mort_dist_2._axis_scale_factors()[1]) # noqa: E241 - 1 converts years to years

        self.assertEqual(2, len(mort_dist_2._population_groups)) # one for age and one for simulation time
        self.assertEqual(44, len(mort_dist_2._population_groups[0])) # node 2 had 22 ages that gets converted to 44 for the plateau
        self.assertEqual(302, len(mort_dist_2._population_groups[1])) # node 2 has 151 years that gets converted to 302 for the plateau - count year 2100-2101

        # 2.74-e03 ~ 1/365
        self.assertAlmostEqual(2.74e-03, mort_dist_2._rate_scale_factor(), delta=EPSILON)

        self.assertEqual(44, len(mort_dist_2.mortality_rate_matrix)) # one for each age
        self.assertEqual(302, len(mort_dist_2.mortality_rate_matrix[0])) # one for each year - count year 2100-2101


if __name__ == '__main__':
    unittest.main()
