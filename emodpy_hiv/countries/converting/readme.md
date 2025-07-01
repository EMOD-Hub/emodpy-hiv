# How to compare your new demographics data versus the old

Overview
- Collect old files
- Reformat old files
- Generate new files in old format
- Diff reformated old files against new files in old format


1) Create directory with your old files:
- Demographics.json
- PFA_Overlay.json
- Accessibility_and_Risk_IP_Overlay.json
- Risk_Assortivity_Overlay.json

2) Use the reformat_json.py script to put the JSON into a format that will be easier
to compare against (i.e. indents as spaces, keys sorted, numbers rounded to 9-digits, etc.).
You want these reformated files in a directory that you can "diff" against the new files.

python -m emodpy_hiv.countries.converting.reformat_json <current_filename> <new_filename>

You will need to do this for each file.  It is suggested that the "new_filename" the same name
plus a suffix at most.

3) Use the new_demographics_old_format.py script to create the demographics data for your
country but put in a format similar to the old format.  That is, instead of having one file,
it will create the four files with the same names as above.  You will want these files to be
in a new directory and with the same names as the old files you reformatted.

python -m emodpy_hiv.countries.converting.new_demographics_old_format -c <country> -o <output_dir>

4) Use a diff'ing tool like WinMerge to compare the four files.  You will see some differences,
but the trick is to look for those differences that matter.  For example, you might see
"0" vs "0.0" or "0.588563" vs "0.588562".  The main goal is to see what values are different
and to adjust your new demographics to match.


