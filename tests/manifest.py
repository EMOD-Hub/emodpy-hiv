import os
import shutil
import emod_hiv.bootstrap as emod_hiv

current_directory = os.path.dirname(os.path.realpath(__file__))


failed_tests = os.path.join(current_directory, "failed_tests")

sif_path = os.path.join(current_directory, "stage_sif.id")

#inputs_folder = os.path.join(current_directory, "inputs")
#input_files_folder = os.path.join(inputs_folder, "input_files")

package_folder = os.path.join(current_directory, "download")
schema_path = os.path.join(package_folder, "schema.json")
eradication_path = os.path.join(package_folder, "Eradication")

# create the package folders if they don't exist, extract the binaries and schema files
if not os.path.isdir(package_folder):
    os.mkdir(package_folder)

# get all the Eradication binaries and schema files
if not os.path.isfile(eradication_path):
    emod_hiv.setup(package_folder)

# Running things
comps_platform_name = "SLURMStage"  # "Calculon" or "SLURMStage"
comps_node_group = "idm_48cores"  # for Calculon
comps_priority = "Lowest"  # for Calculon



