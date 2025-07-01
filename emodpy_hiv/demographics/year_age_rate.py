"""
This module contains stuff related to a YearAgeRate dataframe object that can be used
to create demographic objects.
"""

from typing import List, Tuple, Dict
import pandas as pd
from emod_api.demographics.age_distribution import AgeDistribution
from emod_api.demographics.fertility_distribution import FertilityDistribution
from emod_api.demographics.mortality_distribution import MortalityDistribution


class YearAgeRate:
    """
    The YearAgeRate class is a wrapper around a pandas dataframe such that the dataframe
    is expected to have a specific format that is used in the demographics.  Objects of
    this class are used as output from UN World Pop functions and as input into the
    creation of a Demograhics object.  This gives us a standard format of the data for
    most population-based demographic data.

    The dataframe is expected to have four columns:
        * node_id: An integer representing the node the data is associated with
        * min_year: A float representing the calendar start year of the period of years
            for which the represents.
        * min_age: A float representing the age of the people in years.
        * rate: The value (a float) of this column depends on the data contained.
            It can be a rate of fertility or mortality or a fraction of the population.

    This format assumes that the year/age ranges are contiguous from one value to the
    next largest value.  For example, if a row has a min_age = 15 and the next row of
    the same year with the next largest min_age is 20, then the data for the row where
    min_age = 15 is for the age range of [15-20), where 15 is included and 20 is excluded.
    This is the same for min_year.

    For a given node id, the format assumes that each min_year has the exact same set
    of min_ages.  Different nodes can have different min_years or min_ages, but within
    a given node, they must be the same.  The format also assumes that min_year and
    min_age for a given node are not duplicated.
    """

    COL_NAME_NODE_ID  = "node_id"    # Noqa: E221
    COL_NAME_MIN_YEAR = "min_year"
    COL_NAME_MIN_AGE  = "min_age"    # Noqa: E221
    COL_NAME_RATE     = "rate"       # Noqa: E221
    COL_NAMES = [
        COL_NAME_NODE_ID,
        COL_NAME_MIN_YEAR,
        COL_NAME_MIN_AGE,
        COL_NAME_RATE
    ]
    SORT_BY_COLUMNS = [
        COL_NAME_NODE_ID,
        COL_NAME_MIN_YEAR,
        COL_NAME_MIN_AGE
    ]

    @staticmethod
    def _validate_df(df):
        """
        Throws an exception if dataframe doesn't conform to one of the following:
            * Not the expected column names
            * Number of min_ages not the same for each min_year
            * Not the exact set of min_ages for each min_year
            * If there are dupliate rows that have the same node_id, min_year, and min_age.
        """
        node_group_collection = df.groupby(YearAgeRate.COL_NAME_NODE_ID)
        for node_id, node_group in node_group_collection:
            prev_min_year = 0
            prev_num_min_ages = 0
            prev_min_ages = []
            min_year_group_collection = node_group.groupby(YearAgeRate.COL_NAME_MIN_YEAR)
            for min_year, min_year_group in min_year_group_collection:
                # check that there are no duplicate min_years
                min_ages = sorted(min_year_group[YearAgeRate.COL_NAME_MIN_AGE].unique())
                num_min_ages_unique = len(min_ages)
                num_min_ages_total  = len(min_year_group[YearAgeRate.COL_NAME_MIN_AGE])              # Noqa: E221
                if num_min_ages_total != num_min_ages_unique:
                    min_year_list = min_year_group[YearAgeRate.COL_NAME_MIN_AGE].tolist()
                    msg =  f"Invalid duplicate number of entries for {YearAgeRate.COL_NAME_MIN_AGE} "# Noqa: E222
                    msg += f"for node_id={node_id} and min_year={min_year}.\n"
                    msg += f"min_ages={min_year_list}"
                    raise ValueError(msg)
                elif prev_num_min_ages == 0:
                    prev_num_min_ages = num_min_ages_total
                    prev_min_ages = min_ages
                    prev_min_year = min_year
                elif prev_num_min_ages != num_min_ages_total:
                    msg =  f"Invalid number of min_ages for min_year={min_year}.\n"                  # Noqa: E222
                    msg += f"Number of min_ages={prev_num_min_ages} for min_year={prev_min_year}.\n"
                    msg += f"Number of min_ages={num_min_ages_total} for min_year={min_year}."
                    raise ValueError(msg)
                elif min_ages != prev_min_ages:
                    msg =  f"Inconsistent set of min_ages for min_year={min_year}.\n"                # Noqa: E222
                    msg += f"Min_ages for min_year={prev_min_year} are: {prev_min_ages}.\n"
                    msg += f"Min_ages for min_year={min_year} are: {min_ages}."
                    raise ValueError(msg)

    def __init__(self,
                 df: pd.DataFrame = None,
                 csv_filename: str = None):
        """
        Construct a YearAgeRate object from the given dataframe OR one that is contained in a CSV.
        You can only define the dataframe OR the csv_filename, bot NOT both.

        Args:
            df: A pandas dataframe that follows the format of a YearAgeRate object.
            csv_filename: A CSV file containing data for YearAgeRate dataframe.
        """
        if (df is None and csv_filename is None) or (df is not None and csv_filename is not None):
            raise ValueError("You must define either 'df' or 'csv_filename', but not both.")

        if csv_filename is not None:
            df = pd.read_csv(csv_filename)

        if YearAgeRate.COL_NAMES in df.columns.tolist():
            msg = "The dataframe provided does not have the column names expected.\n"
            msg += f"Must have at least: {YearAgeRate.COL_NAMES}\n"
            msg += f"Actual: {df.columns.tolist()}"
            raise ValueError(msg)

        YearAgeRate._validate_df(df)

        self.df = df.sort_values(by=YearAgeRate.SORT_BY_COLUMNS, ascending=True)

    def to_csv(self, csv_filename):
        """
        Save the dataframe to a csv file.

        Args:
            csv_filename: The name of the file to write the dataframe to.
        """
        self.df.to_csv(csv_filename, index=False)

    def to_age_distributions(self) -> List[Tuple[int, AgeDistribution]]:
        """
        Convert this YearAgeRate object ot a list of (node_id, AgeDistribution) tuples.
        For each node in the dataframe, there will be a tuple in the list where the first
        value is the node_id and the second is an AgeDistribution object that can be used
        when creating a Demographics object.

        The "rate" column is assumed to be the fraction of people in that year and age range.
        The dataframe is also assumed to only have the data for one year.

        NOTE: EMOD expects the ReslutValues/Ages to be maximums of the bin. This implies that
        if the last age has a DistributionValue = 1.0, then there should be no people aged
        greater than this last age.  It also means that the first age is also a minimum.
        For example, if the first age were 1.0, then there can be zero people less than 1.0.
        !!!THIS APPLIES ONLY TO THE OUTPUT OF THIS FUNCTION AND NOT THE INPUT!!!
        """

        unique_min_year_list = self.df[YearAgeRate.COL_NAME_MIN_YEAR].unique()
        if len(unique_min_year_list) != 1:
            msg = f"To be converted to an AgeDistribution, the dataframe must have only one " \
                  f"'{YearAgeRate.COL_NAME_MIN_YEAR}'.\n"
            msg += f"The dataframe has the following unique values for 'min_year': {unique_min_year_list}"
            raise ValueError(msg)

        age_distributions = []

        node_group_collection = self.df.groupby(YearAgeRate.COL_NAME_NODE_ID)
        for node_id, node_group in node_group_collection:
            # -----------------------------------------------------------------------------
            # --- Turn the collection of individual fractions into cumulative distribution
            # -----------------------------------------------------------------------------
            fractions = node_group[YearAgeRate.COL_NAME_RATE]
            cumulative_fractions = []
            cum = 0
            total = sum(fractions)
            for frac in fractions:
                # ensure fractions are normalized
                cum += round(frac / total, 6)
                cumulative_fractions.append(cum)
            cumulative_fractions[-1] = 1.0  # ensure last value is exactly 1
            ages = node_group[YearAgeRate.COL_NAME_MIN_AGE].tolist()

            # ------------------------------------------------------------------------
            # --- Make Ages Maximums (see above)
            # --- Insert a zero at the beginning of the fractions to force the values
            # --- to be associated with next age or the maximum of the age range.
            # --- Insert 125 at the end of the ages so that the 1.0 of the fractions
            # --- is associated with 125 - no one is older than 125.
            # ------------------------------------------------------------------------
            cumulative_fractions.insert(0, 0.0)
            ages.append(125.0)

            # -------------------------------
            # --- Convert to dictionary/JSON
            # -------------------------------
            # TODO: we should be creating and returning distribution objects by constructor here, not json/converting
            #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv-old/issues/316
            ages_and_fractions = {
                'ResultValues': ages,
                'DistributionValues': cumulative_fractions,
                'NumDistributionAxes': 0,
                'ResultUnits': 'years',
                'ResultScaleFactor': 365
            }

            # ----------------------------------------------------------
            # --- Convert from dictionary/JSON to AgeDistribution object
            # ----------------------------------------------------------
            age_distribution = AgeDistribution.from_dict(distribution_dict=ages_and_fractions)
            age_distributions.append((node_id, age_distribution))

        return age_distributions

    @staticmethod
    def _node_group_to_distribution_json(node_group: pd.DataFrame,
                                         stepwise_for_year: bool = True) -> Dict:
        """
        Since fertility and mortality data is formatted the same, this method converts the dataframe
        to an EMOD distribution dictionary.  This dictionary can be used with FertilityDistribution's
        or MortalityDistribution's from_dict() method to create the appropriate distribution object.

        The method assumes that the user wants the data in a step-wise format.  That is, for a
        calendar year range and age range, the user wants EMOD to produce the same value/rate
        for the entire range.  The rate doesn't change until the year or age moves to a new range.

        For the max age of the last bin, a value of 125 is used and, for the max_year of the last bin,
        a value of 2100 is used.
        """
        new_node_group = pd.DataFrame()

        # ---------------------------------------------------------------------------------
        # --- Break the collection for the node into groups by min_year
        # --- Then, find the max age of the bin based on the next age (in the next row)
        # --- Things should be sorted such that for the given min_year, the ages are unique
        # --- Create a new group that has ths new/temporary column
        # ---------------------------------------------------------------------------------
        min_year_group_collection = node_group.groupby(YearAgeRate.COL_NAME_MIN_YEAR)
        for min_year, min_year_group in min_year_group_collection:
            min_year_group["max_age"] = min_year_group[YearAgeRate.COL_NAME_MIN_AGE].shift(-1) - 0.001
            min_year_group["max_age"] = min_year_group["max_age"].fillna(125)
            new_node_group = pd.concat([new_node_group, min_year_group])
        new_node_group = new_node_group.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE],
                                                    ascending=True)

        # ----------------------------------------------------------------------------------
        # --- Duplicate the set of rows, but have the min_age be the max_age determined above
        # ----------------------------------------------------------------------------------
        node_group_max_age = new_node_group.copy()
        node_group_max_age.drop([YearAgeRate.COL_NAME_MIN_AGE], axis=1, inplace=True)
        node_group_max_age.rename({"max_age": YearAgeRate.COL_NAME_MIN_AGE}, axis=1, inplace=True)
        new_node_group.drop(["max_age"], axis=1, inplace=True)
        new_node_group = pd.concat([new_node_group, node_group_max_age]).reset_index()
        new_node_group = new_node_group.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE],
                                                    ascending=True)

        # ------------------------------------------------------------------------------------
        # --- Do like we did for min_age, but do it for min_year.  That is, create a new
        # --- max_year column that has the value of min_year in the next row minus a smidge.
        # ------------------------------------------------------------------------------------
        if stepwise_for_year:
            new_node_group2 = pd.DataFrame()
            min_age_group_collection = new_node_group.groupby(YearAgeRate.COL_NAME_MIN_AGE)
            for min_age, min_age_group in min_age_group_collection:
                min_age_group["max_year"] = min_age_group[YearAgeRate.COL_NAME_MIN_YEAR].shift(-1) - 0.001
                min_age_group["max_year"] = min_age_group["max_year"].fillna(2101)
                new_node_group2 = pd.concat([new_node_group2, min_age_group])
            new_node_group = new_node_group2.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE],
                                                        ascending=True)

            # ----------------------------------------------------------------------------------
            # --- Duplicate the set of rows, but have the min_year be the max_year determined above
            # ----------------------------------------------------------------------------------
            node_group_max_year = new_node_group.copy()
            node_group_max_year.drop([YearAgeRate.COL_NAME_MIN_YEAR], axis=1, inplace=True)
            node_group_max_year.rename({"max_year": YearAgeRate.COL_NAME_MIN_YEAR}, axis=1, inplace=True)
            new_node_group.drop(["max_year"], axis=1, inplace=True)
            new_node_group = pd.concat([new_node_group, node_group_max_year])
            new_node_group = new_node_group.sort_values(by=[YearAgeRate.COL_NAME_MIN_YEAR, YearAgeRate.COL_NAME_MIN_AGE],
                                                        ascending=True)
        else:
            # Not coming up with a quick way to determine that the difference between years is 5.
            difference_between_years = 5
            new_node_group[YearAgeRate.COL_NAME_MIN_YEAR] = new_node_group[YearAgeRate.COL_NAME_MIN_YEAR] + difference_between_years/2.0

        # -----------------------------------------
        # --- Create the JSON for the distribution
        # -----------------------------------------
        dist_dict = {
            "NumDistributionAxes": 2,
            "AxisNames": ["age", "year"],
            "AxisUnits": ["years", "simulation_year"],
            "AxisScaleFactors": [365, 1],
            "PopulationGroups": [
                [],
                []
            ],
            "ResultScaleFactor": (1.0 / 365.0),  # 2.73972602739726e-03,
            "ResultUnits": "",
            "ResultValues": []
        }

        min_ages  = sorted(new_node_group[YearAgeRate.COL_NAME_MIN_AGE ].unique().tolist()) # Noqa: E221, E202
        min_years = sorted(new_node_group[YearAgeRate.COL_NAME_MIN_YEAR].unique().tolist())

        dist_dict["PopulationGroups"][0] = min_ages
        dist_dict["PopulationGroups"][1] = min_years

        min_age_group_collection = new_node_group.groupby(YearAgeRate.COL_NAME_MIN_AGE)
        for min_age, min_age_group in min_age_group_collection:
            rate_values = min_age_group[YearAgeRate.COL_NAME_RATE].tolist()
            dist_dict["ResultValues"].append(rate_values)

        return dist_dict

    def to_fertility_distributions(self) -> List[Tuple[int, FertilityDistribution]]:
        """
        Convert this YearAgeRate object to a list of tuples of node_id and FertilityDistribution.

        The method assumes that the user wants the data in a step-wise format.  That is, for a
        calendar year range and age range, the user wants EMOD to produce the same value/rate
        for the entire range.  The rate doesn't change until the year or age moves to a new range.

        For the max age of the last bin, a value of 125 is used and, for the max_year of the last bin,
        a value of 2100 is used.  Using these maximums still produces the correct values because we
        want the result constant for the entire range.  Having the range wider just produces
        the same constant.
        """
        fertility_distributions = []

        node_group_collection = self.df.groupby(YearAgeRate.COL_NAME_NODE_ID)
        for node_id, node_group in node_group_collection:
            # TODO: we should be creating and returning distribution objects in this call, not json/converting below
            #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv-old/issues/316
            dist_dict = YearAgeRate._node_group_to_distribution_json(node_group)
            dist_dict["ResultUnits"] = "annual birth rate per 1000 women"
            dist_dict["ResultScaleFactor"] = dist_dict["ResultScaleFactor"] / 1000.0

            distribution = FertilityDistribution.from_dict(distribution_dict=dist_dict)
            fertility_distributions.append((node_id, distribution))

        return fertility_distributions

    def to_mortality_distributions(self, stepwise_for_year: bool =True) -> Dict[int, MortalityDistribution]:
        """
        Convert this YearAgeRate object to a dict of node_id: MortalityDistribution entries.

        The method assumes that the user wants the data in a step-wise format.  That is, for a
        calendar year range and age range, the user wants EMOD to produce the same value/rate
        for the entire range.  The rate doesn't change until the year or age moves to a new range.

        For the max age of the last bin, a value of 125 is used and, for the max_year of the last bin,
        a value of 2100 is used.  Using these maximums still produces the correct values because we
        want the result constant for the entire range.  Having the range wider just produces
        the same constant.

        Args:
            stepwise_for_year:
                If true, the age and calendar year both in step-wise format.  If false, calendar year
                is adjust by 2.5 and the linear interpolation will be used between calendar years.
        """
        mortality_distributions = {}

        node_group_collection = self.df.groupby(YearAgeRate.COL_NAME_NODE_ID)
        for node_id, node_group in node_group_collection:
            # TODO: we should be creating and returning distribution objects in this call, not json/converting below
            #  https://github.com/InstituteforDiseaseModeling/emodpy-hiv-old/issues/316
            dist_dict = YearAgeRate._node_group_to_distribution_json(node_group,stepwise_for_year=stepwise_for_year)
            dist_dict["ResultUnits"] = "annual death rate for an individual"

            distribution = MortalityDistribution.from_dict(distribution_dict=dist_dict)
            mortality_distributions[node_id] = distribution

        return mortality_distributions


def plot(year_age_rate_list: List[YearAgeRate],
         title: str = None,
         node_id: int = 0,
         img_dir: str = None,
         filename_to_save_to: str = None):
    """
    Create a plot window with one subplot for each min_age value and where the subplot
    will has min_year on the x-axis and "rate" on the y-axis.  Each YearAgeRate object
    in the 'year_age_rate_list' will have one curve on each subplot

    Args:
        year_age_rate_list: A list of YearAgeRate objects that have same min_age values
            for all min_year values.  The min_year values do not need to be the same,
            just the min_ages.

        title:
            The title of the plot window.

        node_id:
            Data will be extracted from the YearAgeRate objects for this node.

        img_dir: If this is defined, the images are saved to this directory.  If not defined,
            the images are displayed in a window.

        filename_to_save_to: The name of the file to save the image to.  This is only used if
            img_dir is defined.
    """
    from math import sqrt, ceil
    import matplotlib.pyplot as plt

    def getColor(idx):
        colors = ['r', 'b', 'g', 'c', 'm', 'y', 'k']
        return colors[idx % len(colors)]

    def get_line_style(idx):
        ls_list = ["-", "--", ":", "-."]
        return ls_list[idx % len(ls_list)]

    if img_dir:
        plt.figure(figsize=(15, 10))

    min_age_list = year_age_rate_list[0].df[YearAgeRate.COL_NAME_MIN_AGE].unique().tolist()
    num_sub_plots_total = len(min_age_list)
    num_sub_plots_x = ceil(sqrt(num_sub_plots_total))
    num_sub_plots_y = ceil(float(num_sub_plots_total) / float(num_sub_plots_x))

    i_sub_plot = 0
    for min_age in min_age_list:
        sub_plot_ix = i_sub_plot % num_sub_plots_x
        sub_plot_iy = int(i_sub_plot / num_sub_plots_x)
        sub_plot = plt.subplot2grid((num_sub_plots_y, num_sub_plots_x), (sub_plot_iy, sub_plot_ix))

        i_yar = 0
        for yar in year_age_rate_list:
            node_df = yar.df[yar.df[YearAgeRate.COL_NAME_NODE_ID] == node_id]
            min_age_df = node_df[node_df[YearAgeRate.COL_NAME_MIN_AGE] == min_age]

            x = min_age_df[YearAgeRate.COL_NAME_MIN_YEAR].tolist()
            y = min_age_df[YearAgeRate.COL_NAME_RATE    ].tolist() # Noqa: E202

            color = getColor(i_yar)
            ls = get_line_style(i_yar)
            sub_plot.plot(x, y, color, linewidth=2, linestyle=ls)
            plt.setp(sub_plot.get_xticklabels(), fontsize='7')
            plt.title(str(min_age), fontsize='9')

            i_yar += 1
        i_sub_plot += 1

    if title is None:
        title = "Data for Node=" + str(node_id)
    plt.suptitle(title)

    plt.subplots_adjust(left=0.04, right=0.99, bottom=0.02, top=0.9, wspace=0.3, hspace=0.3)

    if img_dir:
        import os
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        if filename_to_save_to is None:
            filename_to_save_to = "YearAgeRate.png"
        fn = os.path.join(img_dir, filename_to_save_to)
        print(fn)
        plt.savefig(fn, dpi=300)
    else:
        plt.show()
    plt.close()
