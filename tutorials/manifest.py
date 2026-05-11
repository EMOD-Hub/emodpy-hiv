import os

# === Tutorials Directory ===
tutorials_dir = os.path.dirname(__file__)

# === Directory for Executables ===
# This folder will contain your Eradication binary, schema, SIF files and other
# things that you might need to run EMOD.
executables_dir = os.path.join(tutorials_dir, "executables")

# === Singularity Image ===
# COMPS - the location of the file containing AssetCollection id for the dtk sif
comps_sif_path = os.path.join(tutorials_dir, "comps_sif_file.id")
# SLURM_LOCAL - BigPurple - Full path to the SIF file
slurm_sif_path = "/gpfs/data/bershteynlab/EMOD/singularity_images/centos_dtk-build.sif"

# === Schema ===
# The script is going to use this to store the downloaded schema file.
# Create 'download' directory or change to your preferred (existing) location.
schema_path = os.path.join(executables_dir, "schema.json")

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

# === Container Platform ===
plat_image = "ghcr.io/emod-hub/emod-ubuntu-runtime:latest"

# === Simulation Scale ===
# Scale factor applied to x_Base_Population in run_experiment(). Default 1.0 (no change).
# Set to a smaller value (e.g. 0.5) to run faster simulations during testing.
x_Base_Population_scale = 1.0
