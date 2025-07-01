# a simple script to backout the source csv data for mortality and fertility distributions in an EMOD demographics json

import json

import pandas as pd
from pathlib import Path

FERTILITY = 'fertility'
MORTALITY = 'mortality'
ALLOWED_DATA_TYPES = [FERTILITY, MORTALITY]


# is_even = lambda value: value % 2 == 0
def is_even(value):
    return value % 2 == 0


# is_odd = lambda value: not is_even(value)
def is_odd(value):
    return not is_even(value)


def parse_fertility_data(source_file: str, country: str = 'Zambia--json_parsed', year_bin_size: int = 5) -> pd.DataFrame:
    with open(source_file, 'rb') as f:
        data = json.load(f)
    data = data['Defaults']['IndividualAttributes']['FertilityDistribution']
    raw_ages = data['PopulationGroups'][0]
    raw_years = data['PopulationGroups'][1]

    # process the ages; assume they are 'doubled' e.g. 15 & 19.99 (with identical data), so we keep half of them
    ages = [age for index, age in enumerate(raw_ages) if is_even(index)]  # keep index 0, 2, 4, ...  # TODO: ages looks correct for min_age in a bin
    age_ranges = [f'{ages[index-1]}-{ages[index]-1}' for index in range(1, len(ages))]
    # this is missing the FINAL range, so we add it on manually
    age_ranges.append(f'{ages[-1]}-{ages[-1]+5-1}')  # TODO: this assumes 5-year age bins (creating the last one)

    # We will assume the year-data is stair-stepped (meaning: we will skip every-other year when parsing data)
    # Process the year range entry. Assuming year_bin_size-year bins, STARTING on the recorded year (of the kept
    #  year duplicates
    periods = []
    min_years = [raw_years[year] for year in range(0, len(raw_years), 2)]
    for min_year in min_years:
        max_year = min_year + year_bin_size  # e.g. 15-20, 20-25, ... if year_bin_size is 5
        periods.append(f"{min_year}-{max_year}")

    # here we pare down the fertility data to match the expected shape (assumptions above)
    fertility_values = data['ResultValues']
    fertility_values = [[fertility_values[age_index][year_index]
                         for year_index in range(0, len(fertility_values[age_index]), 2)]
                        for age_index in range(0, len(fertility_values), 2)]

    data_rows_by_period = {}
    for age_index in range(len(fertility_values)):
        fertilities_for_this_age = fertility_values[age_index]

        # fertility files have a column per period instead of a row per period (like mortality distributions)
        for year_index, fertility in enumerate(fertilities_for_this_age):
            # create a new row if needed
            period = periods[year_index]
            if period not in data_rows_by_period:
                data_rows_by_period[period] = {'Country': country, 'Years': period}
            data_row = data_rows_by_period[period]

            # now extend the data row with the current age binned fertility data
            data_row[age_ranges[age_index]] = fertility
    df = pd.DataFrame(data_rows_by_period.values())
    return df


def parse_mortality_data(source_file: str, gender: str, year_bin_size: int = 5) -> pd.DataFrame:
    with open(source_file, 'rb') as f:
        data = json.load(f)
    data = data['Defaults']['IndividualAttributes'][f"MortalityDistribution{gender}"]
    raw_ages = data['PopulationGroups'][0]
    raw_years = data['PopulationGroups'][1]

    # process the ages; assume they are 'doubled' e.g. 15 & 19.99 (with identical data), so we keep half of them
    ages = [age for index, age in enumerate(raw_ages) if is_even(index)]  # keep index 0, 2, 4, ...
    age_intervals = [ages[index] - ages[index - 1] for index in range(1, len(ages))]
    # this is missing the FINAL interval, so we add it on manually
    age_intervals.append(raw_ages[-1] - raw_ages[-2])

    # process the year range entry. Assuming year_bin_size-year bins, centered on the recorded year.
    periods = []
    for raw_year in raw_years:
        # min_year = year_bin_size * math.floor(raw_year/year_bin_size)
        # max_year = year_bin_size * math.ceil(raw_year/year_bin_size)
        min_year = round(raw_year - year_bin_size / 2)
        max_year = round(raw_year + year_bin_size / 2)
        periods.append(f"{min_year}-{max_year}")

    # TODO: assume raw_ages length is even and that every pair forms an output age (with identical mortality data),
    #  hence we read every-other 'age row' to skip the presumed duplicate.

    # here we pare down the mortality data to match the expected shape (assumptions above)
    mortality_values = data['ResultValues']
    mortality_values = [mortality_values[age_index] for age_index in range(0, len(mortality_values), 2)]

    data_rows = []
    for age_index in range(len(mortality_values)):
        # if is_odd(age_index):
        #     continue
        mortalities_for_this_age = mortality_values[age_index]
        for year_index, mortality in enumerate(mortalities_for_this_age):
            data_row = {
                'Period': periods[year_index],
                'Age (x)': ages[age_index],
                'Age interval (n)': age_intervals[age_index],
                'Central death rate m(x,n)': mortality
            }
            data_rows.append(data_row)
    df = pd.DataFrame(data_rows)
    return df


def main(args):
    if args.data_type not in ALLOWED_DATA_TYPES:
        raise Exception(f"{args.data_type} is not one of the allowed data types to extract: {str(ALLOWED_DATA_TYPES)}")
    if args.data_type == FERTILITY:
        df = parse_fertility_data(source_file=args.source_file)

        output_dir = Path(args.output_file).absolute().parent
        Path(output_dir).absolute().mkdir(parents=True, exist_ok=True)

        df.to_csv(args.output_file, index=False)
        print(f'wrote file: {args.output_file}')
    elif args.data_type == MORTALITY:
        df_male = parse_mortality_data(source_file=args.source_file, gender='Male')
        df_female = parse_mortality_data(source_file=args.source_file, gender='Female')

        output_dir = Path(args.output_file).absolute().parent
        Path(output_dir).absolute().mkdir(parents=True, exist_ok=True)

        output_file = Path(output_dir, Path(args.output_file).stem + '--male.csv')
        df_male.to_csv(output_file, index=False)
        print(f'wrote file: {output_file}')

        output_file = Path(output_dir, Path(args.output_file).stem + '--female.csv')
        df_female.to_csv(output_file, index=False)
        print(f'wrote file: {output_file}')


def parse_args():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--file', dest='source_file', type=str, required=True,
                        help="EMOD demographics json file to read data from. Required.")
    parser.add_argument('-t', '--type', dest='data_type', type=str, required=True,
                        help="Data to extract, one of: {str(ALLOWED_DATA_TYPES)}. Required.")
    parser.add_argument('-o', '--output', dest='output_file', type=str, required=True,
                        help="Data csv file path to write results to. Required.")

    args = parser.parse_args()
    return args


# if __name__ == "__main__":
#     args = parse_args()
#     main(args=args)
