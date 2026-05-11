import os
import shutil
import emod_hiv.bootstrap as emod_hiv

current_directory = os.path.dirname(os.path.realpath(__file__))


failed_tests = os.path.join(current_directory, "failed_tests")

sif_path = os.path.join(current_directory, "stage_sif.id")

#inputs_folder = os.path.join(current_directory, "inputs")
#input_files_folder = os.path.join(inputs_folder, "input_files")

executables_dir = os.path.join(current_directory, "executables")
schema_path = os.path.join(executables_dir, "schema.json")
eradication_path = os.path.join(executables_dir, "Eradication")

# create the executables folder if it doesn't exist, extract the binaries and schema files
if not os.path.isdir(executables_dir):
    os.mkdir(executables_dir)

# get all the Eradication binaries and schema files
if not os.path.isfile(eradication_path):
    emod_hiv.setup(executables_dir)

# Running things
comps_platform_name = "SLURMStage"  # "Calculon" or "SLURMStage"

container_platform_name = "Container"
plat_image = "ghcr.io/emod-hub/emod-ubuntu-runtime:latest"

x_Base_Population_scale = 0.5  # run tutorial tests at half population for speed
