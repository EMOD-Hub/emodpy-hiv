"""
This module contains methods for extracting data from UN World Population files.
https://population.un.org/wpp/

These methods output dataframes that can be used to initialize Demographic objects in EMOD.
"""
from typing import Union
from pathlib import Path
from importlib import resources
import pandas as pd
from emodpy_hiv.demographics.year_age_rate import YearAgeRate
import emodpy_hiv.countries.un_world_pop_data as un_data


POPULATION_FILES = {
    "2012": "WPP2012_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.XLS",
    "2015": "WPP2015_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.XLS",
    "2019": "WPP2019_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.xlsx",
    "2024": "WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx"
}

FERTILITY_FILES = {
    "2012": "WPP2012_FERT_F07_AGE_SPECIFIC_FERTILITY.xlsx",
    "2015": "WPP2015_FERT_F07_AGE_SPECIFIC_FERTILITY.XLS",
    "2019": "WPP2019_FERT_F07_AGE_SPECIFIC_FERTILITY.xlsx",
    "2024": "WPP2024_FERT_F02_FERTILITY_RATES_BY_5-YEAR_AGE_GROUPS_OF_MOTHER.xlsx"
}

MORTALITY_FILES = {
    "2012": {
        "male":   "WPP2012_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.xlsx",
        "female": "WPP2012_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx"
    },
    "2015": {
        "male":   "WPP2015_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.XLS",
        "female": "WPP2015_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.XLS"
    },
    "2019": {
        "male":   "WPP2019_MORT_F17_2_ABRIDGED_LIFE_TABLE_MALE.xlsx",
        "female": "WPP2019_MORT_F17_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx"
    },
    "2024": {
        "male":   "WPP2024_MORT_F07_2_ABRIDGED_LIFE_TABLE_MALE.xlsx",
        "female": "WPP2024_MORT_F07_3_ABRIDGED_LIFE_TABLE_FEMALE.xlsx"
    }
}

KNOWN_VERSIONS = ["2012", "2015", "2019", "2024"]
KNOWN_GENDERS = ["male", "female"]

def _check_version(version):
    if version not in KNOWN_VERSIONS:
        supported_versions = ""
        for index, v in enumerate(KNOWN_VERSIONS):
            supported_versions += v
            if (index + 1) < len(KNOWN_VERSIONS):
                supported_versions += ", "
        raise ValueError(f"'version'= '{version}' is not supported.\nOnly {supported_versions} formats are supported.")


def _check_gender(gender):
    if gender not in KNOWN_GENDERS:
        raise ValueError(f"'gender'= '{gender}' is not supported.\nOnly 'male' and 'female' are supported.")


def _get_population_filename(version):
    _check_version(version)
    un_data_root = resources.files(un_data)
    filename = Path(un_data_root, POPULATION_FILES[version])
    return filename


def _get_fertility_filename(version):
    _check_version(version)
    un_data_root = resources.files(un_data)
    filename = Path(un_data_root, FERTILITY_FILES[version])
    return filename


def _get_mortality_filename(version, gender):
    _check_version(version)
    _check_gender(gender)
    un_data_root = resources.files(un_data)
    filename = Path(un_data_root, MORTALITY_FILES[version][gender])
    return filename


def _check_country(country, possible_countries, filename):
    if country not in possible_countries:
        raise ValueError(f"'country'= '{country}' is not supported.\nThe file,\n{filename},\nonly supports the following countries:\n{possible_countries}")


def _check_filename(filename):
    if ((isinstance(filename, Path) and not filename.exists()) or
        (isinstance(filename, str) and not Path(filename).exists())):
        raise ValueError(f"The file does not exist.\n{filename}")


def _check_years(years, possible_years, filename):
    for year in years:
        if year not in possible_years:
            raise ValueError(f"'year'= '{year}' is not supported.\nThe file,\n{filename},\nonly supports the following years:\n{possible_years}")


def extract_population_by_age(country: str,
                              version: str,
                              years: list[float],
                              filename: Union[str,Path] = None):
    """
    This code is for extracting population by age data from the files
    downloaded from the UN World Pop (https://population.un.org/wpp/Download/Standard/Population/).
    The code assumes that the files is in Strict Open XML Spreadsheet format.  This format require
    us to use the 'calamine' engine to read the file.  The file is expected to be for both sexes
    and to have 5 year age bins. (i.e. WPP2019_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.xlsx,
    WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx)

    Args:
        country:
            The name of the country used in the spreadsheet for which you want to extract the data.

        version:
            A string with the year/version of the file.  Supported versions are 2012, 2015, 2019, 2024

        years:
            A list of years to get data for
            NOTE: Data files say it is for July 1st of the given year.

        filename:
            If not provided, the 'version' will be used to select from the known versions.  If a filename
            is provided, it is assumed to be file from the UN World Pop website.  It may have several sheets
            but the data will be extracted from the first two.  The 'estimates' sheet gives you data for the
            past while the 'medium variant' sheet gives you the data for the future. It is expected to be in
            the Strict Open XML Spreadsheet format.

    Return
        It will return a pandas DataFrame where each row is a year and the columns are for an age range
    """
    if filename is None:
        filename = _get_population_filename(version)
    else:
        _check_filename(filename)

    # ---------------------------------------------------------
    # --- Define column names and sheets to read the data from.
    # ---------------------------------------------------------
    COUNTRY_COL = "Major area, region, country or area *"
    PERIOD_COL  = "Reference date (as of 1 July)"  # noqa: E221
    AGE_00_04   = "0-4"                            # noqa: E221
    AGE_05_09   = "5-9"                            # noqa: E221
    AGE_10_14   = "10-14"                          # noqa: E221
    AGE_15_19   = "15-19"                          # noqa: E221
    AGE_20_24   = "20-24"                          # noqa: E221
    AGE_25_29   = "25-29"                          # noqa: E221
    AGE_30_34   = "30-34"                          # noqa: E221
    AGE_35_39   = "35-39"                          # noqa: E221
    AGE_40_44   = "40-44"                          # noqa: E221
    AGE_45_49   = "45-49"                          # noqa: E221
    AGE_50_54   = "50-54"                          # noqa: E221
    AGE_55_59   = "55-59"                          # noqa: E221
    AGE_60_64   = "60-64"                          # noqa: E221
    AGE_65_69   = "65-69"                          # noqa: E221
    AGE_70_74   = "70-74"                          # noqa: E221
    AGE_75_79   = "75-79"                          # noqa: E221
    AGE_80_84   = "80-84"                          # noqa: E221
    AGE_85_89   = "85-89"                          # noqa: E221
    AGE_90_94   = "90-94"                          # noqa: E221
    AGE_95_99   = "95-99"                          # noqa: E221
    AGE_100     = "100+"                           # noqa: E221
    AGE_80_PLUS = "80+"                            # noqa: E221

    sheet_list = []
    age_cols = [AGE_00_04, AGE_05_09, AGE_10_14, AGE_15_19,
                AGE_20_24, AGE_25_29, AGE_30_34, AGE_35_39,
                AGE_40_44, AGE_45_49, AGE_50_54, AGE_55_59,
                AGE_60_64, AGE_65_69, AGE_70_74, AGE_75_79,
                AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99,
                AGE_100]

    medium_cols = age_cols
    if version == "2012":
        sheet_list = ["ESTIMATES", "MEDIUM FERTILITY"]
        COUNTRY_COL = "Major area, region, country or area *"
        PERIOD_COL  = "Reference date (as of 1 July)" # noqa: E221
        medium_cols = age_cols.copy()
        age_cols.append(AGE_80_PLUS)
    elif version == "2015":
        sheet_list = ["ESTIMATES", "MEDIUM VARIANT"]
        COUNTRY_COL = "Major area, region, country or area *"
        PERIOD_COL  = "Reference date (as of 1 July)" # noqa: E221
        medium_cols = age_cols.copy()
        age_cols.append(AGE_80_PLUS)
    elif version == "2019":
        sheet_list = ["ESTIMATES", "MEDIUM VARIANT"]
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Reference date (as of 1 July)" # noqa: E221
    elif version == "2024":
        sheet_list = ["Estimates", "Medium variant"]
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Year" # noqa: E221
    else:
        raise ValueError("version '{0}' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported".format(version))

    # --------------------------------
    # --- Extract data from the sheets
    # --------------------------------
    df = pd.DataFrame()
    for sheet in sheet_list:
        cols_to_read = [COUNTRY_COL, PERIOD_COL]
        if "estimate" in sheet.lower():
            cols_to_read.extend(age_cols)
        else:
            cols_to_read.extend(medium_cols)

        df_sheet = pd.read_excel(filename,
                                 sheet_name=sheet,
                                 skiprows=16,
                                 usecols=cols_to_read,
                                 engine="calamine")
        _check_country(country, df_sheet[COUNTRY_COL].unique(), filename)
        df_sheet = df_sheet[df_sheet[COUNTRY_COL] == country]
        df = pd.concat([df, df_sheet])
    df = df.drop(COUNTRY_COL, axis=1)

    # -----------------------------------
    # --- Get the rows of data we want
    # -----------------------------------
    _check_years(years, df[PERIOD_COL].unique(), filename)
    df = df[df[PERIOD_COL].isin(years)]

    # ---------------------------------------------------------------
    # --- In the 2012, 2015 data, the Estimates sheet has this "80+" column
    # --- that can be used instead of the 80-84, etc columns.
    # --- NOTE: This is crappy logic, but I need to move on.
    # ---------------------------------------------------------------
    if version == "2012" or version == "2015":
        val = df[AGE_80_PLUS].iloc[0]
        has_80p = isinstance(val, float) or isinstance(val, int)
        if has_80p:
            df = df.drop([AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99, AGE_100], axis=1)
            for col in [AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99, AGE_100]:
                age_cols.remove(col)
        else:
            df = df.drop(AGE_80_PLUS, axis=1)
            age_cols.remove(AGE_80_PLUS)

    # -----------------------------------------------------------
    # --- rename the age columns so they are just the minimum age
    # -----------------------------------------------------------
    new_col_names = {}
    for col in age_cols:
        if col == AGE_80_PLUS:
            new_col_names[col] = "80"
        elif len(col) == 3:
            new_col_names[col] = col[0:1]
        elif len(col) == 5:
            new_col_names[col] = col[0:2]
        else:
            new_col_names[col] = col[0:3]
    df.rename(columns=new_col_names, inplace=True)

    # ------------------------------------------------------------------
    # --- Some columns can have the "...".  This changes those to zeros.
    # --- (This could go away with the 80+ handling.)
    # ------------------------------------------------------------------
    #df[year] = ( pd.to_numeric(df[year], errors='coerce' ).fillna(0) )

    # -----------------------------------------------------------------
    # --- The data is in thousands of people so multiply by 1000
    # --- and convert to integer since we want the value as an integer.
    # -----------------------------------------------------------------
    for column in df.columns:
        if column != PERIOD_COL:
            df[column] = df[column] * 1000

    return df


def extract_population_by_age_for_ingest_form(filename, country, version, years, gender):
    df = extract_population_by_age(filename=filename, country=country, version=version, years=years)

    ret_df = pd.DataFrame()
    ret_df["Year"      ] = 0  # noqa: E202
    ret_df["Gender"    ] = 0  # noqa: E202
    ret_df["AgeBin"    ] = 0  # noqa: E202
    ret_df["Population"] = 0

    for col_name in df.columns:
        if col_name != "Reference date (as of 1 July)":
            for index, value in df[col_name].items():
                year = df["Reference date (as of 1 July)"][index]
                age_bin = f"[{str(col_name)}:{str(int(col_name)+5)})"
                ret_df.loc[len(ret_df)] = [year, gender, age_bin, value]

    return ret_df


def extract_population_by_age_and_distribution(country: str,
                                               version: str,
                                               year: int = 1960,
                                               filename: Union[str, Path] = None):
    """
    This code is for extracting population by age data from the files
    downloaded from the UN World Pop (https://population.un.org/wpp/Download/Standard/Population/).
    The code assumes that the files is in Strict Open XML Spreadsheet format.  This format require
    us to use the 'calamine' engine to read the file.  The file is expected to be for both sexes
    and to have 5 year age bins. (i.e. WPP2019_POP_F15_1_ANNUAL_POPULATION_BY_AGE_BOTH_SEXES.xlsx,
    WPP2024_POP_F02_1_POPULATION_5-YEAR_AGE_GROUPS_BOTH_SEXES.xlsx)

    Args:
        country:
            The name of the country used in the spreadsheet for which you want to extract the data.

        version:
            A string with the year/version of the file.  Supported versions are 2012, 2015, 2019, 2024

        year:
            The year in the data to get the total population and age distribution for.  Default is 1960
            NOTE: Data files say it is for July 1st of the given year.

        filename:
            If not provided, the 'version' will be used to select from the known versions.  If a filename
            is provided, it is assumed to be file from the UN World Pop website.  It may have several sheets
            but the data will be only be extracted from the first sheet, 'estimates'.  The 'estimates' sheet
            gives you data for the past.  It is assumed that you are using this function to get the starting
            point of an EMOD simulation that starts in the past. It is expected to be in the Strict Open XML
            Spreadsheet format.

    Return:
        It will return the total population for the given year PLUS a YearAgeRate object where
        the "rate" column contains the fraction of people in that particular year and age ranges.
    """
    if filename is None:
        filename = _get_population_filename(version)
    else:
        _check_filename(filename)

    # ---------------------------------------------------------
    # --- Define column names and sheets to read the data from.
    # ---------------------------------------------------------
    COUNTRY_COL = "Major area, region, country or area *"
    PERIOD_COL  = "Reference date (as of 1 July)"  # noqa: E221
    AGE_00_04   = "0-4"                            # noqa: E221
    AGE_05_09   = "5-9"                            # noqa: E221
    AGE_10_14   = "10-14"                          # noqa: E221
    AGE_15_19   = "15-19"                          # noqa: E221
    AGE_20_24   = "20-24"                          # noqa: E221
    AGE_25_29   = "25-29"                          # noqa: E221
    AGE_30_34   = "30-34"                          # noqa: E221
    AGE_35_39   = "35-39"                          # noqa: E221
    AGE_40_44   = "40-44"                          # noqa: E221
    AGE_45_49   = "45-49"                          # noqa: E221
    AGE_50_54   = "50-54"                          # noqa: E221
    AGE_55_59   = "55-59"                          # noqa: E221
    AGE_60_64   = "60-64"                          # noqa: E221
    AGE_65_69   = "65-69"                          # noqa: E221
    AGE_70_74   = "70-74"                          # noqa: E221
    AGE_75_79   = "75-79"                          # noqa: E221
    AGE_80_84   = "80-84"                          # noqa: E221
    AGE_85_89   = "85-89"                          # noqa: E221
    AGE_90_94   = "90-94"                          # noqa: E221
    AGE_95_99   = "95-99"                          # noqa: E221
    AGE_100     = "100+"                           # noqa: E221
    AGE_80_PLUS = "80+"                            # noqa: E221

    sheet_list = []
    age_cols = [AGE_00_04, AGE_05_09, AGE_10_14, AGE_15_19,
                AGE_20_24, AGE_25_29, AGE_30_34, AGE_35_39,
                AGE_40_44, AGE_45_49, AGE_50_54, AGE_55_59,
                AGE_60_64, AGE_65_69, AGE_70_74, AGE_75_79,
                AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99,
                AGE_100]

    if version == "2012" or version == "2015":
        sheet_list = ["ESTIMATES"] # "MEDIUM FERTILITY"
        COUNTRY_COL = "Major area, region, country or area *"
        PERIOD_COL  = "Reference date (as of 1 July)" # noqa: E221
        age_cols.append(AGE_80_PLUS)
    elif version == "2019":
        sheet_list = ["ESTIMATES"] # "MEDIUM VARIANT"
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Reference date (as of 1 July)" # noqa: E221
    elif version == "2024":
        sheet_list = ["Estimates"] # "Medium variant"
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Year" # noqa: E221
    else:
        raise ValueError("version '{0}' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported".format(version))

    cols_to_read = [COUNTRY_COL, PERIOD_COL]
    cols_to_read.extend(age_cols)

    # --------------------------------
    # --- Extract data from the sheets
    # --------------------------------
    df = pd.DataFrame()
    for sheet in sheet_list:
        df_sheet = pd.read_excel(filename,
                                 sheet_name=sheet,
                                 skiprows=16,
                                 usecols=cols_to_read,
                                 engine="calamine")
        _check_country(country, df_sheet[COUNTRY_COL].unique(), filename)
        df_sheet = df_sheet[df_sheet[COUNTRY_COL] == country]
        df = pd.concat([df, df_sheet])
    df = df.drop(COUNTRY_COL, axis=1)

    # -----------------------------------
    # --- Get the one row of data we want
    # -----------------------------------
    df = df[df[PERIOD_COL] == year]

    # ---------------------------------------------------------------
    # --- In the 2012, 2015 data, the Estimates sheet has this "80+" column
    # --- that can be used instead of the 80-84, etc columns.
    # --- NOTE: This is crappy logic, but I need to move on.
    # ---------------------------------------------------------------
    if version == "2012" or version == "2015":
        val = df[AGE_80_PLUS].iloc[0]
        has_80p = isinstance(val, float) or isinstance(val, int)
        if has_80p:
            df = df.drop([AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99, AGE_100], axis=1)
            for col in [AGE_80_84, AGE_85_89, AGE_90_94, AGE_95_99, AGE_100]:
                age_cols.remove(col)
        else:
            df = df.drop(AGE_80_PLUS, axis=1)
            age_cols.remove(AGE_80_PLUS)

    # -----------------------------------------------------------
    # --- rename the age columns so they are just the minimum age
    # -----------------------------------------------------------
    new_col_names = {}
    for col in age_cols:
        if col == AGE_80_PLUS:
            new_col_names[col] = "80"
        elif len(col) == 3:
            new_col_names[col] = col[0:1]
        elif len(col) == 5:
            new_col_names[col] = col[0:2]
        else:
            new_col_names[col] = col[0:3]
    df.rename(columns=new_col_names, inplace=True)

    # -------------------------------------------------------------------
    # --- Transpose the data so we have rows of min ages for our one Year
    # -------------------------------------------------------------------
    df = df.set_index(PERIOD_COL, inplace=False)
    df = df.transpose()
    df = df.rename_axis("tmp_min_age")

    # ------------------------------------------------------------------
    # --- Some columns can have the "...".  This changes those to zeros.
    # --- (This could go away with the 80+ handling.)
    # ------------------------------------------------------------------
    df[year] = (pd.to_numeric(df[year], errors='coerce').fillna(0))

    # ---------------------------------------------------------------
    # --- Change the data to the fraction of people in that age range
    # --- since this is supposed to be an age distribution.
    # ---------------------------------------------------------------
    total_pop = df[year].sum()
    df = df / total_pop

    # -----------------------------------------------------------------
    # --- The data is in thousands of people so multiply by 1000
    # --- and convert to integer since we want the value as an integer.
    # -----------------------------------------------------------------
    total_pop = int(1000 * total_pop)

    # --------------------------------------------------
    # --- Convert dataframe into a YearAgeRate dataframe
    # --------------------------------------------------
    df[YearAgeRate.COL_NAME_MIN_AGE ] = df.index.values                                 # noqa: E202
    df[YearAgeRate.COL_NAME_MIN_AGE ] = df[YearAgeRate.COL_NAME_MIN_AGE].astype(float)  # noqa: E202
    df[YearAgeRate.COL_NAME_NODE_ID ] = 0                                               # noqa: E202
    df[YearAgeRate.COL_NAME_MIN_YEAR] = year
    df.rename({year: YearAgeRate.COL_NAME_RATE}, axis=1, inplace=True)

    df[YearAgeRate.COL_NAME_RATE] = df[YearAgeRate.COL_NAME_RATE].astype(float).round(8)
    df = df[YearAgeRate.COL_NAMES]
    df.reset_index()

    return total_pop, YearAgeRate(df)


def extract_fertility(country: str,
                      version: str,
                      filename: Union[str, Path] = None):
    """
    This code is for extracting fertility rates for the given country from the fertility files
    downloaded from the UN World Pop (https://population.un.org/wpp/Download/Standard/Fertility/).
    The code assumes that the files is in Strict Open XML Spreadsheet format.  This format require
    us to use the 'calamine' engine to read the file.  The file is expected to be the Age Specific
    rates (i.e. WPP2012_FERT_F07_AGE_SPECIFIC_FERTILITY, WPP2024_FERT_F02_FERTILITY_RATES_BY_5-YEAR_AGE_GROUPS_OF_MOTHER)

    Args:
        country
            The name of the country used in the spreadsheet for which you want to extract the data.

        version
            A string with the year/version of the file.  Supported versions are 2012, 2015, 2019, 2024

        filename
            If not provided, the 'version' will be used to select from the known versions.  If a filename
            is provided, it is assumed to be file from the UN World Pop website.  It may have several sheets
            but the data will be extracted from the first two.  The 'estimates' sheet gives you data for the
            past while the 'medium variant' sheet gives you the data for the future. It is expected to be in
            the Strict Open XML Spreadsheet format.

    Return
        A YearAgeRate object containing the fertility data in the given file.
    """
    if filename is None:
        filename = _get_fertility_filename(version)
    else:
        _check_filename(filename)

    # ---------------------------------------------------------
    # --- Define column names and sheets to read the data from.
    # ---------------------------------------------------------
    PERIOD_COL  = "Period" # noqa: E221
    AGE_15_19   = "15-19"  # noqa: E221
    AGE_20_24   = "20-24"  # noqa: E221
    AGE_25_29   = "25-29"  # noqa: E221
    AGE_30_34   = "30-34"  # noqa: E221
    AGE_35_39   = "35-39"  # noqa: E221
    AGE_40_44   = "40-44"  # noqa: E221
    AGE_45_49   = "45-49"  # noqa: E221

    age_cols = [AGE_15_19, AGE_20_24, AGE_25_29, AGE_30_34, AGE_35_39, AGE_40_44, AGE_45_49]

    if version == "2012":
        sheet_list = ["ESTIMATES", "MEDIUM FERTILITY"]
        COUNTRY_COL = "Major area, region, country or area *"
    elif version == "2015":
        sheet_list = ["ESTIMATES", "MEDIUM VARIANT"]
        COUNTRY_COL = "Major area, region, country or area *"
    elif version == "2019":
        sheet_list = ["ESTIMATES", "MEDIUM VARIANT"]
        COUNTRY_COL = "Region, subregion, country or area *"
    elif version == "2024":
        sheet_list = ["Estimates", "Medium variant"]
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Year" # noqa: E221
        AGE_10_14 = "10-14"
        AGE_50_54 = "50-54"
        age_cols.insert(0, AGE_10_14)
        age_cols.append(AGE_50_54)
    else:
        raise ValueError("version '{0}' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported".format(version))

    cols_to_read = [COUNTRY_COL, PERIOD_COL]
    cols_to_read.extend(age_cols)

    # --------------------------------
    # --- Extract data from the sheets
    # --------------------------------
    df = pd.DataFrame()
    for sheet in sheet_list:
        df_sheet = pd.read_excel(filename,
                                 sheet_name=sheet,
                                 skiprows=16,
                                 usecols=cols_to_read,
                                 engine="calamine")
        _check_country(country, df_sheet[COUNTRY_COL].unique(), filename)
        df_sheet = df_sheet[df_sheet[COUNTRY_COL] == country]
        df = pd.concat([df, df_sheet])

    df = df.drop(COUNTRY_COL, axis=1)

    # ------------------------------------------------------------
    # --- Change the Period column to only contain min value/year
    # ------------------------------------------------------------
    if version == "2012" or version == "2015" or version == "2019":
        df[PERIOD_COL] = df[PERIOD_COL].str.slice_replace(4, 9, "").astype(float)

    # -----------------------------------------------------------
    # --- rename the age columns so they are just the minimum age
    # -----------------------------------------------------------
    new_col_names = {}
    for col in age_cols:
        new_col_names[col] = col[0:2]
    df.rename(columns=new_col_names, inplace=True)

    df = pd.melt(df, id_vars=[PERIOD_COL], var_name=YearAgeRate.COL_NAME_MIN_AGE, value_name=YearAgeRate.COL_NAME_RATE)

    # ----------------------------------------------------------
    # --- Convert dataframe into a YearAgeRate dataframe format
    # ----------------------------------------------------------
    df.rename({PERIOD_COL: YearAgeRate.COL_NAME_MIN_YEAR}, axis=1, inplace=True)
    df[YearAgeRate.COL_NAME_MIN_AGE ] = df[YearAgeRate.COL_NAME_MIN_AGE ].astype(float)    # noqa: E202
    df[YearAgeRate.COL_NAME_MIN_YEAR] = df[YearAgeRate.COL_NAME_MIN_YEAR].astype(float)
    df[YearAgeRate.COL_NAME_NODE_ID ] = 0                                                  # noqa: E202
    df = df.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE], ascending=True)

    df[YearAgeRate.COL_NAME_RATE] = df[YearAgeRate.COL_NAME_RATE].astype(float).round(1)
    df = df[YearAgeRate.COL_NAMES]

    return YearAgeRate(df=df)


def extract_mortality(country: str,
                      version: str,
                      gender: str = None,
                      filename: Union[str, Path] = None):
    """
    This code is for extracting mortality rates for the given country from the mortality files
    downloaded from the UN World Pop (https://population.un.org/wpp/Download/Standard/Mortality/).
    The code assumes that the files is in Strict Open XML Spreadsheet format.  This format require
    us to use the 'calamine' engine to read the file.  The file is expected to be for one gender
    and to be the Abriged Life Table.

    Args:
        country:
            The name of the country used in the spreadsheet for which you want to extract the data.

        version:
            A string with the year/version of the file.  Supported versions are 2012, 2015, 2019, 2024

        gender:
            The gender of the data to be extracted.  Possible values are 'male' and 'female'.
            Required if the filename is not provided.

        filename:
            If not provided, the 'version' will be used to select from the known versions.  If a filename
            is provided, it is assumed to be file from the UN World Pop website.  It may have several sheets
            but the data will be extracted from the first one plus the next one or two.  The 'estimates'
            sheet gives you data for the past while the 'medium XXX' sheets give you the data for the future.
            It is expected to be in the Strict Open XML Spreadsheet format.

    Return
        A YearAgeRate object containing the mortality data in the given file.
    """
    if filename is None:
        filename = _get_mortality_filename(version, gender)
    else:
        _check_filename(filename)

    # ---------------------------------------------------------
    # --- Define column names and sheets to read the data from.
    # ---------------------------------------------------------
    COUNTRY_COL      = "Region"                     # noqa: E221
    PERIOD_COL       = "Period"                     # noqa: E221
    AGE_COL          = "Age (x)"                    # noqa: E221
    AGE_INTERVAL_COL = "Age interval (n)"
    DEATH_RATE_COL   = "Central death rate m(x,n)"  # noqa: E221

    sheet_list = []
    if version == "2012":
        COUNTRY_COL = "Major area, region, country or area *"
        sheet_list = ["ESTIMATES", "MEDIUM_2010-2050", "MEDIUM_2050-2100"]
    elif version == "2015":
        COUNTRY_COL = "Major area, region, country or area *"
        sheet_list = ["ESTIMATES", "MEDIUM 2015-2050", "MEDIUM 2050-2100"]
    elif version == "2019":
        COUNTRY_COL = "Region, subregion, country or area *"
        sheet_list = ["ESTIMATES", "MEDIUM 2020-2050", "MEDIUM 2050-2100"]
    elif version == "2024":
        COUNTRY_COL = "Region, subregion, country or area *"
        PERIOD_COL  = "Year" # noqa: E221
        sheet_list = ["Estimates", "Medium variant"]
    else:
        raise ValueError("version '{0}' is not supported.\nOnly 2012, 2015, 2019, 2024 formats are supported".format(version))

    cols_to_read = [COUNTRY_COL, PERIOD_COL, AGE_COL, AGE_INTERVAL_COL, DEATH_RATE_COL]

    col_rename_dict = {
        PERIOD_COL    : YearAgeRate.COL_NAME_MIN_YEAR,  # noqa: E203
        AGE_COL       : YearAgeRate.COL_NAME_MIN_AGE,   # noqa: E203
        DEATH_RATE_COL: YearAgeRate.COL_NAME_RATE
    }

    # --------------------------------
    # --- Extract data from the sheets
    # --------------------------------
    df = pd.DataFrame()
    for sheet in sheet_list:
        df_sheet = pd.read_excel(filename,
                                 sheet_name=sheet,
                                 skiprows=16,
                                 usecols=cols_to_read,
                                 engine="calamine")
        _check_country(country, df_sheet[COUNTRY_COL].unique(), filename)
        df_sheet = df_sheet[df_sheet[COUNTRY_COL] == country]
        df = pd.concat([df, df_sheet])

    # ------------------------------------------------------------
    # --- Change the Period column to only contain min value/year
    # ------------------------------------------------------------
    if version == "2012" or version == "2015" or version == "2019":
        df[PERIOD_COL] = df[PERIOD_COL].str.slice_replace(4, 9, "").astype(float)

    # ----------------------------------------------------------
    # --- Convert dataframe into a YearAgeRate dataframe format
    # ----------------------------------------------------------
    df.rename(col_rename_dict, axis=1, inplace=True)

    df = df.drop([COUNTRY_COL, AGE_INTERVAL_COL], axis=1)

    df[YearAgeRate.COL_NAME_NODE_ID ] = 0                                                 # noqa: E202
    df[YearAgeRate.COL_NAME_MIN_YEAR] = df[YearAgeRate.COL_NAME_MIN_YEAR].astype(float)
    df[YearAgeRate.COL_NAME_MIN_AGE ] = df[YearAgeRate.COL_NAME_MIN_AGE ].astype(float)   # noqa: E202
    df[YearAgeRate.COL_NAME_RATE    ] = df[YearAgeRate.COL_NAME_RATE    ].round(8)        # noqa: E202
    df = df[YearAgeRate.COL_NAMES]

    return YearAgeRate(df=df)


