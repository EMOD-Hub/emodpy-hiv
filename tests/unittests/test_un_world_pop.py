import unittest
import pytest
import pandas as pd
from pathlib import Path
import sys

import emodpy_hiv.demographics.un_world_pop as unwp


parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

@pytest.mark.unit

class TestUnWorldPop(unittest.TestCase):
    """
    The following tests verify that the age, fertility, and mortality data can be extracted
    from these sample files of the UN World Population data.  The test files were originally
    the files downloaded but were reduced to a handful of countries in order to make the
    tests faster.

    Each tests extracts the data from the UN World Pop file and then compares it to an
    existing CSV file that was validated to be the data we intended to extract.
    """

    def setUp(self):
        pass

    def _read_file_to_string( self, fn ):
        with open(fn, 'r') as handle:
            str = handle.read().replace("\r\n", "\n")
        return str

    def test_age_distribution_2012(self):
        country = "Zimbabwe"
        version = "2012"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2012_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.XLS')

        total_pop, act_yar = unwp.extract_population_by_age_and_distribution(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_age_distribution_2012.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(3752390, total_pop)
        self.assertEqual(exp_str, act_str)

        # test selecting the file given the country and version
        total_pop, act_yar = unwp.extract_population_by_age_and_distribution(country, version)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        self.assertEqual(3752390, total_pop)
        self.assertEqual(exp_str, act_str)


    def test_age_distribution_2015(self):
        country = "Zimbabwe"
        version = "2015"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2015_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.XLS')

        total_pop, act_yar = unwp.extract_population_by_age_and_distribution(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_age_distribution_2015.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(3752390, total_pop)
        self.assertEqual(exp_str, act_str)

    def test_age_distribution_2019(self):
        country = "Zimbabwe"
        version = "2019"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2019_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.xlsx')

        total_pop, act_yar = unwp.extract_population_by_age_and_distribution(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_age_distribution_2019.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(3776678, total_pop)
        self.assertEqual(exp_str, act_str)

    def test_age_distribution_2024(self):
        country = "Zimbabwe"
        version = "2024"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx')

        total_pop, act_yar = unwp.extract_population_by_age_and_distribution(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_age_distribution_2024.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(3809388, total_pop)
        self.assertEqual(exp_str, act_str)

    def test_mortality_2012(self):
        country = "Zimbabwe"
        version = "2012"
        input_fn_female = Path(__file__).parent.joinpath('inputs/WPP2012_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx')
        input_fn_male   = Path(__file__).parent.joinpath('inputs/WPP2012_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.xlsx'  ) # noqa: E221

        exp_fn_female = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2012_female.csv')
        exp_fn_male   = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2012_male.csv'  ) # noqa: E221

        female_act_yar = unwp.extract_mortality(country, version, filename=input_fn_female)
        male_act_yar   = unwp.extract_mortality(country, version, filename=input_fn_male  ) # noqa: E241, E221

        # female_act_yar.df.to_csv(exp_fn_female,index=False)
        # male_act_yar.df.to_csv  (exp_fn_male,  index=False)
        female_act_str = female_act_yar.df.to_csv(index=False).replace("\r\n", "\n")
        male_act_str   = male_act_yar.df.to_csv(index=False).replace("\r\n", "\n") # noqa: E221

        female_exp_str = self._read_file_to_string(exp_fn_female)
        male_exp_str   = self._read_file_to_string(exp_fn_male) # noqa: E221

        self.assertEqual(female_exp_str, female_act_str)
        self.assertEqual(male_exp_str,   male_act_str  ) # noqa: E241

        # test selecting the file given the country and version
        female_act_yar = unwp.extract_mortality(country, version, gender="female")
        self.assertEqual(female_exp_str, female_act_str)

    def test_mortality_2015(self):
        country = "Zimbabwe"
        version = "2015"
        input_fn_female = Path(__file__).parent.joinpath('inputs/WPP2015_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.XLS')
        input_fn_male   = Path(__file__).parent.joinpath('inputs/WPP2015_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.XLS'  ) # noqa: E221

        exp_fn_female = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2015_female.csv')
        exp_fn_male   = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2015_male.csv'  ) # noqa: E221

        female_act_yar = unwp.extract_mortality(country, version, filename=input_fn_female)
        male_act_yar   = unwp.extract_mortality(country, version, filename=input_fn_male  ) # noqa: E241, E221

        # female_act_yar.df.to_csv(exp_fn_female,index=False)
        # male_act_yar.df.to_csv  (exp_fn_male,  index=False)
        female_act_str = female_act_yar.df.to_csv(index=False).replace("\r\n", "\n")
        male_act_str   = male_act_yar.df.to_csv(index=False).replace("\r\n", "\n") # noqa: E221

        female_exp_str = self._read_file_to_string(exp_fn_female)
        male_exp_str   = self._read_file_to_string(exp_fn_male) # noqa: E221

        female_act_yar.df.to_csv(exp_fn_female, index=False)
        male_act_yar.df.to_csv(exp_fn_male, index=False)

        self.assertEqual(female_exp_str, female_act_str)
        self.assertEqual(male_exp_str,   male_act_str  ) # noqa: E241

    def test_mortality_2019(self):
        country = "Zimbabwe"
        version = "2019"
        input_fn_female = Path(__file__).parent.joinpath('inputs/WPP2019_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx')
        input_fn_male   = Path(__file__).parent.joinpath('inputs/WPP2019_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.xlsx'  ) # noqa: E221

        exp_fn_female = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2019_female.csv')
        exp_fn_male   = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2019_male.csv'  ) # noqa: E221

        female_act_yar = unwp.extract_mortality(country, version, filename=input_fn_female)
        male_act_yar   = unwp.extract_mortality(country, version, filename=input_fn_male  ) # noqa: E241, E221

        # female_act_yar.df.to_csv(exp_fn_female,index=False)
        # male_act_yar.df.to_csv  (exp_fn_male,  index=False)
        female_act_str = female_act_yar.df.to_csv(index=False).replace("\r\n", "\n")
        male_act_str   = male_act_yar.df.to_csv(index=False).replace("\r\n", "\n") # noqa: E221

        female_exp_str = self._read_file_to_string(exp_fn_female)
        male_exp_str   = self._read_file_to_string(exp_fn_male  ) # noqa: E221

        self.assertEqual(female_exp_str, female_act_str)
        self.assertEqual(male_exp_str,   male_act_str  ) # noqa: E241

    def test_mortality_2024(self):
        country = "Zimbabwe"
        version = "2024"
        input_fn_female = Path(__file__).parent.joinpath('inputs/WPP2024_MORT_F07_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx')
        input_fn_male   = Path(__file__).parent.joinpath('inputs/WPP2024_MORT_F07_2_ABRIDGED_LIFE_TABLE_MALE.xlsx'  ) # noqa: E221

        exp_fn_female = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2024_female.csv')
        exp_fn_male   = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_mortality_2024_male.csv'  ) # noqa: E221

        female_act_yar = unwp.extract_mortality(country, version, filename=input_fn_female)
        male_act_yar   = unwp.extract_mortality(country, version, filename=input_fn_male  ) # noqa: E221, E241

        # female_act_yar.df.to_csv(exp_fn_female,index=False)
        # male_act_yar.df.to_csv  (exp_fn_male,  index=False)
        female_act_str = female_act_yar.df.to_csv(index=False).replace("\r\n", "\n")
        male_act_str   = male_act_yar.df.to_csv(index=False).replace("\r\n", "\n") # noqa: E221

        female_exp_str = self._read_file_to_string(exp_fn_female)
        male_exp_str   = self._read_file_to_string(exp_fn_male) # noqa: E221

        self.assertEqual(female_exp_str, female_act_str)
        self.assertEqual(male_exp_str,   male_act_str  ) # noqa: E241

    def test_fertility_2012(self):
        country = "Zimbabwe"
        version = "2012"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2012_FERT_F07_AGE_SPECIFIC_FERTILITY.xlsx')

        act_yar = unwp.extract_fertility(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_fertility_2012.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(exp_str, act_str)

        # test selecting the file given the country and version
        act_yar = unwp.extract_fertility(country, version)
        self.assertEqual(exp_str, act_str)


    def test_fertility_2015(self):
        country = "Zimbabwe"
        version = "2015"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2015_FERT_F07_AGE_SPECIFIC_FERTILITY.XLS')

        act_yar = unwp.extract_fertility(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_fertility_2015.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(exp_str, act_str)

    def test_fertility_2019(self):        
        country = "Zimbabwe"
        version = "2019"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2019_FERT_F07_AGE_SPECIFIC_FERTILITY.xlsx')

        act_yar = unwp.extract_fertility(country, version, filename=input_fn)
        act_str = act_yar.df.to_csv(index=False).replace("\r\n", "\n")

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_fertility_2019.csv')
        # act_yar.df.to_csv(exp_fn,index=False)
        exp_str = self._read_file_to_string(exp_fn)

        self.assertEqual(exp_str, act_str)

    def test_fertility_2024(self):        
        country = "Zimbabwe"
        version = "2024"
        input_fn = Path(__file__).parent.joinpath('inputs/WPP2024_FERT_F02_FERTILITY_RATES_BY_5-YEAR_AGE_GROUPS_OF_MOTHER.xlsx')

        act_yar = unwp.extract_fertility(country, version, filename=input_fn)
        act_yar.df = act_yar.df.reset_index(drop=True)

        exp_fn = Path(__file__).parent.joinpath('inputs/test_un_world_pop/test_fertility_2024.csv')
        exp_df = pd.read_csv(exp_fn)
        self.assertTrue(all(act_yar.df == exp_df))

    def test_error_handling_extract_population_by_age(self):
        with self.assertRaises(ValueError) as context:
            df = unwp.extract_population_by_age(country="XXXXXXXX", version="2012", years=[1960, 1961, 1962], filename=None)
        self.assertTrue("'country'= 'XXXXXXXX' is not supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            df = unwp.extract_population_by_age(country="Zambia", version="XXXXXXXX", years=[1960, 1961, 1962], filename=None)
        self.assertTrue("'version'= 'XXXXXXXX' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported." in str(context.exception),
                        msg=str(context.exception))

        with self.assertRaises(ValueError) as context:
            df = unwp.extract_population_by_age(country="Zambia", version="2012", years=[1960, 9999, 1962], filename=None)
        self.assertTrue("'year'= '9999' is not supported.\nThe file," in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            df = unwp.extract_population_by_age(country="Zambia", version="2012", years=[1960, 1961, 1962], filename="XXXXXXXX")
        self.assertTrue("The file does not exist.\nXXXXXXXX" in str(context.exception),
                        msg=str(context.exception))

    def test_error_handling_extract_population_by_age_and_distribution(self):
        with self.assertRaises(ValueError) as context:
            total_pop, act_yar = unwp.extract_population_by_age_and_distribution("XXXXXXXX", "2012", filename=None)
        self.assertTrue("'country'= 'XXXXXXXX' is not supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            total_pop, act_yar = unwp.extract_population_by_age_and_distribution("Zambia", "XXXXXXXX", filename=None)
        self.assertTrue("'version'= 'XXXXXXXX' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            total_pop, act_yar = unwp.extract_population_by_age_and_distribution("Zambia", "2012", filename="XXXXXXXX")
        self.assertTrue("The file does not exist.\nXXXXXXXX" in str(context.exception),
                        msg=str(context.exception))

    def test_error_handling_extract_fertility(self):
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_fertility("XXXXXXXX", "2012", filename=None)
        self.assertTrue("'country'= 'XXXXXXXX' is not supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_fertility("Zambia", "XXXXXXXX", filename=None)
        self.assertTrue("'version'= 'XXXXXXXX' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_fertility("Zambia", "2012", filename="XXXXXXXX")
        self.assertTrue("The file does not exist.\nXXXXXXXX" in str(context.exception),
                        msg=str(context.exception))

    def test_error_handling_extract_mortality(self):
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_mortality(country="XXXXXXXX", version="2012", gender="male", filename=None)
        self.assertTrue("'country'= 'XXXXXXXX' is not supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_mortality(country="Zambia", version="XXXXXXXX", gender="male", filename=None)
        self.assertTrue("'version'= 'XXXXXXXX' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_mortality(country="Zambia", version="2012", gender="XXXXXXXX", filename=None)
        self.assertTrue("'gender'= 'XXXXXXXX' is not supported.\nOnly 'male' and 'female' are supported." in str(context.exception),
                        msg=str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            act_yar = unwp.extract_mortality(country="Zambia", version="2012", gender="male", filename="XXXXXXXX")
        self.assertTrue("The file does not exist.\nXXXXXXXX" in str(context.exception),
                        msg=str(context.exception))



if __name__ == '__main__':
    unittest.main()
