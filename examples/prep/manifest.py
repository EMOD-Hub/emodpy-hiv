import os

my_ep4_assets=None
schema_file="stash/schema.json"
eradication_path="stash/Eradication"
assets_input_dir="Assets"
plugins_folder="stash"

with open(os.path.join('..', 'image_name')) as fid01:
    image_str = fid01.readlines()[0].strip()

plat_name = "Container"
job_dir = "../example_jobs"
plat_image = image_str
