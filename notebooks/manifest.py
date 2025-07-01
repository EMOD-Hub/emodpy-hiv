import os

#
# This is a user-modifiable Python file designed to be a set of simple input
# file and directory settings that you can choose and change.
#

# === Directory for Executables ===
# This folder will contain your Eradication binary, schema, SIF files and other
# things that you might need to run EMOD.
executables_dir="executables"

# === Singularity Image ===
# COMPS - the location of the file containing AssetCollection id for the dtk sif
sif_path = os.path.join(executables_dir, "dtk_sif.id")
# SLURM_LOCAL - BigPurple - Full path to the SIF file
#sif_path = "/gpfs/data/bershteynlab/EMOD/singularity_images/centos_dtk-build.sif"

# === Schema ===
# The script is going to use this to store the downloaded schema file.
# Create 'download' directory or change to your preferred (existing) location.
schema_file = os.path.join(executables_dir, "schema.json")

# === Executable ===
# The script is going to use this to store the downloaded Eradication binary.
# Create 'download' directory or change to your preferred (existing) location.
eradication_path = os.path.join(executables_dir, "Eradication")

# === Assets ===
# Create 'Assets' directory or change to a path you prefer.
# idmtools will upload files found here.
assets_input_dir = "Assets"

# === Embedded Python Scripts ===
# This is a location for EMOD embedded python scripts.  Scripts included
# here will be included in your simulation directory so that EMOD
# can use them during the simulation.
embedded_python_scripts_path = "embedded_python"
