"""
The plot_report_hiv_by_age_and_gender.py is a helper set of functions for
getting the data out of a colleciton of ReportHIVByAgeAndGender.csv files
and plotting it.
"""
import numpy as np
import pandas as pd
import json, os, glob
import matplotlib.pyplot as plt

def get_color_name( idx ):
    """
    Select the color to use give then index
    """
    color_names = [ 'red', 'blue', 'limegreen', 'cyan', 'magenta', 'orange', 'black' ]
    return color_names[ idx % len(color_names) ]

def get_line_style( idx ):
    """
    Select the line style to use give then index
    """
    ls_list = [ "-", "--", ":", "-." ]
    return ls_list[ idx % len(ls_list) ]


def xy_plot( df_pivot,
             num_runs,
             title_1,
             col_name_x,
             strat_names,
             col_name_y,
             min_x=None, max_x=None, min_y=None, max_y=None,
             img_dir=None ):
    """
    Plot the data in X-Y plots.  If img_dir is None, then we plot it so it should
    show up in a notebook.  Otherwise, we create images in the specified folder.
    """

    if img_dir:
        fig, ax = plt.subplots(layout='constrained')
    else:
        fig = plt.figure()
        ax = fig.add_axes([0,0,1,1])

    strat_cols = list(df_pivot.columns.values)

    color_index = 0
    marker_index = 0
    x = df_pivot.index.values.tolist()
    for gender in range(2):
        ls_index = 0
        for run in range(num_runs):
            strat_index = 2*run + gender
            y = df_pivot[ strat_cols[strat_index] ]
            clr = get_color_name( color_index )
            ls = get_line_style( ls_index )

            ax.plot( x, y, c=clr, linewidth=1.0, linestyle = ls, label=strat_names[strat_index] )
            ls_index = ls_index + 1

        color_index = color_index + 1

    if max_x != None:
        max = max_x
        min = 0.0
        if min_x != None:
            min = min_x
        ax.set_xlim( [ min, max ] )

    if max_y != None:
        max = max_y
        min = 0.0
        if min_y != None:
            min = min_y
        ax.set_ylim( [ min, max ] )
        
    ax.minorticks_on()
    ax.grid( which="major", color = 'darkgray', linewidth = 0.5, linestyle = '--' )
    ax.grid( which="minor", color = 'gray'    , linewidth = 0.1, linestyle = '--' )

    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 0.75), fontsize='8')
    ax.set_xlabel( col_name_x )
    ax.set_ylabel( col_name_y )
    ax.set_title( title_1, fontsize='14' )

    if img_dir:
        title_1 = title_1.replace(" ", "_")
        fn = os.path.join( img_dir, title_1 + "_" + ".png" )
        fig.savefig( fn, dpi=300 )
        plt.close(fig)

    return


def get_report_filenames( experiment_dir, base_report_fn ):
    """
    Get the list of reports in the experiment_dir.
    """
    report_filenames = []
    for sim_dir in os.listdir( experiment_dir ):
        full_sim_dir = os.path.join( experiment_dir, sim_dir )
        full_report_fn = os.path.join( full_sim_dir, base_report_fn )
        if os.path.exists( full_report_fn ):
            report_filenames.append( full_report_fn )
            
    return report_filenames


def create_dataframe_from_csv_reports( report_filenames ):
    """
    Read all of the reports and put them into one dataframe
    """
    full_df = pd.DataFrame()
    run = 1
    for fn in report_filenames:
        print("Reading "+fn)
        df = pd.read_csv( fn )
        df["Run_Number"] = run
        full_df = pd.concat([full_df, df])
        run = run + 1

    return full_df


def create_pivot_table_for_ages( df, num_runs, value_column, new_age_name, report_ages, ages_to_remove ):
    """
    For the given value_column, group the data do that you have one column of data for each run and gender
    """
    df_pivot = df.pivot_table( index="Year", columns=["Run_Number"," Gender", " Age"], values=[value_column], aggfunc="sum" )

    if report_ages:
        for run in range(num_runs):
            run = run + 1
            df_pivot[(value_column, run, 0, new_age_name)] = df_pivot[(value_column, run, 0, report_ages[0])]
            df_pivot[(value_column, run, 1, new_age_name)] = df_pivot[(value_column, run, 1, report_ages[0])]
            for age_index in range(1,len(report_ages)):
                df_pivot[(value_column, run, 0, new_age_name)] += df_pivot[(value_column, run, 0, report_ages[age_index])]
                df_pivot[(value_column, run, 1, new_age_name)] += df_pivot[(value_column, run, 1, report_ages[age_index])]

            for age in report_ages:
                df_pivot = df_pivot.drop([(value_column, run, 0, age),(value_column, run, 1, age)], axis=1)
            for age in ages_to_remove:
                df_pivot = df_pivot.drop([(value_column, run, 0, age),(value_column, run, 1, age)], axis=1)

    return df_pivot


def plot_age_based_data( img_dir, df, num_runs, title, value_column ):
    """
    Read the data and plot it
    """
    print("plotting "+title)
    new_age_name = "15_49"
    report_ages = [15,20,25,30,35,40,45]
    ages_to_remove = [50]

    strat_names = []
    for run in range(num_runs):
        run = run + 1
        strat_names.append( str(run)+"-Male")
        strat_names.append( str(run)+"-Female")

    df_pivot = create_pivot_table_for_ages( df, num_runs, value_column, new_age_name, report_ages, ages_to_remove )
    xy_plot( df_pivot,
             num_runs,
             title,
             "Year",
             strat_names,
             value_column,
             min_x=None, max_x=None, min_y=None, max_y=None,
             img_dir=img_dir )


if __name__ == "__main__":

    output_path =  "tutorial_2_results"
    report_filenames = get_report_filenames( output_path, "ReportHIVByAgeAndGender.csv" )
    df = create_dataframe_from_csv_reports( report_filenames )
    num_runs = len(report_filenames)
    plot_age_based_data( output_path, df, num_runs,  "Population (15-49) Over Time",                                  " Population" )
    plot_age_based_data( output_path, df, num_runs,  "Number of People (15-49) on ART Over Time",                     " On_ART" )
    plot_age_based_data( output_path, df, num_runs,  "Number of Newly Infected People (15-49) (Incidence) Over Time", " Newly Infected" )
    plot_age_based_data( output_path, df, num_runs,  "Number of Infected People (15-49) (Prevalence) Over Time",      " Infected" )

