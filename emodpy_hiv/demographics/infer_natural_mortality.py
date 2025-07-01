
import os
import pandas as pd
import numpy as np
from functools import reduce
from pathlib import Path
from importlib import resources
import argparse

from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

import emodpy_hiv.countries as countries

from emodpy_hiv.demographics.year_age_rate import YearAgeRate
import emodpy_hiv.demographics.year_age_rate as year_age_rate
import emodpy_hiv.demographics.un_world_pop as unwp



def infer_natural_mortality(year_age_rate_data: YearAgeRate,
                            interval_fit: tuple[float, float] = None,
                            predict_horizon: float = 2100.0) -> YearAgeRate:
    """
    Convert the raw mortality data to what would have been the expected natural mortality had HIV
    not caused a spike in mortality.  This algorithm assumes that during the 'interval_fit'
    mortality rates had a relatively steady decline (i.e. less people were dying each year),
    but shortly after the 'interval_fit' there was a spike in mortality.  The algorithm uses
    the data in the 'interval_fit' and extrapolates it out over the time period.

    It assumes that the input data is for only one node.

    Args:
        year_age_rate_data: This is a YearAgeRate data object containing the raw mortality data,
            probably output from the **extract_mortality()** function
        interval_fit: This tuple contains the range of years that we want to determine the
            mortality trend before the HIV epidemic.  These years will be extrapolated
            from the end of the fit forward.
        predict_horizon: This determines how far out the data will be extrapolated.

    Returns:
        A YearAgeRate object with the inferred mortality rates.
    """

    if len(year_age_rate_data.df[YearAgeRate.COL_NAME_NODE_ID].unique().tolist()) != 1:
        node_id_list = year_age_rate_data.df[YearAgeRate.COL_NAME_NODE_ID].unique().tolist()
        msg  =  "Invalid number of nodes in the YearAgeRate object.\n"         # noqa: E221, E222
        msg +=  "The algorithm currently only supports one node at a time.\n"  # noqa: E222
        msg += f"The input has the following nodes: {node_id_list}"
        raise ValueError(msg)

    if interval_fit is None:
        interval_fit = (1970, 1980)
    elif interval_fit[1] <= interval_fit[0]:
        msg  =  "Invalid 'interval_fit' values.\n" # noqa: E221, E222
        msg += f"The first value in the tuple, {interval_fit[0]} must be strictly less\n"
        msg += f"than the second value, {interval_fit[1]}."
        raise ValueError(msg)

    if predict_horizon <= interval_fit[1]:
        msg  = "Invalid value of 'predict_horizon' with respect to 'interval_fit'.\n" # noqa: E221
        msg += f"The 'predicted_horizon' (={predict_horizon}) must be greater than\n"
        msg += f"the second value of the 'interval_fit[1]' (={interval_fit[1]})."

    df_mort = year_age_rate_data.df.copy()

    # ---------------------------------------------------
    # --- Log transform the data and sort by year and age
    # ---------------------------------------------------
    df_mort[YearAgeRate.COL_NAME_RATE] = df_mort[YearAgeRate.COL_NAME_RATE].apply(lambda x: np.log(x))
    df_mort.sort_values([YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE], inplace=True)

    # -------------------------------------------------------------------
    # --- Extract the data for that exists BEFORE the reference interval.
    # --- Do not include any data from the interval
    # --- inclusive=left means the right is not inclusive.
    # -------------------------------------------------------------------
    min_year_col = df_mort[YearAgeRate.COL_NAME_MIN_YEAR]
    df_before_time = df_mort[min_year_col.between(0, interval_fit[0], inclusive='left')].copy()

    # -------------------------------------------------------------------------
    # --- Get list of ages to extrapolate the data for and setup the dataframe
    # -------------------------------------------------------------------------
    age_list = df_mort[YearAgeRate.COL_NAME_MIN_AGE].unique().tolist()
    df_mort.set_index([YearAgeRate.COL_NAME_MIN_AGE], inplace=True)

    df_list = []
    for age in age_list:
        tmp_data = df_mort.loc[age, :]
        extrap_model = make_pipeline(StandardScaler(with_mean=False), LinearRegression())

        # -------------------------------------------------------------------------------------------------
        # --- Get the data (log(rate)) for the reference interval and from the beginning of the reference
        # --- interval all the way to the end of the prediction.
        # -------------------------------------------------------------------------------------------------
        min_year_col = tmp_data[YearAgeRate.COL_NAME_MIN_YEAR]
        first_extrap_df = tmp_data[min_year_col.between(interval_fit[0], interval_fit[1])]
        xx              = tmp_data[min_year_col.between(interval_fit[0], predict_horizon)].values[:, 1] # noqa: E221

        # ----------------------------------------------------------------------------------------
        # --- Have the model fit the reference interval and then use that to predict the interval
        # --- from the beginning of the reference interval to the end.
        # ----------------------------------------------------------------------------------------
        values = first_extrap_df.values
        extrap_model.fit(values[:, 1].reshape(-1, 1), values[:, 2])
        extrap_predictions = extrap_model.predict(xx.reshape(-1, 1))

        # ----------------------------------------------------
        # --- Create a new dataframe with the new predictions
        # ----------------------------------------------------
        extrap_dict = {
            YearAgeRate.COL_NAME_MIN_AGE: age,
            YearAgeRate.COL_NAME_MIN_YEAR: xx,
            'Extrap': extrap_predictions
        }
        loc_df = pd.DataFrame.from_dict(extrap_dict)
        loc_df.set_index([YearAgeRate.COL_NAME_MIN_AGE, YearAgeRate.COL_NAME_MIN_YEAR], inplace=True)

        df_list.append(loc_df.copy())

    # ---------------------------------------------------------------
    # --- Concatenate the dataframes from the different ages together
    # ---------------------------------------------------------------
    df_e1 = pd.concat(df_list, axis=0)

    # -----------------------------------------------------------
    # --- Merge this datafame with the predictions with original
    # -----------------------------------------------------------
    df_list_final = [df_mort, df_e1]
    df_total = reduce(lambda left, right: pd.merge(left, right, on=[YearAgeRate.COL_NAME_MIN_AGE, YearAgeRate.COL_NAME_MIN_YEAR]), df_list_final)
    df_total = df_total.reset_index(inplace=False).set_index([YearAgeRate.COL_NAME_MIN_AGE], inplace=False)

    # ----------------------------------------------
    # --- Convert the data to rates from log(rates)
    # ----------------------------------------------
    df_total['Extrap'] = df_total['Extrap'].apply(np.exp)
    df_total['Data'] = df_total[YearAgeRate.COL_NAME_RATE].apply(np.exp)

    # ------------------------------------------------------------------
    # --- Convert the before time data to rates from log(rates) and
    # --- combine the data into one dataframe for the entire time period
    # ------------------------------------------------------------------
    df_before_time['Data'] = df_before_time[YearAgeRate.COL_NAME_RATE].apply(np.exp)
    df_before_time.set_index([YearAgeRate.COL_NAME_MIN_AGE], inplace=True)
    df_total = pd.concat([df_total, df_before_time], axis=0, join='outer', sort=True)
    df_total.reset_index(inplace=True)
    df_total.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE], inplace=True)

    # ----------------
    # --- Replace NaNs
    # ----------------
    def min_not_nan(x_list):
        loc_in = list(filter(lambda x: not np.isnan(x), x_list))
        return np.min(loc_in)
    df_total[YearAgeRate.COL_NAME_RATE] = df_total[['Data', 'Extrap']].apply(min_not_nan, axis=1)

    # ------------------------------------------------------
    # --- Convert dataframe to one suitable for YearAgeRate
    # ------------------------------------------------------
    df_total.drop(columns=['Data', 'Extrap'], inplace=True)
    df_total = df_total[YearAgeRate.COL_NAMES]
    df_total.sort_values(by=YearAgeRate.SORT_BY_COLUMNS, inplace=True)

    return YearAgeRate(df=df_total)


def mortality_read_infer_plot(country: str,
                              version: str,
                              gender: str,
                              interval_fit: tuple[float, float] = None,
                              save_data: bool = False, 
                              other_csv_filename: str = None,
                              img_dir: str = None,
                              filename_to_save_to: str = None) -> None:
    """
    Extract the mortality data from the given file for the given country and plot
    both the raw data and the inferred data (without HIV deaths).  The plot window will
    have a plot for each age where the data in the plot shows the rate per year for
    that age group.  The label shows the minimum age of the band.  This means that the
    age range being represented is from this value to the next largest age that is plotted.

    Args:
        un_world_pop_filename: The path to a UN World Population spreadsheet containing
            mortality data.  It can be for either female or male.

        country: The name of the country to be extracted.  It must match exactly to the
            country name used in the referenced spreadsheet.

        version: The year/version of the indicated spreadsheet.  Each year has a slightly
            different format.  Supported versions are 2012, 2015, 2019, 2024

        gender:
            The gender of the data to be extracted.  Possible values are 'male' and 'female'.

        save_data: If true (default is False), two YearAgeRate CSV formatted files are
            output into the current directory.  The files are: 'raw_mortality_year_age_rate.csv'
            and 'mortality_minus_hiv_year_age_rate.csv'.

        other_csv_filename: If the filename is defined, it reads an expected YearAgeRate CSV
            file and plots it with the raw and inferred data from the spreadsheet.
            This allows the user to plot other mortality data (i.e. older versions)
            with the new data.

        img_dir: If this is defined, the images are saved to this directory.  If not defined,
            the images are displayed in a window.

        filename_to_save_to: The name of the file to save the image to.  This is only used if
            img_dir is defined.

    Return:
        No return
    """
    raw_mortality_yar = unwp.extract_mortality(country=country,
                                               version=version,
                                               gender=gender)
    mortality_minus_hiv_yar = infer_natural_mortality(year_age_rate_data=raw_mortality_yar,
                                                      interval_fit=interval_fit,
                                                      predict_horizon=2100)

    if save_data:
        raw_mortality_yar.to_csv("raw_mortality_year_age_rate.csv")
        mortality_minus_hiv_yar.to_csv("mortality_minus_hiv_year_age_rate.csv")

    plot_list = []
    plot_list.append(raw_mortality_yar)
    plot_list.append(mortality_minus_hiv_yar)

    if other_csv_filename:
        other_yar = YearAgeRate(csv_filename=other_csv_filename)
        plot_list.append(other_yar)

    title = f"Red: UN World Population, country={country}, version={version}, gender={gender}\n"
    title += f"Blue: Natural mortality inferred from {interval_fit[0]} to {interval_fit[1]}"
    year_age_rate.plot(year_age_rate_list=plot_list,
                       title=title,
                       node_id=0,
                       img_dir=img_dir,
                       filename_to_save_to=filename_to_save_to)


def mortality_read_infer_plot_app(country: str,
                                  version: str, 
                                  gender: str,
                                  min_year: int,
                                  max_year: int,
                                  save_data: bool = False, 
                                  other_csv_filename: str = None,
                                  img_dir: str = None) -> None:
    """
    Using the 'version' and 'gender', select the UN World Population mortality data file.
    Extract the mortality data from the selected file for the given country and plot
    both the raw data and the inferred data (without HIV deaths).  The plot will
    have a plot for each age where the data in the plot shows the rate per year for
    that age group.  The label shows the minimum age of the band.  This means that the
    age range being represented is from this value to the next largest age that is plotted.

    Args:
        country: The name of the country to be extracted.  It must match exactly to the
            country name used in the referenced spreadsheet.

        version: The year/version of the indicated spreadsheet.  Each year has a slightly
            different format.  Supported versions are 2012, 2015, 2019, 2024

        gender: The gender of the data to be extracted.  Possible values are 'male' and 'female'.

        min_year: The start year of the interval to fit the data to.

        max_year: The end year of the interval to fit the data to.

        save_data: If true (default is False), two YearAgeRate CSV formatted files are
            output into the current directory.  The files are: 'raw_mortality_year_age_rate.csv'
            and 'mortality_minus_hiv_year_age_rate.csv'.

        other_csv_filename: If the filename is defined, it reads an expected YearAgeRate CSV
            file and plots it with the raw and inferred data from the spreadsheet.
            This allows the user to plot other mortality data (i.e. older versions)
            with the new data.

        img_dir: If this is defined, the images are saved to this directory.  If not defined,
            the images are displayed in a window.

    Return:
        No return
    """
    if min_year >= max_year:
        raise ValueError(f"Invalid interval: {min_year} >= {max_year}.\n" +
                         "The min year must be less than the max year.")
    if min_year < 1950:
        raise ValueError(f"Invalid interval: {min_year} < 1950.\n" +
                         "The min year must be greater than or equal to 1950,\n" +
                         "because the data is not present in the files.")
    if max_year > 2100:
        raise ValueError(f"Invalid interval: {max_year} > 2100.\n" +
                         "The max year must be less than or equal to 2100,\n" +
                         "because the data is not present in the files.")

    filename_to_save_to = f"Inferred_Mortality_{gender}_{country}_{version}_from_{min_year}_to_{max_year}.png"
    filename_to_save_to = filename_to_save_to.replace(" ", "_")

    mortality_read_infer_plot(country=country, 
                              version=version,
                              gender=gender,
                              interval_fit=(min_year, max_year),
                              save_data=save_data,
                              other_csv_filename=other_csv_filename,
                              img_dir=img_dir,
                              filename_to_save_to=filename_to_save_to)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('-g', '--gender',   type=str, default='male',   help="Gender of mortality data. Options: 'male' or 'female'")
    parser.add_argument('-y', '--year',     type=str, default="2015",   help="Year of UN World Population data.  Options: 2012, 2015, 2019, 2024")
    parser.add_argument('-c', '--country',  type=str, default="Zambia", help="Country name in UN World Population data.")
    parser.add_argument('-m', '--min_year', type=int, default=1950,     help="The start year of the interval to fit the data to.")
    parser.add_argument('-x', '--max_year', type=int, default=1975,     help="The end year of the interval to fit the data to.")
    parser.add_argument('-o', '--output',   type=str, default=None,     help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')

    args = parser.parse_args()

    mortality_read_infer_plot_app(country=args.country, 
                                  version=args.year,
                                  gender=args.gender,
                                  min_year=args.min_year,
                                  max_year=args.max_year,
                                  save_data=False,
                                  other_csv_filename=None,
                                  img_dir=args.output)
