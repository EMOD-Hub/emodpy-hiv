from matplotlib import pyplot as plt
import json
import pandas as pd
import os
from itertools import cycle
import seaborn as sns
import numpy as np
import scipy.stats as st


def plot_experiements(ids_array=[],
                      channels='All',
                      custom_path: str = 'default',
                      subfolder: str = 'output'):

    simulation_results = []
    if custom_path == 'default':
        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(path, "inputs")
    else:
        path = custom_path

    # for each id in the array, add a new element to the simulation_results array
    for id in ids_array:
        file_name = os.path.join(path, id, subfolder, "InsetChart.json")
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)
        simulation_results.append({
            "id": id,
            "table": pd.DataFrame(data['Channels'])
        })
    # channels ='All'
    if channels == 'All':
        df = pd.DataFrame(simulation_results[0]['table'])
        channel_names = sorted(df.columns.tolist())
    else:
        channel_names = sorted(channels)

    j = 1

    # identify the number of rows and columns for the plot based on the number of channels
    cols = 1
    rows = 1
    if len(channel_names) % 2 == 0:
        rows = int(len(channel_names) / 2)
        cols = 2
    else:
        rows = int(len(channel_names) / 2) + 1
        cols = 2

    fig = plt.figure().set_size_inches((5 * cols), ((2 * rows) + 3))
    plt.subplots_adjust(left=0.05, bottom=0.05, right=.98, top=.96, wspace=0.1, hspace=0.3)

    plt.style.use('ggplot')
    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)

    for channel in channel_names:
        exp = 0
        color = cycle(["black", "magenta", "green", "cyan", "orange"])
        # marker = cycle([".", "v", "o", "s", "x", "d"])
        linestyle = cycle(["-", "--", ":"])
        for simulation in simulation_results:
            c = next(color)
            # m = next(marker)
            ls = next(linestyle)
            y = simulation['table'][channel]['Data']
            x = range(0, len(y))
            plt.subplot(rows, cols, j)
            plt.plot(x, y, color=c, linewidth=.5, linestyle=ls, label=simulation['id'])
            # plt.scatter(x, y, marker=m, color=c, s=.5)
            plt.title(channel.replace(",", ",\n").replace(":", ":\n"), fontsize=7)
            exp += 1
        if j == 1:
            plt.figlegend( loc='upper center', ncol=2, fontsize=10)

        j += 1

    plt.savefig("All_Channels.png")
    plt.show()
    plt.close(fig)


def plot_all(file_name):
    """_summary_

    Args:
        df (_type_): _description_
    """
    # create a pandas dataframe from the json file myjson.json
    with open(file_name, 'r') as json_file:
        data = json.load(json_file)

    df = pd.DataFrame(data['Channels'])
    channel_names = sorted(df.columns.tolist())
    channels_data = df
    j = 1
    color = cycle(["blue", "darkgreen", "darkmagenta", "darkblue", "indigo", "orange"])
    fig = plt.figure().set_size_inches(15, 10)
    plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=.92, wspace=0.4, hspace=0.8)
    plt.style.use('ggplot')
    plt.rc('xtick', labelsize=6)
    plt.rc('ytick', labelsize=6)
    for channel in channel_names:
        y = channels_data[channel]['Data']
        x = range(0, len(y))
        plt.subplot(7, 6, j)
        plt.plot(x, y, color="grey", linewidth=.3)
        plt.scatter(x, y, marker='o', color=next(color), s=1)
        plt.title(channel.replace(",", ",\n").replace(":", ":\n"), fontsize=7)
        j += 1
    plt.savefig("All_Channels.png")
    plt.show()
    plt.close(fig)


def property_report(path="output", filename="PropertyReport.json"):
    """_summary_

    Args:
        path (str, optional): _description_. Defaults to "output".
        filename (str, optional): _description_. Defaults to "PropertyReport.json".
    """
    propertyfile = os.path.join(path, filename)
    rawdata = ""
    with open(propertyfile) as json_file:
        rawdata = json.load(json_file)

    pr_data = pd.DataFrame(rawdata['Channels'])
    pr_channel_names = pr_data.columns.sort_values()
    colors = ["blue", "deepskyblue", "orchid", "chocolate", "blueviolet", "limegreen", "deeppink", "darkmagenta",
              "slateblue", "red", "green", "pink"]

    for i in range(0, 35, 12):
        sp = 1
        c = 0
        fig = plt.figure().set_size_inches(12, 10)
        plt.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=.92, wspace=0.4, hspace=0.8)
        # 12 channels:
        subset = pr_channel_names[i:i + 12]

        for validate_channel in subset:
            y = pr_data[validate_channel]['Data']
            x = range(0, len(y))
            plt.subplot(4, 3, sp)
            plt.plot(x, y, color="lightblue", linewidth=.4)
            plt.scatter(x, y, marker='o', color=colors[c], s=3)
            plt.title(validate_channel.replace(",", "\n"), fontsize=7)
            sp = sp + 1
            c = c + 1
            plt.savefig(f"Property_Report_Set_{i}.png")

        plt.show()
        plt.close(fig)


def plot_event_report(EventReport, xvalues="Year", yvalues="AgeYears", useAgeInt=False, useYearInt=False, title="Event Report", fig_dir="figs",
                      colors_arr=["blue", "deepskyblue", "orchid", "chocolate", "blueviolet", "limegreen", "deeppink",
                                  "darkmagenta", "slateblue", "red", "green", "pink"],
                      marker_arr=["o", "v", "*"]):
    """_summary_

    Args:
        data (_type_): _description_
        xvalues (str, optional): _description_. Defaults to "Year".
        yvalues (str, optional): _description_. Defaults to "AgeYears".
        title (str, optional): _description_. Defaults to "Event Report".
        fig_dir (str, optional): _description_. Defaults to "figs".
        colors_arr (list, optional): _description_. Defaults to ["blue","deepskyblue", "orchid", "chocolate", "blueviolet", "limegreen", "deeppink", "darkmagenta", "slateblue", "red", "green", "pink"].
        marker_arr (list, optional): _description_. Defaults to ["o", "v", "*"].
    """
    import matplotlib.pyplot as plot

    # Verify if EventReport is a valid csv file
    if not os.path.isfile(EventReport):
        print("Error: EventReport is not a valid csv file")
        return

    # Load the CSV data into a pandas dataframe
    data = pd.read_csv(EventReport)

    data['AgeYears'] = data['Age' ].apply(lambda x: int(x / 365))
    data['YearInt' ] = data['Year'].apply(lambda x: int(x      ))

    # Get the list of unique event names from event_df
    event_names = data['Event_Name'].unique().tolist()

    # Create a scatter plot where the series are the event_names
    # form dataframe
    marker = cycle(marker_arr)
    colors = cycle(colors_arr)

    data = data[[xvalues, yvalues, 'Event_Name']]

    plot.rcParams["figure.figsize"] = [12, 10]

    # create a plot for this data
    fig, ax = plot.subplots()
    num = 0
    for event in event_names:
        num += 1
        ax = data.loc[data.Event_Name == event].plot(x=xvalues, y=yvalues, kind='scatter', ax=ax, marker=next(marker),
                                                     alpha=0.5, label=event, s=8, color=next(colors))
        # ax = data.loc[data.Event_Name == event].plot(x=xvalues, y=yvalues, kind='line', ax=ax,
        #                                              alpha=0.5, label=event, )
    # Add titles
    plot.title(title)
    plot.xlabel(xvalues)
    plot.ylabel(yvalues)
    plot.legend(loc='best')
    os.makedirs(fig_dir, exist_ok=True)
    plot.savefig(os.path.join(fig_dir, f"{yvalues}Event_Report.png"))
    plot.show()
    plot.close(fig)


def plot_heatmap_relationships(filename="output/RelationshipStart.csv", title="Relationships", output_dir="figs"):
    """_summary_

    Args:
        filename (str, optional): _description_. Defaults to "output/RelationshipStart.csv".
        title (str, optional): _description_. Defaults to "Relationships".
        output_dir (str, optional): _description_. Defaults to "figs".

    Returns:
        _type_: _description_

    """
    sns.set()

    rel_names = ['Transitory', 'Informal', 'Marital']
    fig_dir = output_dir

    dat = pd.read_csv(filename)
    dat['Count'] = 1
    dat['MALE_age_floor'] = dat['A_age'].floordiv(1)
    dat['FEMALE_age_floor'] = dat['B_age'].floordiv(1)
    dat['Rel_type'] = dat['Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)']

    os.makedirs(fig_dir, exist_ok=True)

    for rel_type in rel_names:
        rel_dat = dat[dat['Rel_type'] == rel_names.index(rel_type)]
        print('male-', rel_dat['MALE_age_floor'].min())
        print('female-', rel_dat['FEMALE_age_floor'].min())

        # Pivot the data to create a heatmap matrix
        heatmap_data = rel_dat.pivot_table(index='MALE_age_floor', columns='FEMALE_age_floor', values='Count',
                                           fill_value=0)

        # Create a heatmap using seaborn
        plt.figure(figsize=(10, 10))
        sns.heatmap(heatmap_data, annot=False, cmap='YlGnBu', vmin=0, vmax=1)
        # reverse the order of the y axis values
        plt.gca().invert_yaxis()

        # Set the labels and title of the heatmap
        plt.xlabel('FEMALE_age_floor')
        plt.ylabel('MALE_age_floor')
        plt.title(f'Relationship Heatmap - {rel_type}')

        # Save the heatmap figure
        plt.savefig(os.path.join(fig_dir, f'heatmap_{rel_type}.png'))

        # Display the heatmap
        plt.show()


def plot_heatmap_from_matrix(data, title="Joint Probability Heatmap", subtitle="", fig_dir="figs", color_map='YlGnBu',
                             include_annotations=True,
                             min_age=17.5, bin_size=2.5, fig_size=(12, 10)):
    """_summary_

    Args:
        data (_type_): _description_
        title (str, optional): _description_. Defaults to "Joint Probability Heatmap".
        subtitle (str, optional): _description_. Defaults to "".
        fig_dir (str, optional): _description_. Defaults to "figs".
        color_map (str, optional): _description_. Defaults to 'YlGnBu'.
        include_annotations (bool, optional): _description_. Defaults to True.
        min_age (float, optional): _description_. Defaults to 17.5.
        bin_size (float, optional): _description_. Defaults to 2.5.
        fig_size (tuple, optional): _description_. Defaults to (12,10).

    Returns:
        _type_: _description_

    """
    sns.set()
    # read the matrix into a dataframe
    dat = pd.DataFrame(data)
    # add column names and index names
    max_col = min_age + bin_size * len(dat.columns)
    dat.columns = np.arange(min_age, max_col, bin_size)

    max_index = min_age + bin_size * len(dat)
    dat.index = np.arange(min_age, max_index, bin_size)

    # dat['Count'] = 1
    # create a heatmap plot
    plt.figure(figsize=fig_size)
    # plt.imshow( dat)
    sns.heatmap(dat, annot=include_annotations, cmap=color_map, annot_kws={"size": 8})
    # reverse the order of the y axis values
    plt.gca().invert_yaxis()

    # plt.axis('equal')
    # Set the labels and title of the heatmap
    plt.title(f'{title} \n {subtitle}\n # Bins:{len(dat.columns)} ')
    os.makedirs(fig_dir, exist_ok=True)
    # Save the heatmap figure
    # Display the heatmap
    output_file = os.path.join("figs", f'{title}-{subtitle}.png')
    plt.savefig(output_file)
    plt.show()


def chart_age_gender_compare(df, col_series=['Ratio Has Debuted', 'Ratio First Coital Act'], age_array=[], cols=2):
    """_summary_
    It compares the two sets of data from the generated combined report (Benchmark and Test)

    Args:
        df (_type_): _description_
        col_series (list, optional): _description_. Defaults to ['Ratio Has Debuted', 'Ratio First Coital Act'].
        age_array (list, optional): _description_. Defaults to [].
        cols (int, optional): _description_. Defaults to 2.
    """
    # data and arrays:
    subplot_filters = df['Test'].unique()
    genders = df['Gender'].unique()
    if len(age_array) == 0:
        age_array = df['Age'].unique()

    # plots features
    plt.style.use('ggplot')
    fig, axs = plt.subplots(nrows=len(age_array), ncols=cols, figsize=(14, 14), layout='constrained')
    marker = cycle(["o", "v"])

    # plots
    for r, age in enumerate(age_array):
        for c, subplot in enumerate(subplot_filters):
            for serie in col_series:
                for gender in genders:
                    ss = df.loc[(df['Gender'] == gender) & (df['Age'] == age) & (df['Test'] == subplot)]
                    y = ss[serie]
                    x = ss['Year']
                    # color=next(colors),
                    axs[r, c].plot(x, y, linestyle="-", linewidth=.4, markersize=2, marker=next(marker),
                                   label=f"{gender} - {serie}")
                    axs[r, c].legend(fontsize=8)
                    axs[r, c].set_ylim((0, 1.1))
                    axs[r, c].set_title(f"{age}  {subplot}", size='small')

    fig.supxlabel('Year')
    fig.supylabel('Percent')
    fig.savefig(f"Comparing Plots {'_'.join([str(i) for i in age_array])}.png")
    plt.show()
    plt.close(fig)


def chart_age_gender_splitted_subplots(df,
                                       col_series=['Ratio Has Debuted',
                                                   'Ratio First Coital Act'],
                                       age_array=[[13, 17], [18, 20]],
                                       addlines=False,
                                       title="",
                                       genders=['Female', 'Male'],
                                       markeroutline=['gray', 'darkred'],
                                       fillingcolor=['lightgray', 'red'],
                                       markers=['o', 'v'],
                                       leftinclusive=False, rightinclusive=True):
    """
    This function plots the data ReportByAgeAndGender.csv

    Args:
        df (_type_): _description_
        col_series (list, optional): _description_. Defaults to ['Ratio Has Debuted', 'Ratio First Coital Act'].
        age_array (list, optional): _description_. Defaults to [[13,17], [18,20]].
        addlines (bool, optional): _description_. Defaults to False.
        title (str, optional): _description_. Defaults to "".
        genders (list, optional): _description_. Defaults to ['Female', 'Male'].
        markeroutline (list, optional): _description_. Defaults to ['gray', 'darkred'].
        fillingcolor (list, optional): _description_. Defaults to ['lightgray', 'red'].
        markers (list, optional): _description_. Defaults to ['o', 'v'].
        leftinclusive (bool, optional): _description_. Defaults to False.
        rightinclusive (bool, optional): _description_. Defaults to True.
    """

    # data and arrays:
    title = title.replace('.json', '')
    if len(age_array) == 0:
        age_array = df['Age'].unique()

    # plots features
    plt.style.use('ggplot')
    fig, axs = plt.subplots(nrows=len(genders), ncols=len(age_array), figsize=(14, 10), layout='constrained')
    marker = cycle(markers)
    filling = cycle(fillingcolor)
    outlinecolor = cycle(markeroutline)

    # plots
    for r, gender in enumerate(genders):
        for c, age in enumerate(age_array):
            for serie in col_series:
                if leftinclusive and rightinclusive:
                    ss = df.loc[(df['Gender'] == gender) & (df['Age'] >= age[0]) & (df['Age'] <= age[1])]
                elif leftinclusive and not rightinclusive:
                    ss = df.loc[(df['Gender'] == gender) & (df['Age'] >= age[0]) & (df['Age'] < age[1])]
                elif not leftinclusive and rightinclusive:
                    ss = df.loc[(df['Gender'] == gender) & (df['Age'] > age[0]) & (df['Age'] <= age[1])]
                y = ss[serie]
                x = ss['Year']
                axs[r, c].scatter(x, y, marker=next(marker), s=10, facecolors=next(filling), color=next(outlinecolor),
                                  label=f"{gender} - {serie}")
                if addlines:
                    axs[r, c].plot(x, y, linestyle="-", linewidth=.4)
                axs[r, c].legend(fontsize=8)
                axs[r, c].set_ylim((0, 1.1))
                axs[r, c].set_title(f"{age} include Left: {leftinclusive}, Right: {rightinclusive}", size='medium')

    fig.supxlabel('Year')
    fig.supylabel('Percent')
    suptitle = f"Plots By Bin And Gender {title}{'_'.join([str(i) for i in age_array])}"
    fig.suptitle(suptitle)
    fig.savefig(f"{suptitle}.png")
    plt.show()
    plt.close(fig)


def chart_age_gender_byage(df=False, sexdebut_series=['Ratio Has Debuted', 'Ratio First Coital Act'], age_array=[0],
                           genders=["Male", "Female"], output_path="output"):
    """
    Plots for ReportHIVByAgeAndGender.csv

    Args:
        df (bool, optional): _description_. Defaults to False.
        sexdebut_series (list, optional): _description_. Defaults to ['Ratio Has Debuted', 'Ratio First Coital Act'].
        age_array (list, optional): _description_. Defaults to [0].
        genders (list, optional): _description_. Defaults to ["Male", "Female"].
    """
    if df.empty: 
        read_ReportHIVByAgeAndGender(output_path=output_path, type="Test", age_gender_report_name='ReportHIVByAgeAndGender.csv')

    description = '-'.join([str(i) for i in age_array])
    marker = cycle(["o", ".", "v", "2", "*"])
    plt.style.use('ggplot')
    fig = plt.figure()
    fig.set_size_inches(12, 8)
    for serie in sexdebut_series:
        for gender in genders:
            ss = df.loc[(df['Gender'] == gender) & (df['Age'].isin(age_array))]
            y = ss[serie]
            x = ss['Year']
            plt.plot(x, y, linestyle="-", linewidth=1, markersize=5, marker=next(marker), label=f"{gender} - {serie}")
            # plt.scatter(x, y, marker = next(marker), color =next(color), s=10, label=f"{gender} - {serie }")
            plt.xlabel("Time")
            plt.ylabel("Percentage")

    plt.legend()
    plt.title(f" {description} years Old - HIV Sexual Debut with Coital Acts as Standard Intervention")
    plt.savefig(f"{description}HIVSexualDebutAsStandardIntervention.png")
    plt.show()
    plt.close(fig)


def chart_age_gender_sets(df="", sexdebut_series=['Ratio Has Debuted', 'Ratio First Coital Act'],
                          age_gender_sets=[[15, "Female"], [15, "Male"]], test_case="", title="", output_path="output"):
    """
    Plots for ReportHIVByAgeAndGender.csv

    Args:
        df (str, optional): _description_. Defaults to "".
        sexdebut_series (list, optional): _description_. Defaults to ['Ratio Has Debuted', 'Ratio First Coital Act'].
        age_gender_sets (list, optional): _description_. Defaults to [[15, "Female"],[15, "Male"]].
        test_case (str, optional): _description_. Defaults to "".
        title (str, optional): _description_. Defaults to "".
    """
    if df.empty: 
        read_ReportHIVByAgeAndGender(output_path=output_path, type="Test", age_gender_report_name='ReportHIVByAgeAndGender.csv')

    marker = cycle(["o", "v"])
    plt.style.use('ggplot')
    fig = plt.figure()
    fig.set_size_inches(12, 8)
    description = []
    title = title.replace('.json', '')
    print("Start plotting Sexual Debut for specific Age - Gender Charts ...")
    for target_set in age_gender_sets:
        for serie in sexdebut_series:
            ss = df.loc[(df['Age'] == target_set[0]) & (df['Gender'] == target_set[1])]
            y = ss[serie]
            x = ss['Year']
            plt.ylim([0, 1.1])
            plt.plot(x, y, linestyle="-", linewidth=1, markersize=5, marker=next(marker),
                     label=f"{target_set[0]}-{target_set[1]}: {serie}")
            plt.xlabel("Time")
            plt.ylabel("Percentage")

        description.append(' '.join([str(i) for i in target_set]))
    plt.legend()
    description = ' & '.join([str(i) for i in description])
    plt.title(f" {description} years old. {test_case} {title}")
    plt.savefig(f"{description}_{title}{test_case}.png")
    plt.show()
    plt.close(fig)


def read_ReportHIVByAgeAndGender(output_path='output', age_gender_report_name='ReportHIVByAgeAndGender.csv', type="Test"):
    """_summary_

    Args:
        output_path (str, optional): _description_. Defaults to 'output'.
        age_gender_report_name (str, optional): _description_. Defaults to 'ReportHIVByAgeAndGender.csv'.
        type (str, optional): _description_. Defaults to "Test".

    Returns:
        _type_: _description_
    """
    # Load the CSV data into a pandas dataframe
    print(f"file location: {output_path} \nfile name:{age_gender_report_name}")
    filename = os.path.join(output_path, age_gender_report_name)
    out_path = os.path.join(output_path, "ReportHIVByAgeAndGender_percent.csv")
    df = pd.read_csv(filename)
    df["Ratio Has Debuted"] = df["Has Debuted"] / df[" Population"]
    df["Ratio First Coital Act"] = df["Had First Coital Act"] / df[" Population"]
    df['Gender'] = df[' Gender'].apply(lambda x: 'Female' if x == 1 else 'Male')
    df['Age'] = df[' Age']
    df['Test'] = type
    df.to_csv(out_path, sep=',')
    print(df.head)
    return df


def get_best_distribution(data):
    """_summary_

    Args:
        data (_type_): _description_

    Returns:
        _type_: _description_
    """
    dist_names = ["norm", "exponweib", "weibull_max", "weibull_min", "pareto", "genextreme"]
    dist_results = []
    params = {}
    for dist_name in dist_names:
        dist = getattr(st, dist_name)
        param = dist.fit(data)

        params[dist_name] = param
        # Applying the Kolmogorov-Smirnov test
        D, p = st.kstest(data, dist_name, args=param)
        print("p value for " + dist_name + " = " + str(p))
        dist_results.append((dist_name, p))

    # select the best fitted distribution
    best_dist, best_p = (max(dist_results, key=lambda item: item[1]))
    # store the name of the best fit and its p value

    print("Best fitting distribution: " + str(best_dist))
    print("Best p value: " + str(best_p))
    print("Parameters for the best fit: " + str(params[best_dist]))

    return best_dist, best_p, params[best_dist]


if __name__ == "__main__":
    channels_subset = ["Prevalence (Females, 15-49)",
                       "Infected",
                       "Prevalence (Females, 15-49)",
                       "Prevalence (Males, 15-49)",
                       "Prevalence among Sexually Active (Adults)",
                       "Single Post-Debut Men",
                       "Single Post-Debut Women",
                       "Susceptible Population",
                       "Waning Population",
                       "Number of (untreated) Individuals with AIDS",
                       "Number of Events"]
    experiment_id = os.path.join("02_184217", "35b9d80a-8e61-ee11-92fc-f0921c167864")

    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(path, "inputs", experiment_id)

    # folder ids (usualy the simulation folder ids)
    simulation_root_folders_array = os.listdir(path)

    plot_experiements(simulation_root_folders_array, channels="All", custom_path=path) # plot all channels for several experiments
    plot_experiements(simulation_root_folders_array, channels=channels_subset, custom_path=path) # plot all channels for several experiments

    for x in range(len(simulation_root_folders_array)):
        Ev_Recorder_path = os.path.join(path, simulation_root_folders_array[x], 'output', 'ReportEventRecorder.csv')
        plot_event_report(Ev_Recorder_path, 
                          xvalues="Time", 
                          yvalues="Age", 
                          useAgeInt=True,  
                          title=f"Event Report for {simulation_root_folders_array[x]}")
