import os
import json
from typing import Union
from pathlib import Path


def format_sort_round_json(current_filename: Union[str, Path],
                           new_filename: Union[str, Path]):
    """
    A function that takes a JSON file and reformats it to be sorted and rounded to 9 digits.
    This is helpful when comparing the new and old models. The function will create a new file.

    Args:
        current_filename (str or Path):
            The name of the JSON file to be converted.

        new_filename (str or Path):
            The name of the new JSON file to be created.
    """
    if os.path.exists(new_filename):
        ValueError(f"File {new_filename} already exists. Please delete it before running this function.")
    if not os.path.exists(current_filename):
        raise ValueError(f"File {current_filename} does not exist. Please check the file path.")

    tmp_json = None
    with open(current_filename, 'r') as file:
        tmp_json = json.load(file)

    with open(new_filename, "w") as file:
        # This process of writing and reading and writing allows us to write a file where
        # the floating point values are rounded to 9 digits. This helps us not have rounding
        # issues between different platforms.
        tmp_json = json.dumps(tmp_json, indent=4, sort_keys=True)
        tmp_json = json.loads(tmp_json, parse_float=lambda x: round(float(x), 9))
        json.dump(tmp_json, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('current_filename', type=str, default=None, help='The name of the JSON file to be converted.')
    parser.add_argument('new_filename', type=str, default=None, help='The name of the new JSON file to be created.')

    args = parser.parse_args()

    format_sort_round_json(args.current_filename, args.new_filename)
