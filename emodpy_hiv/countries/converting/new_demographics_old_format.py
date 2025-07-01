import json
from pathlib import Path
from typing import Union

import emodpy_hiv.country_model as country_model


def _reduce_to_population_only(demog_json):
    """
    Reduce the demographics json to only include the population parameters.
    This is used to create the Demographics.json file.
    """
    del demog_json["Defaults"]["Society"]
    for node in demog_json["Nodes"]:
        del node["IndividualProperties"]
        del node["Society"]
    return demog_json


def _reduce_to_ip_only(demog_json):
    """
    Reduce the demographics json to only include the IndividualProperties
    parameters.  This is used to create the Accessibility_and_Risk_IP_Overlay.json file.
    """
    del demog_json["Defaults"]["Society"]
    del demog_json["Defaults"]["IndividualAttributes"]
    del demog_json["Defaults"]["NodeAttributes"]
    for node in demog_json["Nodes"]:
        new_ips = []
        for ip_name in ["Accessibility", "Risk", "CascadeState"]:
            for ip in node["IndividualProperties"]:
                if ip["Property"] == ip_name:
                    new_ips.append(ip)
        node["IndividualProperties"] = new_ips
        del node["Society"]
        del node["IndividualAttributes"]
        del node["NodeAttributes"]
    return demog_json


def _reduce_to_society_only(demog_json):
    """
    Reduce the demographics json to only include the Society parameters minus
    the Concurrency_Configuration and Relationship_Parameters.
    This is used to create the PFA_Overlay.json file.
    """
    from emodpy_hiv.utils.emod_enum import RelationshipType
    del demog_json["Defaults"]["IndividualAttributes"]
    del demog_json["Defaults"]["IndividualProperties"]
    del demog_json["Defaults"]["NodeAttributes"]
    for rel_type in RelationshipType:
        if rel_type == RelationshipType.COUNT:
            continue
        demog_json["Defaults"]["Society"][rel_type.value]["Pair_Formation_Parameters"]["Assortivity"] = {"Group": "NO_GROUP"}
        del demog_json["Defaults"]["Society"][rel_type.value]["Relationship_Parameters"]

    for node in demog_json["Nodes"]:
        del node["IndividualAttributes"]
        del node["IndividualProperties"]
        del node["NodeAttributes"]
        del node["Society"]["Concurrency_Configuration"]
    return demog_json


def _reduce_to_assortivity_only(demog_json):
    """
    Reduce the demographics json to only include the Assortivity parameter/matrix
    that is part of the Pair_Formation_Parameters.  This used  to be the old
    Risk_Assortivity_Overlay.json file.
    """
    from emodpy_hiv.utils.emod_enum import RelationshipType
    del demog_json["Defaults"]["IndividualAttributes"]
    del demog_json["Defaults"]["IndividualProperties"]
    del demog_json["Defaults"]["NodeAttributes"]
    del demog_json["Defaults"]["Society"]["Concurrency_Configuration"]
    for rel_type in RelationshipType:
        if rel_type == RelationshipType.COUNT:
            continue
        assortivity = demog_json["Defaults"]["Society"][rel_type.value]["Pair_Formation_Parameters"]["Assortivity"]
        del demog_json["Defaults"]["Society"][rel_type.value]["Pair_Formation_Parameters"]
        demog_json["Defaults"]["Society"][rel_type.value]["Pair_Formation_Parameters"] = {}
        demog_json["Defaults"]["Society"][rel_type.value]["Pair_Formation_Parameters"]["Assortivity"] = assortivity
        del demog_json["Defaults"]["Society"][rel_type.value]["Concurrency_Parameters"]
        del demog_json["Defaults"]["Society"][rel_type.value]["Relationship_Parameters"]

    for node in demog_json["Nodes"]:
        del node["IndividualAttributes"]
        del node["IndividualProperties"]
        del node["NodeAttributes"]
        del node["Society"]["Concurrency_Configuration"]
        for rel_type in RelationshipType:
            if rel_type == RelationshipType.COUNT:
                continue
            del node["Society"][rel_type]["Relationship_Parameters"]
    return demog_json


OLD_FILENAMES = [
    "Demographics",
    "PFA_Overlay",
    "Accessibility_and_Risk_IP_Overlay",
    "Risk_Assortivity_Overlay"
]


def get_old_demographic_filenames(add_extension: bool = True):
    filenames = OLD_FILENAMES.copy()
    if add_extension:
        for name in filenames:
            name = name + ".json"
    return filenames


def create_old_demographic_files(country_name: str,
                                 output_dir: Union[str, Path] = None,
                                 suffix: str = None):
    """
    A function that outputs the demographics files for the Zambia model in the old format
    of four overlay files: Demographics.json, PFA_Overlay.json, Accessibility_and_Risk_IP_Overlay.json,
    Risk_Assortivity_Overlay.json. The files are created in the output_dir directory.  This can be
    helpful wnen comparing the new and old models.

    Args:
        output_dir (str or Path)
            The directory where the files will be created. If None, the current
            directory will be used.

        suffix (str):
            A suffix to add to the file names. If None, no suffix will be added.
    """
    if country_name is None:
        raise ValueError("You must specify a country to create the demographics for.")

    country_class = country_model.get_country_class(country_class_name=country_name)

    if output_dir is None:
        output_dir = "."

    reduce_list = ["population", "ip", "society", "assortivity"]
    for reduce in reduce_list:
        demog = country_class.build_demographics()
        demog_json = demog.to_dict()
        reduced_fn = None
        if reduce == "population":
            demog_json = _reduce_to_population_only(demog_json=demog_json)
            reduced_fn = OLD_FILENAMES[0]
        elif reduce == "society":
            demog_json = _reduce_to_society_only(demog_json=demog_json)
            reduced_fn = OLD_FILENAMES[1]
        elif reduce == "ip":
            demog_json = _reduce_to_ip_only(demog_json=demog_json)
            reduced_fn = OLD_FILENAMES[2]
        elif reduce == "assortivity":
            demog_json = _reduce_to_assortivity_only(demog_json=demog_json)
            reduced_fn = OLD_FILENAMES[3]

        if suffix is not None:
            reduced_fn = reduced_fn + "_" + suffix

        tmp_filename = Path(output_dir).joinpath(reduced_fn + ".json")

        with open(tmp_filename, "w") as file:
            tmp = json.dumps(demog_json, indent=4, sort_keys=True)
            tmp = json.loads(tmp, parse_float=lambda x: round(float(x), 9))
            json.dump(tmp, file, indent=4, sort_keys=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--country', type=str, default=None, help='The country class to create the demographics for.')
    parser.add_argument('-o', '--output', type=str, default=None, help='A directory to save the default demographics data to in the old set of four overlay files format.')
    parser.add_argument('-s', '--suffix', type=str, default=None, help='A short string to append to the output file names.')

    args = parser.parse_args()

    create_old_demographic_files(args.country, args.output, args.suffix)
