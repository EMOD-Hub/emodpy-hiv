import pandas as pd

import emodpy_hiv.plotting.xy_plot as xy_plot
import emodpy_hiv.plotting.helpers as helpers

COL_NAME_REL_ID       = "Rel_ID"                 # noqa: E221
COL_NAME_NODE_ID      = "Node_ID"                # noqa: E221
COL_NAME_START_TIME   = "Rel_start_time"         # noqa: E221
COL_NAME_END_TIME_EXP = "Rel_scheduled_end_time"
COL_NAME_END_TYPE_ACT = "Rel_actual_end_time"
COL_NAME_REL_TYPE     = "Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)" # noqa: E221
COL_NAME_OUTSIDE_PFA  = "Is_rel_outside_PFA"     # noqa: E221
COL_NAME_MALE_ID      = "male_ID"                # noqa: E221
COL_NAME_FEMALE_ID    = "female_ID"              # noqa: E221
COL_NAME_MALE_AGE     = "male_age"               # noqa: E221
COL_NAME_FEMALE_AGE   = "female_age"             # noqa: E221
COL_NAME_NUM_ACTS     = "num_total_coital_acts"  # noqa: E221
COL_NAME_TERMINATION  = "Termination_Reason"     # noqa: E221

TMP_COL_NAME_DURATION = "Rel_duration"
TMP_COL_NAME_AVG_DUR  = "Average Duration"       # noqa: E221

TR_NA                 = "NA"                     # noqa: E221
TR_BROKEUP            = "BROKEUP"                # noqa: E221
TR_SELF_MIGRATING     = "SELF_MIGRATING"         # noqa: E221
TR_PARTNER_DIED       = "PARTNER_DIED"           # noqa: E221
TR_PARTNER_TERMINATED = "PARTNER_TERMINATED"     # noqa: E221
TR_PARTNER_MIGRATING  = "PARTNER_MIGRATING"      # noqa: E221


def extract_data_for_relationship(filename: str,
                                  relationship_type: int):
    """
    Extract the relationship duration information for the given relationship type in the given file.
    Please note that only relationships that "broke-up" are considered because those are the relationships
    that went to the completion of the drawn duration.  The relationship could have ended prematurely due
    to things like death or a partner migrating away.

    Args:
        filename (str, required):
            The path and name of the RelationshipEnd.csv to be read.

        relationship_type (int, required):
            The type of relationship. Options: 0 (transitory), 1 (informal), 2 (marital), 3 (commercial).

    Returns:
        Dataframe where the rows must be of the given relationship type and with the extra column
        of the actual relationship duration.
    """
    df = pd.read_csv(filename)

    if COL_NAME_REL_TYPE not in df.columns:
        raise ValueError(f"'{COL_NAME_REL_TYPE}' column does not exist in the file({filename}).")

    if relationship_type not in df[COL_NAME_REL_TYPE].unique():
        raise ValueError(f"'{relationship_type}' is not a valid relationship type in the file({filename}).")

    df = df[ df[COL_NAME_REL_TYPE   ] == relationship_type ]  # noqa: E201, E202
    df = df[ df[COL_NAME_TERMINATION] == TR_BROKEUP        ]  # noqa: E201, E202

    df[TMP_COL_NAME_DURATION] = df[COL_NAME_END_TYPE_ACT] - df[COL_NAME_START_TIME]

    return df


def plot_relationship_duration_histogram(dir_or_filename: str,
                                         relationship_type: int,
                                         bin_size: float,
                                         expected: list[float] = None,
                                         exp_avg: float = None,
                                         heterogeneity: float = None,
                                         scale: float = None,
                                         show_avg_per_run: bool = False,
                                         img_dir: str = None):
    """
    Plot the relationship duration histogram for the given relationship type and
    show information in the title about the expected Weibull distribution.
    Please note that only relationships that "broke-up" are considered because those are the relationships
    that went to the completion of the drawn duration.  The relationship could have ended prematurely due
    to things like death or a partner migrating away.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the RelationshipEnd.csv files.

        relationship_type (int, required):
            The type of relationship. Options: 0 (transitory), 1 (informal), 2 (marital), 3 (commercial).

        bin_size (float, required):
            The size of the bins for the histogram.

        expected (list, optional):
            Expected values for the Weibull distribution.  There must be 16 values.

        exp_avg (float, optional):
            Expected average duration in days.  Will be shown in the title.

        heterogeneity (float, optional):
            Heterogeneity parameter for the Weibull distribution.  Will be show in the title.

        scale (float, optional):
            Scale parameter for the Weibull distribution.  Will be show in the title.

        show_avg_per_run (bool, optional):
            Whether to show the average duration per run.  Will be show in the title.

        img_dir (str, optional):
            Directory to save the images. If None, the images will not be saved and a window will be opened.

    Returns:
        None - but image will be saved or window opened.
    """

    # -------------------------------------------------------
    # Create the array of bins given the bin size
    # The bins are bin_size, 2*bin_size, ..., 16*bin_size,
    # They are the maximum value of the bin.
    # I selected 16 bins because it seemed like you saw the distribution well.
    # -------------------------------------------------------
    num_bins = 16
    bins = []
    this_bin = bin_size
    for bin_index in range(num_bins):
        bins.append(this_bin)
        this_bin = this_bin + bin_size

    if (expected is not None) and (len(expected) != 16):
        raise ValueError("The 'expected' Weibull distribution histogram is expected to have 16 values.")

    # ------------------------------
    # Create the labels for the bins
    # ------------------------------
    bin_label_list = []
    for bin_index, this_bin in enumerate(bins):
        if bin_index == 0:
            label = f"0-{this_bin}"
        else:
            label = f"{bins[bin_index-1]}-{this_bin}"
        bin_label_list.append(label)

    # -----------------------------------------
    # Get the list of files in the directory
    # If a single file is given, use that file
    # -----------------------------------------
    dir_filenames = helpers.get_filenames(dir_or_filename=dir_or_filename,
                                          file_prefix="RelationshipEnd",
                                          file_extension=".csv")

    # --------------------------------------------------------------------------------------
    # Extract the duration data out of each file and determine the histogram
    # of relationship duration.  The histogram is the fraction of relationships in each bin.
    # --------------------------------------------------------------------------------------
    total = 0
    total_count = 0
    histogram_list = []
    for fn in dir_filenames:
        df = extract_data_for_relationship(filename=fn,
                                           relationship_type=relationship_type)
        count_sum = 0
        count_histogram = []
        for this_bin in bins:
            count_histogram.append(0)

        for item in df[TMP_COL_NAME_DURATION]:
            total = total + item
            for bin_index, this_bin in enumerate(bins):
                if (item < this_bin) or (this_bin == bins[len(bins) - 1]):
                    count_histogram[bin_index] = count_histogram[bin_index] + 1
                    count_sum = count_sum + 1
                    break
        histogram = []
        for count in count_histogram:
            histogram.append(count / count_sum)
        histogram_list.append(histogram)
        total_count = total_count + count_sum

    # Calculate average for all relationships in all files
    act_avg = total / total_count

    # ------------------------------------------------------------------------------------
    # Create the dataframe to plot and make the index the bin labels and put the histogram
    # into the data frame.  If not showing the average, then there should be one column for
    # each file.  If showing the average, we want one column with the average of each bin.
    # ------------------------------------------------------------------------------------
    df_hist = pd.DataFrame()
    df_hist["Label"] = bin_label_list
    df_hist.index = df_hist["Label"]
    del df_hist["Label"]

    for hist_index, histogram in enumerate(histogram_list):
        df_hist["Duration-" + str(hist_index)] = histogram

    if show_avg_per_run:
        column_names = df_hist.columns
        df_hist[TMP_COL_NAME_AVG_DUR] = 0
        for column_name in column_names:
            df_hist[TMP_COL_NAME_AVG_DUR] = df_hist[TMP_COL_NAME_AVG_DUR] + df_hist[column_name]
            del df_hist[column_name]
        df_hist[TMP_COL_NAME_AVG_DUR] = df_hist[TMP_COL_NAME_AVG_DUR] / len(dir_filenames)

    # -------------------------------------------------------------------------
    # Create the expected dataframe - Show Weibull distribution that the model
    # should have duplicated.
    # -------------------------------------------------------------------------
    expected_df = None
    if expected:
        expected_df = pd.DataFrame()
        expected_df.index = df_hist.index
        expected_df["Expected Duration"] = expected

    # ------------------------------
    # Create the title for the plot
    # ------------------------------
    rel_str = "TRANSITORY"
    if relationship_type == 1:
        rel_str = "INFORMAL"
    elif relationship_type == 2:
        rel_str = "MARITAL"
    elif relationship_type == 3:
        rel_str = "COMMERCIAL"

    title = ""
    if show_avg_per_run:
        title = title + "Average Duration per Run - "
    title = title + f"Relationship Duration Histogram - {rel_str}"

    title2 = f"Weibull Distribution - Scale={scale:0.2f} - Hetero={heterogeneity:0.2f} - Exp Avg={exp_avg:0.2f} - Act Avg={act_avg:0.2f}"

    # ---------------
    # Create the plot
    # ---------------
    xy_plot.xy_plot(img_dir=img_dir,
                    df=df_hist,
                    expected_df=expected_df,
                    title_1=title,
                    title_2=title2,
                    x_axis_name="Duration (days)",
                    y_axis_name="Fraction of Relationships",
                    show_legend=show_avg_per_run,
                    show_markers=show_avg_per_run,
                    fraction_of_total=False,
                    min_x=None, max_x=None, min_y=None, max_y=None,
                    x_axis_as_log_scale=False,
                    y_axis_as_log_scale=False)


def plot_relationship_duration_histogram_with_expected(dir_or_filename: str,
                                                       relationship_type: str = "transitory",
                                                       show_avg_per_run: bool = False,
                                                       show_expected: bool = False,
                                                       img_dir: str = None):
    """
    Plot the relationship duration histogram for the given relationship type.
    Please note that only relationships that "broke-up" are considered because those are the relationships
    that went to the completion of the drawn duration.  The relationship could have ended prematurely due
    to things like death or a partner migrating away.

    Args:
        dir_or_filename (str, required):
            The directory or filename containing the RelationshipEnd.csv files.

        relationship_type (str, optional):
            The type of relationship. Options: transitory, informal, marital, commercial.
            Default is "transitory".

        show_avg_per_run (bool, optional):
            Whether to show the average duration per run.
            Default is False.

        show_expected (bool, optional):
            Whether to show the expected Weibull distribution.
            Default is False.

        img_dir (str, optional):
            Directory to save the images.  If None, the images will not be saved and a window will be opened.
            Default is none - don't save image and open a window.

    Returns:
        None - but image will be saved or window opened.
    """
    bin_size = None
    expected = None
    hetero   = None  # noqa: E221
    scale    = None  # noqa: E221
    exp_avg  = None  # noqa: E221
    rel_type = None

    # ------------------------------------------------------------------------------------------------
    # Expected array are the values of the Weibull distribution with the given scale and heterogeneity
    # One can generate these expected values using the C++ code in PrngTest.cpp
    # ------------------------------------------------------------------------------------------------
    if relationship_type == "transitory":
        rel_type = 0
        bin_size = 200
        expected = [0.401084, 0.291050, 0.160738, 0.080045,
                    0.037918, 0.016957, 0.007118, 0.003026,
                    0.001270, 0.000482, 0.000210, 0.000071,
                    0.000020, 0.000006, 0.000000, 0.000000]
        hetero = 0.833333333
        scale = 0.956774771214
        exp_avg = 328
    elif relationship_type == "informal":
        rel_type = 1
        bin_size = 200
        expected = [0.159120, 0.196236, 0.174445, 0.140089,
                    0.105469, 0.075556, 0.052367, 0.035005,
                    0.023288, 0.015160, 0.009357, 0.005755,
                    0.003228, 0.002049, 0.001199, 0.000774]
        hetero = 0.75
        scale = 2.03104913138
        exp_avg = 681
    elif relationship_type == "marital":
        rel_type = 2
        bin_size = 1500
        expected = [0.076216, 0.125540, 0.137884, 0.132489,
                    0.119088, 0.100110, 0.081648, 0.063388,
                    0.048465, 0.035221, 0.025370, 0.018314,
                    0.012766, 0.008317, 0.005764, 0.003480]
        hetero = 0.666666667
        scale = 22.154455184937
        exp_avg = 7299
    elif relationship_type == "commercial":
        rel_type = 3
        bin_size = 3
        expected = [0.348380, 0.227677, 0.147723, 0.096667,
                    0.062807, 0.040239, 0.026340, 0.017745,
                    0.011341, 0.007405, 0.004911, 0.002995,
                    0.001882, 0.001295, 0.000901, 0.000646]
        hetero = 1.0
        scale = 0.01917808219
        exp_avg = 7.0
    else:
        raise ValueError(f"Unknown relationship type = {relationship_type}.")

    if not show_expected:
        expected = None

    plot_relationship_duration_histogram(dir_or_filename=dir_or_filename,
                                         relationship_type=rel_type,
                                         bin_size=bin_size,
                                         expected=expected,
                                         exp_avg=exp_avg,
                                         heterogeneity=hetero,
                                         scale=scale,
                                         show_avg_per_run=show_avg_per_run,
                                         img_dir=img_dir)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('dir_or_filename', type=str, nargs=1, help='A directory with RelationshipEnd.csv files or a single file.')
    parser.add_argument('-o', '--output', default=None, help='If provided, a directory will be created and images saved to the folder.  If not provided, it opens windows.')
    parser.add_argument('-t', '--type_of_relationship', default='marital', help='Options: transitory, informal, marital, commercial')
    parser.add_argument('-m', '--mean', help='Gives the average/mean of each run for that bin.', action='store_true')
    parser.add_argument('-x', '--expected', help='Show the expected Weibull distribution.', action='store_true')

    args = parser.parse_args()

    dir_or_filename = args.dir_or_filename[0]

    possible_relationship_types = ["transitory", "informal", "marital", "commercial"]
    if args.type_of_relationship not in possible_relationship_types:
        raise ValueError("Unknown relationship type = " + args.type_of_relationship)

    plot_relationship_duration_histogram_with_expected(dir_or_filename=dir_or_filename,
                                                       relationship_type=args.type_of_relationship,
                                                       show_avg_per_run=args.mean,
                                                       show_expected=args.expected,
                                                       img_dir=args.output)
