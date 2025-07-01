import os
import pandas as pd
from sklearn.linear_model import LinearRegression

import emodpy_hiv.plotting.xy_plot as xy_plot
import emodpy_hiv.plotting.helpers as helpers

COL_NAME_REL_ID             = "Rel_ID"           # noqa: E221
COL_NAME_START_TIME         = "Rel_start_time"   # noqa: E221
COL_NAME_SCHEDULED_END_TIME = "Rel_scheduled_end_time"
COL_NAME_REL_TYPE           = "Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)"  # noqa: E221
# "Is_rel_outside_PFA"
# "Original_node_ID"
# "Current_node_ID"
# "A_ID"
# "A_is_infected"
# "A_gender"
# "A_age"
COL_NAME_RISK_A             = "A_IP='Risk'"      # noqa: E221
# "A_previous_num_coital_acts"
# "A_total_num_active_rels"
# "A_num_active_TRANSITORY_rels"
# "A_num_active_INFORMAL_rels"
# "A_num_active_MARITAL_rels"
# "A_num_active_COMMERCIAL_rels"
# "A_num_lifetime_rels"
# "A_num_rels_last_6_mo"
# "A_extra_relational_bitmask"
# "A_is_circumcised"
# "A_has_STI_coinfection"
# "A_is_superspreader"
# "B_ID"
# "B_is_infected"
# "B_gender"
# "B_age"
COL_NAME_RISK_B             = "B_IP='Risk'"      # noqa: E221
# "B_previous_num_coital_acts"
# "B_total_num_active_rels"
# "B_num_active_TRANSITORY_rels"
# "B_num_active_INFORMAL_rels"
# "B_num_active_MARITAL_rels"
# "B_num_active_COMMERCIAL_rels"
# "B_num_lifetime_rels"
# "B_num_rels_last_6_mo"
# "B_extra_relational_bitmask"
# "B_is_circumcised"
# "B_has_STI_coinfection"
# "B_is_superspreader"
# "A_CD4_count"
# "B_CD4_count"
# "A_viral_load"
# "B_viral_load"
# "A_HIV_disease_stage"
# "B_HIV_disease_stage"
# "A_HIV_Tested_Positive"
# "B_HIV_Tested_Positive"
# "A_HIV_Received_Results"
# "B_HIV_Received_Results"


def extract_assortivity_risk(start_rel_filename: str,
                             relationship_type: int,
                             male_risk_value="LOW"):
    """
    For the given relationship type, extract the number of relationships that started
    during each time step for each risk value pair.  The male risk value is constant
    so it should return a dataframe with three columns.

    Args:
        start_rel_filename (str, required):
            The name and path of the RelationshipStart.csv file to be read.

        relationship_type (int, required):
            The type of relationship. Options: 0 (transitory), 1 (informal), 2 (marital), 3 (commercial).

        male_risk_value (str, optional):
            The risk value of the male in the relationship being plotted.  This will be
            either LOW, MEDIUM, or HIGH.  Capitalization matters.
            Default is LOW.

    Returns:
        Dataframe with three columns where each column is for a risk value pairing.
        Each row should represent a simulation time (in days) that had relationhips
        created of that time and risk value pairing.  There is no guarantee that
        relationships are created each time step.
    """
    df = pd.read_csv(start_rel_filename)

    if COL_NAME_REL_TYPE not in df.columns:
        raise ValueError(f"'{COL_NAME_REL_TYPE}' column does not exist in the file({start_rel_filename}).")

    if relationship_type not in df[COL_NAME_REL_TYPE].unique():
        raise ValueError(f"'{relationship_type}' does not appear as a relationship type in the file({start_rel_filename}).")

    df = df[ df[COL_NAME_REL_TYPE] == relationship_type ] # noqa: E201, E202

    results_df = pd.DataFrame()
    results_df.index = df[COL_NAME_START_TIME].unique()
    results_df[COL_NAME_START_TIME] = df[COL_NAME_START_TIME].unique()
    risk_values = ["LOW", "MEDIUM", "HIGH"]
    for rv_a in [male_risk_value]:
        df_risk = df[ df[COL_NAME_RISK_A] == rv_a ] # noqa: E201, E202
        for rv_b in risk_values:
            df_risk2 = df_risk[ df_risk[COL_NAME_RISK_B] == rv_b ] # noqa: E201, E202, E226
            tmp_df = pd.DataFrame()
            tmp_df[COL_NAME_START_TIME] = df_risk2[COL_NAME_START_TIME]
            tmp_df[COL_NAME_RISK_B] = df_risk2[COL_NAME_RISK_B]
            tmp_df = tmp_df.groupby(COL_NAME_START_TIME).count()
            if len(tmp_df[COL_NAME_RISK_B]) == 0:
                tmp_df = pd.DataFrame()
                tmp_df.index = df_risk[COL_NAME_START_TIME].unique()
                tmp_df[COL_NAME_START_TIME] = df_risk[COL_NAME_START_TIME].unique()
                tmp_df[COL_NAME_RISK_B] = 0
            results_df[rv_a + "-" + rv_b] = tmp_df[COL_NAME_RISK_B]
            results_df = results_df.fillna(0)

    del results_df[COL_NAME_START_TIME]
    results_df = results_df.fillna(0)

    return results_df


def plot_relationship_assortivity_risk(dir_or_filename: str,
                                       relationship_type: int,
                                       male_risk_value: str = "LOW",
                                       show_avg_per_run: bool = False,
                                       show_regression: bool = False,
                                       regression_dir: str = None,
                                       img_dir: str = None):
    """
    Create a plot showing the number of relationships of a given type
    that started during the timestep for a male with the give risk value
    versus females with the other possible values.  For example, if the
    male's risk value is HIGH, the plot will contain three curves:
    HIGH-LOW, HIGH-MEDIUM, and HIGH-HIGH.  They will all be for the
    given relationship type.  We only do three curves because the data
    can be quite noisy.

    The plot also has the option to show a least squares regression line
    for each risk value pair.  A CSV file can be saved with the regression
    data.  This can be used to compare with the plot_a_vs_b() function to
    compare the regression from two different sets of files.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the RelationshipStart.csv files.

        relationship_type (str, optional):
            The type of relationship. Options: 0 (transitory), 1 (informal), 2 (marital), 3 (commercial).

        male_risk_value (str, optional):
            The risk value of the male in the relationship being plotted.  This will be
            either LOW, MEDIUM, or HIGH.  Capitalization matters.
            Default is LOW.

        show_avg_per_run (bool, optional):
            If 'dir_or_filename' is a directory, this will calculate the average number of
            relationships started at each timestep for the different files in the directory.
            Default is False.

        show_regression (bool, optional):
            If true, a least squares regression line will be calculated and shown on the plot.
            There will be one line for each risk value pair.
            Default is False.

        regression_dir (str, optional):
            If 'show_regression' is true and this provides a path to a directory, then a CSV
            file will be saved with the data points of the displayed regression lines.  The
            name of the file will be the relationship type and the male's risk value.  For
            example, COMMERCIAL-HIGH.csv.
            Default is None.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """
    if not show_regression and regression_dir:
        raise ValueError("Regression directory is set but show_regression is False.\nYou need to show regression if you want to save it.")

    # -------------------------------------------------------------------
    # Get the list of RelationshipStart.csv files in the given directory.
    # -------------------------------------------------------------------
    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="RelationshipStart",
                                          file_extension=".csv")

    # ----------------------------------------------------------------------------------
    # For the given relationship type, extract the number of relationships that started
    # at each time step for each risk value pair where the male risk value is constant.
    # This should result in three columns with counts of new relationships.
    # ----------------------------------------------------------------------------------
    combined_df = pd.DataFrame()
    for fn in dir_filenames:
        df = extract_assortivity_risk(start_rel_filename=fn,
                                      relationship_type=relationship_type,
                                      male_risk_value=male_risk_value)
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
        combined_df = combined_df.fillna(0)

    if show_avg_per_run:
        for column_name in combined_df.columns:
            combined_df[column_name] = combined_df[column_name] / len(dir_filenames)

    # ---------------------------------------------------------------------------------
    # For a given time step, convert the counts of new relationships to a fraction.
    # If we are show all the files, then we need to calculate the fractions for each
    # file.  If doing the average, then it will be the fractions based on the averages.
    # ---------------------------------------------------------------------------------
    col_name_prefixs = [""]
    if not show_avg_per_run:
        col_name_prefixs = []
        for fn in dir_filenames:
            col_name_prefixs.append(fn + "-")

    total_df = pd.DataFrame()
    total_df.index = combined_df.index

    for prefix in col_name_prefixs:
        total_label = "total-" + prefix
        total_df[total_label] = 0
        for column_name in combined_df.columns:
            if prefix in column_name:
                total_df[total_label] = total_df[total_label] + combined_df[column_name]
        for column_name in combined_df.columns:
            if prefix in column_name:
                combined_df[column_name] = combined_df[column_name] / total_df[total_label]
            combined_df[column_name] = combined_df[column_name].fillna(0)

    # ---------------------------------------------------------------------------------
    # If requested, determine a least squares regression line for each risk value pair.
    # ---------------------------------------------------------------------------------
    expected_df = None
    if show_regression:
        expected_df = pd.DataFrame()
        expected_df.index = combined_df.index
        x = combined_df.index.values
        x = x.reshape(len(x), 1)
        for col_name in combined_df.columns:
            y = combined_df[col_name].values      # Dependent variable
            y = y.reshape(len(y), 1)
            model = LinearRegression()
            model.fit(x, y)
            expected_df["Regression-" + col_name] = model.predict(x)

    # convert relationship type to a string
    rel_str = "TRANSITORY"
    if relationship_type == 1:
        rel_str = "INFORMAL"
    elif relationship_type == 2:
        rel_str = "MARITAL"
    elif relationship_type == 3:
        rel_str = "COMMERCIAL"

    # save the regression data to a file
    if regression_dir and show_regression:
        if not os.path.exists(regression_dir):
            os.makedirs(regression_dir)
        expected_df["Time"] = expected_df.index
        expected_df.to_csv(regression_dir + "/" + rel_str + "-" + male_risk_value + ".csv", index=False)
        del expected_df["Time"]

    # ------------------------------
    # Create the titles for the plot
    # ------------------------------
    title2 = ""
    for col in combined_df.columns:
        title2 = title2 + col + "=" + f'{combined_df[col].mean():0.3f}' + " "

    title = ""
    if show_avg_per_run:
        title = "Average Per Run - "
    title = title + f"Relationship Per Risk Assortivity - {rel_str} - Male Risk = {male_risk_value}"

    # -------------
    # plot the data
    # -------------
    xy_plot.xy_plot(img_dir=img_dir,
                    df=combined_df,
                    expected_df=expected_df,
                    title_1=title,
                    title_2=title2,
                    x_axis_name="Days",
                    y_axis_name="Fraction of Relationships",
                    show_legend=show_avg_per_run,
                    show_markers=show_avg_per_run,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_relationship_assortivity_risk_all(dir_or_filename: str,
                                           regression_dir: str = None,
                                           img_dir: str = None):
    """
    Create a plot for each combination male risk value and relationship type.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the RelationshipStart.csv files or a specific file.

        regression_dir (str, optional):
            If provided, a CSV file will be created for each plot where the CSV file has one column
            for each risk value combination - three columns because the male's value is fixed.

        img_dir (str, optional):
            Directory to save the images.  If None, the images will not be saved and a window will be opened.
            Default is none - don't save image and open a window.

    Returns:
        None - but images will be saved or windows opened.
    """
    male_risk_values = ["LOW", "MEDIUM", "HIGH"]
    for rel_type in [0, 1, 2, 3]:
        for risk_value in male_risk_values:
            plot_relationship_assortivity_risk(dir_or_filename=dir_or_filename,
                                               relationship_type=rel_type,
                                               male_risk_value=risk_value,
                                               show_avg_per_run=True,
                                               show_regression=True,
                                               regression_dir=regression_dir,
                                               img_dir=img_dir)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('dir_or_filename', type=str, nargs=1, help='A directory with RelationshipStart.csv files or a single file.')
    parser.add_argument('-o', '--output', default=None, help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')
    parser.add_argument('-t', '--type_of_relationship', default='marital', help='Options: transitory, informal, marital, commercial')
    parser.add_argument('-r', '--risk_value_of_male', default='LOW', help='Options: LOW, MEDIUM, HIGH')
    # parser.add_argument('-n', '--node_id', type=int, default=None, help='Plot the data for a specific node.')
    parser.add_argument('-m', '--mean', help='Gives the average/mean of each run at that time point.', action='store_true')
    parser.add_argument('-e', '--estimated', help='Show the estimated regression line.', action='store_true')

    args = parser.parse_args()

    dir_or_filename = args.dir_or_filename[0]

    possible_risk_values = ["LOW", "MEDIUM", "HIGH"]
    if args.risk_value_of_male not in possible_risk_values:
        raise ValueError("Unknown risk value for male = " + args.risk_value_of_male)

    possible_relationship_types = ["transitory", "informal", "marital", "commercial"]
    if args.type_of_relationship not in possible_relationship_types:
        raise ValueError("Unknown relationship type = " + args.type_of_relationship)

    rel_type = 0
    if args.type_of_relationship == "transitory":
        rel_type = 0
    elif args.type_of_relationship == "informal":
        rel_type = 1
    elif args.type_of_relationship == "marital":
        rel_type = 2
    else:
        rel_type = 3

    plot_relationship_assortivity_risk(dir_or_filename=dir_or_filename,
                                       relationship_type=rel_type,
                                       male_risk_value=args.risk_value_of_male,
                                       show_avg_per_run=args.mean,
                                       show_regression=args.estimated,
                                       regression_dir=None,
                                       img_dir=args.output)
