import os
import pandas as pd
from typing import Union

import emodpy_hiv.demographics.un_world_pop as unwp

import emodpy_hiv.plotting.xy_plot as xy_plot
import emodpy_hiv.plotting.helpers as helpers


TEST_include_dir_or_filename = True

COL_NAME_YEAR           = "Year"                         # noqa: E221
COL_NAME_NODE_ID        = " NodeId"                      # noqa: E221
COL_NAME_GENDER         = " Gender"                      # noqa: E221
COL_NAME_HAS_HIV        = " HasHIV"                      # noqa: E221
COL_NAME_RISK           = " IP_Key:Risk"                 # noqa: E221
COL_NAME_ACCESS         = " IP_Key:Accessibility"        # noqa: E221
COL_NAME_STATE          = " IP_Key:CascadeState"         # noqa: E221
COL_NAME_IS_CIRC        = " IsCircumcised"               # noqa: E221
COL_NAME_AGE            = " Age"                         # noqa: E221
COL_NAME_POP            = " Population"                  # noqa: E221
COL_NAME_INFECTED       = " Infected"                    # noqa: E221
COL_NAME_NEW_INF        = " Newly Infected"              # noqa: E221
COL_NAME_ON_ART         = " On_ART"                      # noqa: E221
COL_NAME_DIED           = " Died"                        # noqa: E221
COL_NAME_DIED_HIV       = " Died_from_HIV"               # noqa: E221
COL_NAME_TESTED_OR_ART  = " Tested Past Year or On_ART"  # noqa: E221
COL_NAME_TESTED_EVER    = " Tested Ever"                 # noqa: E221
COL_NAME_DIAGNOSED      = " Diagnosed"                   # noqa: E221
COL_NAME_NEW_TESTED_POS = " Newly Tested Positive"
COL_NAME_NEW_TESTED_NEG = " Newly Tested Negative"


def create_title(base_title: str = "",
                 node_id: int = None,
                 gender: str = None,
                 show_avg_per_run: bool = False,
                 show_fraction: bool = False,
                 show_fraction_of: bool = False,
                 fraction_of_str: str = "",
                 hiv_negative: bool = False,
                 has_age_bins: bool = False):
    """
    Use the input arguments to create a title for the plot (and filename).

    Args:
        base_title (str, optional):
            This is the core string to place in the title.  It describes the specific data being plotted.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        show_avg_per_run (bool, optional):
            True indicates that the data is an average over multiple runs.

        show_fraction (bool, optional):
            True indicates that the data is not true counts but a fraction
            (i.e. a count divided by another counter)

        show_fraction_of (bool, optional):
            When the denominator of the fraction can be different things,
            say population or infected, this allows you to specify the option
            that is not population.

        fraction_of_str (str, optional):
            If 'show_fraction_of' is true, then this argument an be used to include
            in the plot what the denominator is.

        hiv_negative (bool, optional):
            If True, then the title will indicate that the data is for people without HIV.

        has_age_bins (bool, optional):
            If True, then 'by Age' is added to the title.

    Returns:
        A string to be used a the top line title of the plot.
    """
    title = ""
    if show_avg_per_run and not show_fraction:
        title = "Average Per Run "
    elif not show_avg_per_run and show_fraction:
        title = title + "Fraction of "
    elif show_avg_per_run and show_fraction:
        title = "Average Fraction of "
    if show_fraction:
        if show_fraction_of:
            title = title + fraction_of_str
    if gender == "Female":
        title = title + "Females"
    elif gender == "Male":
        title = title + "Males"
    else:
        title = title + "People"

    if hiv_negative:
        title = title + " Without HIV"

    if base_title:
        title = title + " " + base_title

    if has_age_bins:
        title = title + " by Age"

    if node_id is not None:
        title = title + " - Node " + str(node_id)

    if not show_avg_per_run:
        title = title + " Per Run"

    return title


def create_y_axis_name(base_title: str = "",
                       node_id: int = None,
                       gender: str = None,
                       show_avg_per_run: bool = False,
                       show_fraction: bool = False,
                       show_fraction_of: bool = False,
                       fraction_of_str: str = "",
                       has_age_bins: bool = False):
    """
    Given the arguments, create a label for the y-axis that describes the data being plotted.

    Args:
        base_title (str, optional):
            This is the core string to place in the y-label.  It describes what is being plotted.

        node_id (int, optional):
            TBD

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        show_avg_per_run (bool, optional):
            TBD

        show_fraction (bool, optional):
            True indicates that the data is not true counts but a fraction
            (i.e. a count divided by another counter)

        show_fraction_of (bool, optional):
            When the denominator of the fraction can be different things,
            say population or infected, this allows you to specify the option
            that is not population.

        fraction_of_str (str, optional):
            If 'show_fraction_of' is true, then this argument an be used to include
            in the plot what the denominator is.

        has_age_bins (bool, optional):
            TBD

    Returns:
        A string to be used a the top line title of the plot.
    """
    y_axis_name = "Number of "
    if show_fraction:
        y_axis_name = "Fraction of "
        if show_fraction_of:
            y_axis_name = y_axis_name + fraction_of_str
    if gender == "Female":
        y_axis_name = y_axis_name + "Females"
    elif gender == "Male":
        y_axis_name = y_axis_name + "Males"
    else:
        y_axis_name = y_axis_name + "People"
    y_axis_name = y_axis_name + base_title

    return y_axis_name


def extract_population_data(filename: str,
                            node_id: int = None,
                            gender: str = None,
                            age_bin: float = None,
                            other_strat_column_name: str = None,
                            other_strat_value: Union[int, float, str] = None):
    """
    Extract population data for a specific node, gender and age.

    It is assumed that the file has ages every 5 years from 0 to 100.
    """
    df = pd.read_csv(filename)

    # -------------------------------------------
    # Verify the CSV file has the correct columns
    # -------------------------------------------
    if COL_NAME_POP not in df.columns:
        raise ValueError(f"'{COL_NAME_POP}' column does not exist in the file({filename}).")
    if other_strat_column_name and (other_strat_column_name not in df.columns):
        raise ValueError(f"'{other_strat_column_name}' column does not exist in the file({filename}).")

    if( ((other_strat_column_name is not None) and (other_strat_value is     None)) or # noqa: E201, E271, E275, W504
        ((other_strat_column_name is     None) and (other_strat_value is not None)) ): # noqa: E202, E271, E129
        raise ValueError("Both 'other_strat_column_name' and 'other_strat_value' must be specified.")

    # ---------------------------------------------------------------
    # Determine which columns to put in the pivot table and create it
    # ---------------------------------------------------------------
    pv_columns = []
    if node_id is not None:
        pv_columns.append(COL_NAME_ON_ART)
    if gender is not None:
        pv_columns.append(COL_NAME_GENDER)
    if other_strat_column_name is not None:
        pv_columns.append(other_strat_column_name)
    if age_bin is not None:
        pv_columns.append(COL_NAME_AGE)

    gender_id = 1
    if gender == "Male":
        gender_id = 0

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=pv_columns,
                        values=COL_NAME_POP,
                        aggfunc="sum")

    # ------------------------------------------------------------
    # Extract data from pivot table and put in dataframe.
    # If the input age_bin is 80, we need to include the data from
    # the older ages because 80 for UN World Pop is really 80+.
    # ------------------------------------------------------------
    df2 = pd.DataFrame()
    df2.index = pv.index.values
    df2[COL_NAME_POP] = 0

    list_for_tuple = []
    if node_id is not None:
        list_for_tuple.append(node_id)
    if gender is not None:
        list_for_tuple.append(gender_id)
    if other_strat_column_name is not None:
        list_for_tuple.append(other_strat_value)
    if age_bin is not None:
        age_bin_list = [age_bin]
        if age_bin == 80:
            age_bin_list = [80, 85, 90, 95, 100]
        for age in age_bin_list:
            list_for_tuple_with_age = list_for_tuple.copy()
            list_for_tuple_with_age.append(age)
            if len(list_for_tuple_with_age) == 1:
                column_tuple = list_for_tuple_with_age[0]
            else:
                column_tuple = tuple(list_for_tuple_with_age)
            df2[COL_NAME_POP] = df2[COL_NAME_POP] + pv[column_tuple]
    else:
        if len(list_for_tuple) == 1:
            column_tuple = list_for_tuple[0]
        else:
            column_tuple = tuple(list_for_tuple)
        df2[COL_NAME_POP] = pv[column_tuple]

    return df2


def extract_population_data_multiple_ages(filename: str,
                                          node_id: int = None,
                                          gender: str = None,
                                          age_bin_list: list[float] = None,
                                          filter_by_hiv_negative: bool = False,
                                          other_strat_column_name: str = None,
                                          other_strat_value: Union[int, float, str] = None,
                                          other_data_column_names: list[str] = None):
    """
    Extract population data for multiple ages for a specific node and gender.
    """
    df = pd.read_csv(filename)

    # -----------------------------------------
    # Verify the report had the correct columns
    # -----------------------------------------
    if COL_NAME_POP not in df.columns:
        raise ValueError(f"'Population' column does not exist in the file({filename}).")
    if other_strat_column_name is not None and other_strat_column_name not in df.columns:
        raise ValueError(f"'{other_strat_column_name}' column does not exist in the file({filename}).")

    if( ((other_strat_column_name is not None) and (other_strat_value is     None)) or # noqa: E201, E271, E275, W504
        ((other_strat_column_name is     None) and (other_strat_value is not None)) ): # noqa: E202, E271, E129
        raise ValueError("Both 'other_strat_column_name' and 'other_strat_value' must be specified.")

    if other_data_column_names is None:
        other_data_column_names = []

    # -----------------------------------------------------
    # Determine what data to put in to the pivot table and
    # create pivot table
    # -----------------------------------------------------
    pv_columns = []
    age_data_list = []
    if node_id is not None:
        pv_columns.append(COL_NAME_NODE_ID)
    if gender is not None:
        pv_columns.append(COL_NAME_GENDER)
    if other_strat_column_name is not None:
        pv_columns.append(other_strat_column_name)
    if age_bin_list is not None:
        pv_columns.append(COL_NAME_AGE)
        age_data_list = df[COL_NAME_AGE].unique()

    data_is_for_hiv_negative = False
    if filter_by_hiv_negative:
        if COL_NAME_HAS_HIV in df.columns:
            df = df[df[COL_NAME_HAS_HIV] == 0]
            data_is_for_hiv_negative = True

    data_columns = COL_NAME_POP
    if len(other_data_column_names) > 0:
        data_columns = []
        data_columns.append(COL_NAME_POP)
        for col_name in other_data_column_names:
            if col_name is not None and col_name not in df.columns:
                raise ValueError(f"'{col_name}' column does not exist in the file({filename}).")
            data_columns.append(col_name)

    gender_id = 1
    if gender == "Male":
        gender_id = 0

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=pv_columns,
                        values=data_columns,
                        aggfunc="sum")

    # -------------------------------------------------------
    # Move the data from the pivot table to a new dataframe.
    # If doing ages, we need to create labels for the columns
    # that includes the age ranges.
    # -------------------------------------------------------
    df2 = pd.DataFrame()
    df2.index = pv.index.values

    new_column_names = []
    new_column_names.append(COL_NAME_POP)
    for col_name in other_data_column_names:
        new_column_names.append(col_name)

    list_for_tuple = []
    if node_id is not None:
        list_for_tuple.append(node_id)
    if gender is not None:
        list_for_tuple.append(gender_id)
    if other_strat_column_name is not None:
        list_for_tuple.append(other_strat_value)
    if age_bin_list:
        for age_index in range(len(age_bin_list) - 1):
            age_min = age_bin_list[age_index]
            age_max = age_bin_list[age_index + 1]
            age_label = ":" + str(age_min) + " - " + str(age_max)
            for col_name in new_column_names:
                df2[col_name + age_label] = 0
            for age in age_data_list:
                if (age_min <= age) and (age < age_max):
                    for col_name in new_column_names:
                        list_for_tuple_with_age = []
                        if len(other_data_column_names) > 0:
                            list_for_tuple_with_age.append(col_name)
                        list_for_tuple_with_age.extend(list_for_tuple)
                        list_for_tuple_with_age.append(float(age))
                        if len(list_for_tuple_with_age) == 1:
                            column_tuple = list_for_tuple_with_age[0]
                        else:
                            column_tuple = tuple(list_for_tuple_with_age)
                        df2[col_name + age_label] = df2[col_name + age_label] + pv[column_tuple]
    else:
        for col_name in new_column_names:
            column_tuple = col_name
            if len(list_for_tuple) > 0:
                list_for_tuple_copy = []
                if len(other_data_column_names) > 0:
                    list_for_tuple_copy.append(col_name)
                list_for_tuple_copy.extend(list_for_tuple)
                if len(list_for_tuple_copy) == 1:
                    column_tuple = list_for_tuple_copy[0]
                else:
                    column_tuple = tuple(list_for_tuple_copy)
            df2[col_name] = pv[column_tuple]

    return df2, data_is_for_hiv_negative


def extract_population_data_by_stratification(filename: str,
                                              node_id: int = None,
                                              gender: str = None,
                                              age_bin_list: list[float] = None,
                                              start_column_name: str = None,
                                              strat_values: list[str] = None):
    """
    Extract population data such that you get the population for each stratification.
    """
    if age_bin_list is not None and len(age_bin_list) < 2:
        raise ValueError("'age_bin_list' must have at least two values.\n"
                         + "The second value is the max of the i-th bin and the min of the (i+1)-th bin.")

    df = pd.read_csv(filename)

    # --------------------------------------------
    # Verify the CSV file has the expected columns
    # --------------------------------------------
    if COL_NAME_POP not in df.columns:
        raise ValueError(f"'Population' column does not exist in the file({filename}).")
    if start_column_name not in df.columns:
        raise ValueError(f"'{start_column_name}' column does not exist in the file({filename}).")

    if strat_values is None:
        strat_values = df[start_column_name].unique()
        strat_values = [x for x in strat_values if str(x) != 'nan']

    # -----------------------------------------------------
    # Determine what data to put in to the pivot table and
    # create pivot table
    # -----------------------------------------------------
    pv_columns = []
    age_data_list = []
    pv_columns.append(start_column_name)
    if node_id is not None:
        pv_columns.append(COL_NAME_NODE_ID)
    if gender is not None:
        pv_columns.append(COL_NAME_GENDER)
    if age_bin_list is not None:
        pv_columns.append(COL_NAME_AGE)
        age_data_list = df[COL_NAME_AGE].unique()

    data_columns = COL_NAME_POP

    gender_id = 1
    if gender == "Male":
        gender_id = 0

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=pv_columns,
                        values=data_columns,
                        aggfunc="sum")

    # -------------------------------------------------------
    # Move the data from the pivot table to a new dataframe.
    # If doing ages, we need to create labels for the columns
    # that includes the age ranges.
    # -------------------------------------------------------
    df2 = pd.DataFrame()
    df2.index = pv.index.values

    for strat_value in strat_values:
        list_for_tuple = []
        list_for_tuple.append(strat_value)
        if node_id is not None:
            list_for_tuple.append(node_id)
        if gender is not None:
            list_for_tuple.append(gender_id)
        if age_bin_list:
            for age_index in range(len(age_bin_list) - 1):
                age_min = age_bin_list[age_index]
                age_max = age_bin_list[age_index + 1]
                age_label = ":" + str(age_min) + " - " + str(age_max)
                df2[strat_value + age_label] = 0
                for age in age_data_list:
                    if (age_min <= age) and (age < age_max):
                        list_for_tuple_with_age = list_for_tuple.copy()
                        list_for_tuple_with_age.append(float(age))
                        column_tuple = tuple(list_for_tuple_with_age)
                        df2[strat_value + age_label] = df2[strat_value + age_label] + pv[column_tuple]
        else:
            column_tuple = strat_value
            if len(list_for_tuple) > 0:
                list_for_tuple_copy = list_for_tuple.copy()
                if len(list_for_tuple_copy) == 1:
                    column_tuple = list_for_tuple_copy[0]
                else:
                    column_tuple = tuple(list_for_tuple_copy)
            df2[strat_value] = pv[column_tuple]

    return df2

def extract_population_data_by_stratification_for_dir(dir_or_filename: str,
                                                      node_id: int = None,
                                                      gender: str = None,
                                                      age_bin_list: list[float] = None,
                                                      start_column_name: str = None,
                                                      strat_values: list[str] = None,
                                                      show_avg_per_run: bool = False):
    combined_df = pd.DataFrame()

    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="ReportHIVByAgeAndGender",
                                          file_extension=".csv")

    for fn in dir_filenames:
        print(f"Extracting data from {fn}")
        df = extract_population_data_by_stratification(filename=fn,
                                                       node_id=node_id,
                                                       gender=gender,
                                                       age_bin_list=age_bin_list,
                                                       start_column_name=start_column_name,
                                                       strat_values=strat_values)

        if len(combined_df.columns) == 0:
            combined_df.index = df.index
            for column_name in df.columns:
                name = column_name
                if not show_avg_per_run:
                    name = fn + "-" + name
                combined_df[name] = 0
        for column_name in df.columns:
            if show_avg_per_run:
                combined_df[column_name] = combined_df[column_name] + df[column_name]
            else:
                name = fn + "-" + column_name
                combined_df[name] = df[column_name]

    if show_avg_per_run:
        for column_name in combined_df.columns:
            combined_df[column_name] = combined_df[column_name] / len(dir_filenames)

    col_name_prefixs = [""]
    if not show_avg_per_run:
        col_name_prefixs = []
        for fn in dir_filenames:
            col_name_prefixs.append(fn + "-")

    return combined_df, col_name_prefixs


def create_df_for_plot_by_stratification(combined_df: pd.DataFrame,
                                         col_name_prefixs: list[str],
                                         age_bin_list: list[float] = None,
                                         show_fraction: bool = False):
    if show_fraction:
        total_df = pd.DataFrame()
        total_df.index = combined_df.index

        age_str_list = [""]
        if age_bin_list:
            for age_index in range(len(age_bin_list) - 1):
                age_min = age_bin_list[age_index]
                age_max = age_bin_list[age_index + 1]
                age_str_list.append(":" + str(age_min) + " - " + str(age_max))

        for prefix in col_name_prefixs:
            for age_str in age_str_list:
                total_label = "total-" + prefix + "-" + age_str
                total_df[total_label] = 0
                for column_name in combined_df.columns:
                    if (age_str in column_name) and (prefix in column_name):
                        total_df[total_label] = total_df[total_label] + combined_df[column_name]
                for column_name in combined_df.columns:
                    if (age_str in column_name) and (prefix in column_name):
                        combined_df[column_name] = combined_df[column_name] / total_df[total_label]

    return combined_df


def plot_population_for_dir(dir_or_filename: str,
                            unworld_pop_filename: str,
                            country: str,
                            version: str,
                            x_base_population: float = 1.0,
                            show_avg_per_run: bool = False,
                            gender: str = None,
                            age_bin: float = None,
                            img_dir: str = None):
    """
    Plot the population for the given age bin against the data in the UN World Population spreadsheet.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        unworld_pop_filename (str, required):
            The name and path to a UN World Pop Excel spreadsheet where the 'country' parameter specifies
            a country name found in the spreadsheet and the 'version' specifies the year of the data.
            These values are needed to know how to read the data in the spreadsheet.

        country (str, required):
            The name of the country found in the spreadsheet to extract the data for.

        version (str, required):
            The year associated with when the UN World Pop file was created.
            PLEASE NOTE: This year is a string.

        x_base_population (float, optional):
            The 'x_Base_Population' value (found in the config) is used to divide by the population
            numbers in the CSV file so you get numbers that match the true population.

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin (float, optional):
            If provided, the data for this specific age stratification will be plotted.
            Both the data in the report file and the UN World Pop file must have this
            stratification.  If you do not provide a value, then the population is not
            broken up by age (i.e. total population).

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if x_base_population <= 0.0:
        raise ValueError("'x_base_population' must be a value greater than zero.")

    # Get the file or files in the directory
    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="ReportHIVByAgeAndGender",
                                          file_extension=".csv")

    # ---------------------------------------------------------------
    # Extract the data from each file and combine into one dataframe
    # ---------------------------------------------------------------
    combined_df = pd.DataFrame()
    for fn in dir_filenames:
        df = extract_population_data(fn, gender=gender, age_bin=age_bin)
        if len(combined_df.columns) == 0:
            combined_df.index = df.index
            if show_avg_per_run:
                combined_df[COL_NAME_POP] = 0
        if show_avg_per_run:
            combined_df[COL_NAME_POP] = combined_df[COL_NAME_POP] + df[COL_NAME_POP] / x_base_population
        else:
            combined_df[fn] = df[COL_NAME_POP] / x_base_population

    if show_avg_per_run:
        for column_name in combined_df.columns:
            combined_df[column_name] = combined_df[column_name] / len(dir_filenames)

    # ----------------------------------------------------------------
    # Extract the expected population data from the UN World Pop file
    # and put into dataframe.  Get the data for the years that you have
    # in the CSV file.
    # ----------------------------------------------------------------
    years = combined_df.index.values.astype(int).tolist()
    years = list(set(years))

    date_column = COL_NAME_YEAR
    if version == "2015":
        date_column = "Reference date (as of 1 July)"

    unwp_df2 = None
    title2 = dir_or_filename
    if unworld_pop_filename:
        title2 = str(unworld_pop_filename)
        unwp_df = unwp.extract_population_by_age(country=country, 
                                                 version=version,
                                                 years=years,
                                                 filename=unworld_pop_filename)
        unwp_df.index = unwp_df[date_column].astype(float)
        del unwp_df[date_column]
        rename_dict = {}
        for name in unwp_df.columns:
            rename_dict[name] = int(name)
        unwp_df = unwp_df.rename(columns=rename_dict)

        unwp_df2 = pd.DataFrame()
        unwp_df2.index = unwp_df.index.astype(float)
        if age_bin is not None:
            unwp_df2["Expected Population"] = unwp_df[age_bin]
        else:
            unwp_df2["Expected Population"] = unwp_df.sum(axis=1)

    # --------------------------
    # create title and plot data
    # --------------------------
    title = ""
    if show_avg_per_run:
        title = title + "Average Per Run"
    title = title + "Population"
    if gender is not None:
        title = title + " - " + gender
    if age_bin is not None:
        if age_bin == 80:
            title = title + " - " + str(age_bin) + "+"
        else:
            title = title + " - " + str(age_bin) + "-" + str(age_bin + 5)

    if not TEST_include_dir_or_filename:
        title2 = None

    xy_plot.xy_plot(img_dir=img_dir,
                    df=combined_df,
                    expected_df=unwp_df2,
                    title_1=title,
                    title_2=title2,
                    y_axis_name="Number of People",
                    fraction_of_total=False,
                    show_legend=show_avg_per_run,
                    show_markers=show_avg_per_run,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_population_by_gender(filename: str,
                              img_dir: str = None):
    """
    For the given file, plot the population for each gender over time.

    Args
        filename (str, required):
            The name and path of the ReportHIVByAgeAndGender.csv file to extract the data from.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if not os.path.isfile(filename):
        raise ValueError(f"The filename, '{filename}' given does not appear to be a file.")

    df = pd.read_csv(filename)

    if COL_NAME_GENDER not in df.columns:
        raise ValueError(f"'{COL_NAME_GENDER}' column does not exist in the file({filename}).")

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=[COL_NAME_GENDER],
                        values=COL_NAME_POP,
                        aggfunc="sum")

    df2 = pd.DataFrame()
    df2.index = pv.index
    df2["Number of Men"] = pv[0]
    df2["Number of Women"] = pv[1]

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df2,
                    title_1="Population by Gender",
                    title_2=None,
                    y_axis_name="Number of People",
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_population_by_ip(dir_or_filename: str,
                          exp_dir_or_filename: str = None,
                          node_id: int = None,
                          gender: str = None,
                          age_bin_list=None,
                          ip_key: str = None,
                          ip_values: list[str] = None,
                          show_avg_per_run: bool = False,
                          show_fraction: bool = False,
                          expected_values: dict = None,
                          img_dir: str = None):
    """
    For the indicated files, create a plot showing who has what value of the give IP key over time.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        exp_dir_or_filename (str, required):
            The expected or alternate directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages, in years, where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        ip_key (str, required):
            Extract the data from the files based on this IP stratification column.
            If the files has not been stratified by this IP, you will need to re-run the
            simulations with stratification turned on.

        ip_values (list[str], optional):
            By default, this plotting tool uses all of the values for the IP, however, this allows
            you to only include the ones you are interested (i.e. a subset to the total possible
            values for the IP)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        show_fraction (bool, optional):
            True indicates that the number of people the given IP value will be divided by
            the sum of all the people with all of the selected IP values.  For example, if the
            IP key were Risk and you selected to only plot LOW and MEDIUM, then the total number
            of people with LOW will be divided by the total number of people with either LOW or MEDIUM.

        expected_values (dict, optional):
            If the user provides this dictionary, the constant expected value of each IP will be
            plotted.  This should be a dictionary with an IP value as the key and a constant expected value.
            There should be an IP value for each IP value plotted.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """

    if (exp_dir_or_filename is not None) and (expected_values is not None):
        raise ValueError("You cannot specify both 'exp_dir_or_filename' and 'expected_values'. "
                         + "Please only specify one of these.")
    
    if ip_key is None:
        raise ValueError("IP Key must be specified.")
    ip_col_name = " IP_Key:" + ip_key

    combined_df, col_name_prefixs = extract_population_data_by_stratification_for_dir(
                                        dir_or_filename=dir_or_filename,
                                        node_id=node_id,
                                        gender=gender,
                                        age_bin_list=age_bin_list,
                                        start_column_name=ip_col_name,
                                        strat_values=ip_values,
                                        show_avg_per_run=show_avg_per_run)
    
    combined_df = create_df_for_plot_by_stratification(combined_df=combined_df,
                                                       col_name_prefixs=col_name_prefixs,
                                                       age_bin_list=age_bin_list,
                                                       show_fraction=show_fraction)

    expected_df = None
    if expected_values:
        expected_df = pd.DataFrame()
        expected_df.index = combined_df.index
        for value in ip_values:
            expected_df["Expected: " + value] = expected_values[value]
    elif exp_dir_or_filename is not None:
        expected_df, exp_col_name_prefixs = extract_population_data_by_stratification_for_dir(
                                                dir_or_filename=exp_dir_or_filename,
                                                node_id=node_id,
                                                gender=gender,
                                                age_bin_list=age_bin_list,
                                                start_column_name=ip_col_name,
                                                strat_values=ip_values,
                                                show_avg_per_run=show_avg_per_run)
        expected_df = create_df_for_plot_by_stratification(combined_df=expected_df,
                                                           col_name_prefixs=exp_col_name_prefixs,
                                                           age_bin_list=age_bin_list,
                                                           show_fraction=show_fraction)

    base_title = "with " + ip_key + "=X"
    title = create_title(base_title=base_title,
                         node_id=node_id,
                         gender=gender,
                         show_avg_per_run=show_avg_per_run,
                         show_fraction=show_fraction,
                         show_fraction_of=False,
                         fraction_of_str=None,
                         has_age_bins=(age_bin_list is not None))
    y_axis_name = create_y_axis_name(base_title=" " + base_title,
                                     node_id=node_id,
                                     gender=gender,
                                     show_avg_per_run=show_avg_per_run,
                                     show_fraction=show_fraction,
                                     show_fraction_of=False,
                                     fraction_of_str=None,
                                     has_age_bins=(age_bin_list is not None))

    title2 = None
    if TEST_include_dir_or_filename:
        if exp_dir_or_filename is not None:
            title2 = "color= " + dir_or_filename
            title2 = title2 + "\nblack = " + exp_dir_or_filename
        else:
            title2 = dir_or_filename

    xy_plot.xy_plot(img_dir=img_dir,
                    df=combined_df,
                    expected_df=expected_df,
                    title_1=title,
                    title_2=title2,
                    y_axis_name=y_axis_name,
                    show_legend=show_avg_per_run,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_columns(filename: str,
                 title: str,
                 y_axis_name: str,
                 column_names: list[str],
                 fraction_of_population: bool = False,
                 img_dir: str = None):
    """
    For a given file, plot the indicated columns versus time (i.e. Year).

    Args:
        filename (str, required):
            The name and path of the ReportHIVByAgeAndGender.csv file to extract the data from.

        title (str, required):
            The title to put at the top of the plot.

        y_axis_name (str, required):
            The name to label the y-axis on the plot.

        column_names (list[str], required):
            The list of column names to plot the data for.  The report has a space before each
            column name.  Please be sure to include it.

        fraction_of_population (bool, optional):
            If True, divide the count each column by the population for the same stratification.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if not os.path.isfile(filename):
        raise ValueError(f"The filename, '{filename}' given does not appear to be a file.")

    df = pd.read_csv(filename)

    for name in column_names:
        if name not in df.columns:
            raise ValueError(f"'{name}' column does not exist in the file({filename}).")

    if fraction_of_population:
        column_names.append(COL_NAME_POP)

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=[],
                        values=column_names,
                        aggfunc="sum")

    df2 = pd.DataFrame()
    df2.index = pv.index
    for value in column_names:
        if fraction_of_population and (value != COL_NAME_POP):
            df2[value] = pv[value] / pv[COL_NAME_POP]
        elif not fraction_of_population:
            df2[value] = pv[value]

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df2,
                    title_1=title,
                    title_2=None,
                    y_axis_name=y_axis_name,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_circumcision_by_age(filename: str,
                             age_bin_list: list[float],
                             fraction_of_total: bool = False,
                             img_dir: str = None):
    """
    For a single file, plot the number of men who are circumcised by age.

    Args:
        filename (str, required):
            The name and path of the ReportHIVByAgeAndGender.csv to extract the data from.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        fraction_of_total (bool, optional):
            If True, the number of men who are circumcised will be divided by the total number
            of men with that stratification.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if not os.path.isfile(filename):
        raise ValueError(f"The filename, '{filename}' given does not appear to be a file.")

    df = pd.read_csv(filename)

    if COL_NAME_GENDER not in df.columns:
        raise ValueError(f"'{COL_NAME_GENDER}' column does not exist in the file({filename}).")
    if COL_NAME_AGE not in df.columns:
        raise ValueError(f"'{COL_NAME_AGE}' column does not exist in the file({filename}).")

    ages = df[COL_NAME_AGE].unique()

    y_axis_name = "Number of Circumcised Men"
    if fraction_of_total:
        y_axis_name = "Fraction of Men Circumcised by Age"

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=[COL_NAME_GENDER, COL_NAME_AGE, COL_NAME_IS_CIRC],
                        values=COL_NAME_POP,
                        aggfunc="sum")

    df2 = pd.DataFrame()
    df2.index = pv.index

    gender_id = 0
    is_circumcised = 1
    for index in range(len(age_bin_list) - 1):
        label = f"Men Circumcised: {age_bin_list[index]}-{age_bin_list[index + 1]}"
        pv[label] = 0
        pv["total"] = 0
        for age in ages:
            if (age_bin_list[index] <= age) and (age < age_bin_list[index + 1]):
                pv["total"] = pv["total"] + pv[(gender_id, age, 0)] + pv[(gender_id, age, 1)]
                pv[label] = pv[label] + pv[(gender_id, age, is_circumcised)]
        df2[label] = pv[label]
        if fraction_of_total:
            df2[label] = df2[label] / pv["total"]

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df2,
                    title_1="Circumcised Men by Age",
                    title_2=None,
                    y_axis_name=y_axis_name,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def extract_population_data_multiple_ages_for_dir(dir_or_filename: str,
                                                  node_id: int = None,
                                                  gender: str = None,
                                                  age_bin_list: list[float] = None,
                                                  show_avg_per_run: bool = False,
                                                  filter_by_hiv_negative: bool = False,
                                                  other_strat_column_name: str = None,
                                                  other_strat_value_a: Union[int, float, str] = None,
                                                  other_strat_value_b: Union[int, float, str] = None,
                                                  other_data_column_names: list[str] = None):
    combined_df = pd.DataFrame()

    data_is_for_hiv_negative = False
    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="ReportHIVByAgeAndGender",
                                          file_extension=".csv")
    for fn in dir_filenames:
        print("extracting data from " + fn)
        df_a, hiv_neg_a = extract_population_data_multiple_ages(fn,
                                                                node_id=node_id,
                                                                gender=gender,
                                                                age_bin_list=age_bin_list,
                                                                filter_by_hiv_negative=filter_by_hiv_negative,
                                                                other_strat_column_name=other_strat_column_name,
                                                                other_strat_value=other_strat_value_a,
                                                                other_data_column_names=other_data_column_names)
        df_b = None
        hiv_neg_b = None
        if other_strat_column_name is not None and other_strat_value_b is not None:
            df_b, hiv_neg_b = extract_population_data_multiple_ages(fn,
                                                                    node_id=node_id,
                                                                    gender=gender,
                                                                    age_bin_list=age_bin_list,
                                                                    filter_by_hiv_negative=filter_by_hiv_negative,
                                                                    other_strat_column_name=other_strat_column_name,
                                                                    other_strat_value=other_strat_value_b,
                                                                    other_data_column_names=other_data_column_names)
        
        if hiv_neg_b is not None and hiv_neg_a != hiv_neg_b:
            raise ValueError("The two dataframes for the two stratifications do not have the same HIV negative status. "
                             + "This is likely because you are trying to extract data for a stratification that does not exist in the file.")
        data_is_for_hiv_negative = hiv_neg_a
        
        if len(combined_df.columns) == 0:
            combined_df.index = df_a.index
            for column_name in df_a.columns:
                name = column_name
                if not show_avg_per_run:
                    name = fn + "-" + name
                combined_df[name] = 0
        for column_name in df_a.columns:
            if show_avg_per_run:
                if df_b is not None:
                    combined_df[column_name] = combined_df[column_name] + df_a[column_name] / (df_a[column_name] + df_b[column_name])
                else:
                    combined_df[column_name] = combined_df[column_name] + df_a[column_name]
            else:
                name = fn + "-" + column_name
                if df_b is not None:
                    combined_df[name] = df_a[column_name] / (df_a[column_name] + df_b[column_name])
                else:
                    combined_df[name] = df_a[column_name]

    if show_avg_per_run:
        for column_name in combined_df.columns:
            combined_df[column_name] = combined_df[column_name] / len(dir_filenames)

    col_name_prefixs = [""]
    if not show_avg_per_run:
        col_name_prefixs = []
        for fn in dir_filenames:
            col_name_prefixs.append(fn + "-")

    return combined_df, col_name_prefixs, data_is_for_hiv_negative


def create_df_for_plot_by_age(combined_df: pd.DataFrame,
                              col_name_prefixs: list[str],
                              main_column_name: str,
                              gender: str,
                              age_bins: list[float],
                              show_fraction: bool,
                              fraction_of: bool,
                              fraction_of_column_name: str):
    df2 = pd.DataFrame()
    df2.index = combined_df.index

    if show_fraction:
        for prefix in col_name_prefixs:
            fraction_label = prefix + main_column_name + "/Population"
            if fraction_of:
                fraction_label = prefix + main_column_name + "/" + fraction_of_column_name[1:]
            if age_bins:
                for age_index in range(len(age_bins) - 1):
                    age_min = age_bins[age_index    ]  # noqa: E202
                    age_max = age_bins[age_index + 1]
                    main_label         = prefix + main_column_name        + ":" + str(age_min) + " - " + str(age_max) # noqa: E221
                    pop_label          = prefix + COL_NAME_POP            + ":" + str(age_min) + " - " + str(age_max) # noqa: E221
                    other_label        = prefix + fraction_of_column_name + ":" + str(age_min) + " - " + str(age_max) # noqa: E221
                    fraction_label_age = fraction_label                   + ":" + str(age_min) + " - " + str(age_max) # noqa: E221
                    if fraction_of:
                        df2[fraction_label_age] = combined_df[main_label] / combined_df[other_label]
                    else:
                        df2[fraction_label_age] = combined_df[main_label] / combined_df[pop_label]
                    df2[fraction_label_age] = df2[fraction_label_age].fillna(0)
            else:
                if fraction_of:
                    df2[fraction_label] = combined_df[prefix + main_column_name] / combined_df[prefix + fraction_of_column_name]
                else:
                    df2[fraction_label] = combined_df[prefix + main_column_name] / combined_df[prefix + COL_NAME_POP]
                df2[fraction_label] = df2[fraction_label].fillna(0)
    else:
        new_column_names = {}
        for column_name in combined_df.columns:
            if main_column_name not in column_name:
                del combined_df[column_name]
            else:
                label = column_name
                if gender:
                    label = gender + column_name
                new_column_names[column_name] = label
        combined_df = combined_df.rename(columns=new_column_names)
        df2 = combined_df.copy()

    return df2


def base_plot_by_age(base_title: str,
                     main_column_name: str,
                     dir_or_filename: str,
                     exp_dir_or_filename: str = None,
                     node_id: int = None,
                     age_bins: list[float] = None,
                     gender: str = None,
                     filter_by_hiv_negative: bool = False,
                     other_strat_column_name: str = None,
                     other_strat_value_a: Union[int, float, str] = None,
                     other_strat_value_b: Union[int, float, str] = None,
                     show_avg_per_run: bool = False,
                     show_fraction: bool = False,
                     fraction_of: bool = False,
                     fraction_of_column_name: str = None,
                     fraction_of_str: str = None,
                     img_dir: str = None):

    other_data_column_names = []
    if main_column_name != COL_NAME_POP:
        other_data_column_names.append(main_column_name)
    if show_fraction and fraction_of:
        other_data_column_names.append(fraction_of_column_name)

    combined_df, col_name_prefixs, hiv_neg = extract_population_data_multiple_ages_for_dir(
                                                 dir_or_filename=dir_or_filename,
                                                 node_id=node_id,
                                                 gender=gender,
                                                 age_bin_list=age_bins,
                                                 show_avg_per_run=show_avg_per_run,
                                                 filter_by_hiv_negative=filter_by_hiv_negative,
                                                 other_strat_column_name=other_strat_column_name,
                                                 other_strat_value_a=other_strat_value_a,
                                                 other_strat_value_b=other_strat_value_b,
                                                 other_data_column_names=other_data_column_names)
    
    df2 = create_df_for_plot_by_age(combined_df=combined_df, 
                                    col_name_prefixs=col_name_prefixs,
                                    main_column_name=main_column_name,
                                    gender=gender,
                                    age_bins=age_bins,
                                    show_fraction=show_fraction,
                                    fraction_of=fraction_of,
                                    fraction_of_column_name=fraction_of_column_name)

    exp_df2 = None
    exp_hiv_neg = None
    if exp_dir_or_filename:
        exp_combined_df, exp_col_name_prefixs, exp_hiv_neg = extract_population_data_multiple_ages_for_dir(
                                                                  dir_or_filename=exp_dir_or_filename,
                                                                  node_id=node_id,
                                                                  gender=gender,
                                                                  age_bin_list=age_bins,
                                                                  show_avg_per_run=show_avg_per_run,
                                                                  filter_by_hiv_negative=filter_by_hiv_negative,
                                                                  other_strat_column_name=other_strat_column_name,
                                                                  other_strat_value_a=other_strat_value_a,
                                                                  other_strat_value_b=other_strat_value_b,
                                                                  other_data_column_names=other_data_column_names)
        exp_df2 = create_df_for_plot_by_age(combined_df=exp_combined_df,
                                            col_name_prefixs=exp_col_name_prefixs,
                                            main_column_name=main_column_name,
                                            gender=gender,
                                            age_bins=age_bins,
                                            show_fraction=show_fraction,
                                            fraction_of=fraction_of,
                                            fraction_of_column_name=fraction_of_column_name)

    if exp_hiv_neg is not None and hiv_neg != exp_hiv_neg:
        raise ValueError(f"The two sets of data do not each have the HasHIV column.\n"
                         + "The files in {dir_or_filename} have HasHIV={hiv_neg}.\n"
                         + "The files in {exp_dir_or_filename} have HasHIV={exp_hiv_neg}.\n"
                         + "Please check the files and make sure they are correct.")

    title = create_title(base_title=base_title,
                         node_id=node_id,
                         gender=gender,
                         show_avg_per_run=show_avg_per_run,
                         show_fraction=show_fraction,
                         show_fraction_of=fraction_of,
                         fraction_of_str=fraction_of_str,
                         hiv_negative=hiv_neg,
                         has_age_bins=(age_bins is not None))
    y_axis_name = create_y_axis_name(base_title=" " + base_title,
                                     node_id=node_id,
                                     gender=gender,
                                     show_avg_per_run=show_avg_per_run,
                                     show_fraction=show_fraction,
                                     show_fraction_of=fraction_of,
                                     fraction_of_str=fraction_of_str,
                                     has_age_bins=(age_bins is not None))

    title2 = None
    if TEST_include_dir_or_filename:
        if exp_df2 is not None:
            title2 = "color=" + dir_or_filename
            title2 = title2 + "\nblack=" + exp_dir_or_filename
        else:
            title2 = dir_or_filename

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df2,
                    expected_df=exp_df2,
                    title_1=title,
                    title_2=title2,
                    y_axis_name=y_axis_name,
                    show_legend=show_avg_per_run,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_onART_by_age(dir_or_filename: str,
                      exp_dir_or_filename: str = None,
                      node_id: int = None,
                      gender: str = None,
                      age_bin_list: list[float] = None,
                      show_avg_per_run: bool = False,
                      show_fraction: bool = False,
                      fraction_of_infected: bool = False,
                      img_dir: str = None):
    """
    Create a plot showing information about the people on ART.  You can show the fraction of the
    population or the fraction of the infected population.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        exp_dir_or_filename (str, required):
            The expected or alternate directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        show_fraction (bool, optional):
            True indicates that the number of people on ART will be divided by either the number
            of people in the population or the number of infected people.  It depends on the
            'fraction_of_infected' parameter.

        fraction_of_infected (bool, optional):
            If 'show_fraction' is True, then this parameter determines what the divisor is when
            creating the fraction.  If it is True, it will divide the number of people on ART
            by the number of infected people.  If it is False, the divisor will the total population
            with that stratification.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    base_plot_by_age(base_title="On ART",
                     main_column_name=COL_NAME_ON_ART,
                     dir_or_filename=dir_or_filename,
                     exp_dir_or_filename=exp_dir_or_filename,
                     node_id=node_id,
                     gender=gender,
                     age_bins=age_bin_list,
                     show_avg_per_run=show_avg_per_run,
                     show_fraction=show_fraction,
                     fraction_of=fraction_of_infected,
                     fraction_of_column_name=COL_NAME_INFECTED,
                     fraction_of_str="Infected ",
                     img_dir=img_dir)


def plot_population_by_age(dir_or_filename: str,
                           exp_dir_or_filename: str = None,
                           node_id: int = None,
                           gender: str = None,
                           age_bin_list: list[float] = None,
                           show_avg_per_run: bool = False,
                           img_dir: str = None):
    """
    Create a plot showing the population over time.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        exp_dir_or_filename (str, required):
            The expected or alternate directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if age_bin_list is not None and len(age_bin_list) == 0:
        raise ValueError("The 'age_bin_list' parameter must be a list of ages in years where the population will be counted for each bin. "
                         + "If you do not want to use age bins, please set it to None.")
    
    base_plot_by_age(base_title="",
                     main_column_name=COL_NAME_POP,
                     dir_or_filename=dir_or_filename,
                     exp_dir_or_filename=exp_dir_or_filename,
                     node_id=node_id,
                     gender=gender,
                     age_bins=age_bin_list,
                     show_avg_per_run=show_avg_per_run,
                     show_fraction=False,
                     fraction_of=False,
                     fraction_of_column_name=None,
                     fraction_of_str=None,
                     img_dir=img_dir)


def plot_vmmc_by_age(dir_or_filename: str,
                     exp_dir_or_filename: str = None,
                     node_id: int = None,
                     age_bin_list: list[float] = None,
                     show_avg_per_run: bool = False,
                     img_dir: str = None):
    """
    Create a plot showing information about the men who are circumcised.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        exp_dir_or_filename (str, required):
            The expected or alternate directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    base_plot_by_age(base_title="VMMC",
                     main_column_name=COL_NAME_POP,
                     dir_or_filename=dir_or_filename,
                     exp_dir_or_filename=exp_dir_or_filename,
                     node_id=node_id,
                     gender="Male",
                     age_bins=age_bin_list,
                     show_avg_per_run=show_avg_per_run,
                     show_fraction=False,
                     fraction_of=False,
                     fraction_of_column_name="",
                     fraction_of_str=None,
                     filter_by_hiv_negative=True,
                     other_strat_column_name=COL_NAME_IS_CIRC,
                     other_strat_value_a=1,  # Only show circumcised
                     other_strat_value_b=0,  # Not circumcised
                     img_dir=img_dir)
    

def plot_population_by_age_vs_unworld_pop(filename: str,
                                          unworld_pop_filename: str,
                                          age_bin_list: list[float],
                                          country: str,
                                          version: str,
                                          x_base_population: float = 1.0,
                                          img_dir=None):
    """
    For a single file, plot the actual population for a given age bin versus what was expected
    in the given UN World Population file.  If you have define three age bins, there will be
    six curves -  an actual and an expected for each bin.

    Args:
        filename (str, required):
            The name and path of the ReportHIVByAgeAndGender.csv file to plot the data from.

        unworld_pop_filename (str, required):
            The name and path to a UN World Pop Excel spreadsheet where the 'country' parameter specifies
            a country name found in the spreadsheet and the 'version' specifies the year of the data.
            These values are needed to know how to read the data in the spreadsheet.

        age_bin_list (list[float], required):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        country (str, required):
            The name of the country found in the spreadsheet to extract the data for.

        version (str, required):
            The year associated with when the UN World Pop file was created.
            PLEASE NOTE: This year is a string.

        x_base_population (float, optional):
            The 'x_Base_Population' value (found in the config) is used to divide by the population
            numbers in the CSV file so you get numbers that match the true population.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if not os.path.isfile(filename):
        raise ValueError(f"The filename, '{filename}' given does not appear to be a file.")

    df = pd.read_csv(filename)

    if COL_NAME_GENDER not in df.columns:
        raise ValueError(f"'{COL_NAME_GENDER}' column does not exist in the file({filename}).")
    if COL_NAME_AGE not in df.columns:
        raise ValueError(f"'{COL_NAME_AGE}' column does not exist in the file({filename}).")
    if COL_NAME_POP not in df.columns:
        raise ValueError(f"'{COL_NAME_POP}' column does not exist in the file({filename}).")

    ages = df[COL_NAME_AGE].unique()

    pv = df.pivot_table(index=COL_NAME_YEAR,
                        columns=[COL_NAME_AGE],
                        values=COL_NAME_POP,
                        aggfunc="sum")

    df2 = pd.DataFrame()
    df2.index = pv.index

    for index in range(len(age_bin_list) - 1):
        label = f"Population: {age_bin_list[index]}-{age_bin_list[index + 1]}"
        pv[label] = 0
        for age in ages:
            if (age_bin_list[index] <= age) and (age < age_bin_list[index + 1]):
                pv[label] = pv[label] + pv[(age)]
        df2[label] = pv[label] / x_base_population

    years = df2.index.values.astype(int).tolist()
    years = list(set(years))

    unwp_df = unwp.extract_population_by_age(country=country,
                                             version=version,
                                             years=years,
                                             filename=unworld_pop_filename)
    unwp_df.index = unwp_df[COL_NAME_YEAR]

    unwp_df2 = pd.DataFrame()
    unwp_df2.index = unwp_df.index

    for index in range(len(age_bin_list) - 1):
        name_old = str(age_bin_list[index])
        name_new = f"Expected Population: {age_bin_list[index]}-{age_bin_list[index+1]}"
        unwp_df2[name_new] = unwp_df[name_old]

    unwp_df2.index = unwp_df2.index.astype(float)

    xy_plot.xy_plot(img_dir=img_dir,
                    df=df2,
                    expected_df=unwp_df2,
                    title_1="Population by Age",
                    title_2=f"UN World Population - {country} - {version}",
                    y_axis_name="Number of People",
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_risk(dir_or_filename: str,
              starting_expected_values: dict = None,
              expected_value_for_high_per_node: list[float] = None,
              gender: str = None,
              age_bin_list: list[float] = None,
              show_avg_per_run: bool = False,
              show_fraction: bool = False,
              img_dir: str = None):
    """
    Create one plot for each node in 'expected_value_for_high_per_node' showing the risk
    values for the population versus what is expected.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        starting_expected_values (dict, optional):
            The starting three values of how risk distributed to the population.  These
            should be the same values that you have in the demographics.  The order is
            LOW, MEDIUM, and HIGH.  Typically, one might have 0.85 for LOW, 0.15 for MEDIUM,
            and 0.0 for HIGH because people get set to HIGH in the campaign's CSW logic.

        expected_value_for_high_per_node (list[float, optional]):
            A list of expected fraction of the population to have Risk = HIGH for a given node.
            The node ID of each value is expected to be the index of the position plus 1.
            The starting values for LOW and MEDIUM are adjusted for this HIGH value.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        show_fraction (bool, optional):
            True indicates that for each stratification the number of people with a given
            risk value is divided by the total number of people in that stratification.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """

    if ((starting_expected_values is not None) and (expected_value_for_high_per_node is     None) or    # noqa: E271, W504
        (starting_expected_values is     None) and (expected_value_for_high_per_node is not None)):     # noqa: E225, E271, E129
        raise ValueError("'starting_expected_values' and 'expected_value_for_high_per_node'" +          # noqa: W504
                         " need to be either both None or both defined.")

    if (starting_expected_values is not None) and (starting_expected_values["HIGH"] != 0.0):
        raise ValueError("Expected 'starting_expected_values['HIGH'] to be zero.")

    if (starting_expected_values is not None) and (expected_value_for_high_per_node is not None):
        node_id = 0
        for high_value in expected_value_for_high_per_node:
            node_id = node_id + 1

            expected_values = None
            if (starting_expected_values is not None) and (expected_value_for_high_per_node is not None):
                expected_values = {}
                expected_values["LOW"   ] = starting_expected_values["LOW"   ] * (1.0 - high_value) # noqa: E202
                expected_values["MEDIUM"] = starting_expected_values["MEDIUM"] * (1.0 - high_value)
                expected_values["HIGH"  ] = high_value # noqa: E202

            plot_population_by_ip(dir_or_filename=dir_or_filename,
                                  node_id=node_id,
                                  gender=gender,
                                  age_bin_list=age_bin_list,
                                  ip_key="Risk",
                                  ip_values=["LOW", "MEDIUM", "HIGH"],
                                  show_avg_per_run=show_avg_per_run,
                                  show_fraction=show_fraction,
                                  expected_values=expected_values,
                                  img_dir=img_dir)
    else:
        plot_population_by_ip(dir_or_filename=dir_or_filename,
                              node_id=None,
                              gender=gender,
                              age_bin_list=age_bin_list,
                              ip_key="Risk",
                              ip_values=["LOW", "MEDIUM", "HIGH"],
                              show_avg_per_run=show_avg_per_run,
                              show_fraction=show_fraction,
                              expected_values=None,
                              img_dir=img_dir)


def plot_vmmc_for_dir(dir_or_filename: str,
                      node_id: int = None,
                      age_bin_list: list[float] = None,
                      show_expected: bool = False,
                      show_avg_per_run: bool = False,
                      img_dir: str = None):
    """
    Create a plot showing what fraction of men are circumcised over time versus the
    expected number of circumcised men.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_expected (bool, optional):
            If true, plot the expected fraction of circumcisions.

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if node_id is None and show_expected:
        raise ValueError("You need to specify 'node_id' if you want to compare actual data against the expected values.")

    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="ReportHIVByAgeAndGender",
                                          file_extension=".csv")

    combined_df = pd.DataFrame()
    for fn in dir_filenames:
        df_circ, not_used = extract_population_data_multiple_ages(fn,
                                                                  node_id=node_id,
                                                                  gender="Male",
                                                                  age_bin_list=age_bin_list,
                                                                  other_strat_column_name=COL_NAME_IS_CIRC,
                                                                  other_strat_value=1)
        df_un_circ, not_used = extract_population_data_multiple_ages(fn,
                                                                     node_id=node_id,
                                                                     gender="Male",
                                                                     age_bin_list=age_bin_list,
                                                                     other_strat_column_name=COL_NAME_IS_CIRC,
                                                                     other_strat_value=0)
        if len(combined_df.columns) == 0:
            combined_df.index = df_circ.index
            for column_name in df_circ.columns:
                name = column_name
                if not show_avg_per_run:
                    name = fn + "-" + name
                combined_df[name] = 0
        for column_name in df_circ.columns:
            if show_avg_per_run:
                combined_df[column_name] = combined_df[column_name] + df_circ[column_name] / (df_circ[column_name] + df_un_circ[column_name])
            else:
                name = fn + "-" + column_name
                combined_df[name] = df_circ[column_name] / (df_circ[column_name] + df_un_circ[column_name])

    if show_avg_per_run:
        for column_name in combined_df.columns:
            combined_df[column_name] = combined_df[column_name] / len(dir_filenames)

    traditional_coverage_per_node = [0.054978651, 0.139462861, 0.028676043, 0.091349358, 0.123187070,
                                     0.039308099, 0.727917322, 0.041105263, 0.044388102, 0.398239794]
    rtec_x1 = 2016
    rtec_x2 = 2021
    rtec_y1 = 0.54
    rtec_y2 = 0.9

    expected_df = None
    if show_expected:
        expected_df = pd.DataFrame()
        expected_df.index = combined_df.index
        expected_df["Expected Traditional"] = traditional_coverage_per_node[node_id - 1]
        years = combined_df.index.values.astype(float).tolist()
        rtec = []
        for year in years:
            if year < rtec_x1:
                rtec.append(0)
            elif year > rtec_x2:
                rtec.append(rtec_y2)
            else:
                rtec.append(rtec_y1 + (year - rtec_x1) * (rtec_y2 - rtec_y1) / (rtec_x2 - rtec_x1))
        expected_df["Expected Plus Medical"] = rtec

    title = "Circumcised Men"
    if show_avg_per_run:
        title = title + " - Average"
    if node_id is not None:
        title = title + " - Node " + str(node_id)

    title2 = None
    if TEST_include_dir_or_filename:
        title2 = dir_or_filename

    xy_plot.xy_plot(img_dir=img_dir,
                    df=combined_df,
                    expected_df=expected_df,
                    title_1=title,
                    title_2=title2,
                    y_axis_name="Fraction of Circumcised Men",
                    fraction_of_total=False,
                    show_legend=show_avg_per_run,
                    show_markers=show_avg_per_run,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_prevalence_for_dir(dir_or_filename: str,
                            exp_dir_or_filename: str = None,
                            node_id: int = None,
                            gender: str = None,
                            age_bin_list: list[float] = None,
                            show_avg_per_run: bool = False,
                            show_fraction: bool = False,
                            img_dir: str = None):
    """
    Create a plot showing who is infected with HIV.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        exp_dir_or_filename (str, required):
            The expected or alternate directory or filename containing the ReportHIVByAgeAndGender.csv files.

        node_id (int, optional):
            The ID of the node for which the data is being filtered for.

        gender (str, optional):
            The string (Male or Female) for the gender that data is being filtered for.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        show_fraction (bool, optional):
            True indicates that the number of infected people should be divided by the total
            number of people in that stratification.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    base_plot_by_age(base_title="Infected",
                     main_column_name=COL_NAME_INFECTED,
                     dir_or_filename=dir_or_filename,
                     exp_dir_or_filename=exp_dir_or_filename,
                     node_id=node_id,
                     age_bins=age_bin_list,
                     gender=gender,
                     show_avg_per_run=show_avg_per_run,
                     show_fraction=show_fraction,
                     fraction_of=False,
                     fraction_of_column_name="",
                     fraction_of_str="",
                     img_dir=img_dir)


def plot_risk_zambia(dir_or_filename: str,
                     age_bin_list: list[float] = None,
                     show_avg_per_run: bool = False,
                     show_fraction: bool = False,
                     show_expected: bool = False,
                     img_dir: str = None):
    """
    Create multiple risk value plots where each plot is for a specific node and gender.
    The plot can show the count or fraction of the group that has one of the three
    risk values.  The plot can also show the expected values for specific node and gender
    for Zambia.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the ReportHIVByAgeAndGender.csv files.

        age_bin_list (list[float], optional):
            A list of ages in years where the population with risk value will be counted
            for each bin.  For example, if you enter [10, 25, 30, 55], there will be three
            age bins with the following ranges: [10-25), [25-30), [30-55)

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            people with the given risk type at a given time step between the files.
            Default is False.

        show_fraction (bool, optional):
            True indicates that the data is not true counts but a fraction
            (i.e. a count divided by another counter)

        show_expected (bool, optional):
            True indicates that you want to see the expected fractions of the population that
            have the different risk values PER NODE.  False will be data for all nodes.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    starting_expected_values = {
        "LOW": 0.85,
        "MEDIUM": 0.15,
        "HIGH": 0.0
    }
    node_to_high = []
    gender_list = ["Female", "Male"]
    for gender in gender_list:
        if gender == "Female":
            # node_to_high = [0.125, 0.125, 0.125, 0.0500, 0.0500, 0.0500, 0.125, 0.0500, 0.125, 0.0500]
            node_to_high = [0.125, 0.125, 0.125, 0.0500]
        else:
            # node_to_high = [0.195, 0.195, 0.195, 0.0781, 0.0781, 0.0781, 0.195, 0.0781, 0.195, 0.0781]
            node_to_high = [0.195, 0.195, 0.195, 0.0781]

        if not show_expected:
            starting_expected_values = None
            node_to_high = None
        plot_risk(dir_or_filename=dir_or_filename,
                  starting_expected_values=starting_expected_values,
                  expected_value_for_high_per_node=node_to_high,
                  gender=gender,
                  age_bin_list=age_bin_list,
                  show_avg_per_run=show_avg_per_run,
                  show_fraction=show_fraction,
                  img_dir=img_dir)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('dir_or_filename', type=str, nargs=1, help='A directory with ReportHivByAgeAndGender.csv files or a single file.')
    parser.add_argument('exp_dir_or_filename', type=str, default=None, nargs='?', help='A directory with ReportHivByAgeAndGender.csv files or a single file to compare to.')
    parser.add_argument('-p', '--plot', default='population', help='Options: population, prevalence, risk, vmmc, art, state, column, summary')
    parser.add_argument('-o', '--output', default=None, help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')
    parser.add_argument('-n', '--node_id', type=int, default=None, help='Plot the data for a specific node.')
    parser.add_argument('-m', '--mean', help='Gives the average/mean of each run at that time point.', action='store_true')
    parser.add_argument('-a', '--ages', help='Show the data stratified by age.', action='store_true')
    parser.add_argument('-x', '--expected', help='Show the expected data.', action='store_true')
    parser.add_argument('-c', '--column_name', default='Died', help='Only used with plot=column.  The name of a non-stratification column from the report.  Do not include the space before the name.')

    args = parser.parse_args()

    dir_or_filename = args.dir_or_filename[0]
    exp_dir_or_filename = None
    if args.exp_dir_or_filename is not None:
        exp_dir_or_filename = args.exp_dir_or_filename

    node_id = args.node_id

    plot_list = []
    if args.plot == "summary":
        plot_list = ["population", "prevalence", "vmmc", "art", "state"]
    else:
        plot_list = [args.plot]

    for plot in plot_list:
        if plot == "population":
            if args.expected:
                print("===============================================")
                print("Prevalence plot does not support expected data.")
                print("===============================================")

            age_bin_list = None
            if args.ages:
                age_bin_list = [0, 15, 25, 35, 45, 55, 100]

            plot_population_by_age(dir_or_filename=dir_or_filename,
                                   exp_dir_or_filename=exp_dir_or_filename,
                                   node_id=node_id,
                                   gender=None,
                                   age_bin_list=age_bin_list,
                                   show_avg_per_run=args.mean,
                                   img_dir=args.output)

        elif plot == "prevalence":
            if args.expected:
                print("===============================================")
                print("Prevalence plot does not support expected data.")
                print("===============================================")

            age_bin_list = None
            if args.ages:
                age_bin_list = [15, 25, 35, 45, 55]

            plot_prevalence_for_dir(dir_or_filename=dir_or_filename,
                                    exp_dir_or_filename=exp_dir_or_filename,
                                    node_id=args.node_id,
                                    gender=None,
                                    age_bin_list=age_bin_list,
                                    show_avg_per_run=args.mean,
                                    show_fraction=False,
                                    img_dir=args.output)

        elif plot == "risk":
            if args.node_id is not None:
                print("===============================================")
                print("Population plot does not support node_id.")
                print("===============================================")

            age_bin_list = None
            if args.ages:
                age_bin_list = [15, 35, 55]

            plot_population_by_ip(dir_or_filename=dir_or_filename,
                                  exp_dir_or_filename=exp_dir_or_filename,
                                  node_id=args.node_id,
                                  ip_key="Risk",
                                  age_bin_list=age_bin_list,
                                  show_avg_per_run=args.mean,
                                  show_fraction=False,
                                  img_dir=args.output)
            # plot_risk_zambia(dir_or_filename=dir_or_filename,
            #                  age_bin_list=age_bin_list,
            #                  show_avg_per_run=args.mean,
            #                  show_fraction=True,
            #                  show_expected=args.expected,
            #                  img_dir=args.output)

        elif plot == "vmmc":
            age_bin_list = None
            if args.ages:
                age_bin_list = [15, 20, 25, 30, 35, 40, 45, 50, 55]

            plot_vmmc_by_age(dir_or_filename=dir_or_filename,
                             exp_dir_or_filename=exp_dir_or_filename,
                             node_id=args.node_id,
                             age_bin_list=age_bin_list,
                             show_avg_per_run=args.mean,
                             img_dir=args.output)
            # plot_vmmc_for_dir(dir_or_filename=dir_or_filename,
            #                   node_id=args.node_id,
            #                   age_bin_list=age_bin_list,
            #                   show_expected=args.expected,
            #                   show_avg_per_run=args.mean,
            #                   img_dir=args.output)

        elif plot == "art":
            if args.expected:
                print("========================================")
                print("ART plot does not support expected data.")
                print("========================================")

            age_bin_list = None
            if args.ages:
                age_bin_list = [0, 15, 50, 75, 100]

            plot_onART_by_age(dir_or_filename=dir_or_filename,
                              exp_dir_or_filename=exp_dir_or_filename,
                              node_id=args.node_id,
                              gender=None,
                              age_bin_list=age_bin_list,
                              show_avg_per_run=args.mean,
                              show_fraction=True,
                              fraction_of_infected=True,
                              img_dir=args.output)

        elif plot == "state":
            if args.expected:
                print("==========================================")
                print("State plot does not support expected data.")
                print("==========================================")

            age_bin_list = None
            if args.ages:
                age_bin_list = [15, 30, 45]

            plot_population_by_ip(dir_or_filename=dir_or_filename,
                                  exp_dir_or_filename=exp_dir_or_filename,
                                  node_id=args.node_id,
                                  ip_key="CascadeState",
                                  age_bin_list=age_bin_list,
                                  show_avg_per_run=args.mean,
                                  show_fraction=False,
                                  img_dir=args.output)

        elif plot == "column":
            plot_columns(filename=dir_or_filename,
                         title=args.column_name,
                         y_axis_name="Count",
                         column_names=[" " + args.column_name],
                         img_dir=args.output)

        else:
            raise ValueError(f"Plot type '{args.plot}' is not supported.")
