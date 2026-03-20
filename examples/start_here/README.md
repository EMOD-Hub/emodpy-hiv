# HIV Example Scenario

These instructions have been tested on Windows, Mac, and Linux. There are a few variations per platform but not everything will be called out here in the interest of brevity.
Linux and Mac users will almost certainly be typing 'python3' and 'pip3' in all places where you see 'python' or 'pip' below.

## ALWAYS
- Open a terminal/shell/console.
- Make sure you are running Python3.6.2 or later.

```
python --version
```
- Make sure you have your COMPS creds.

## Environment Prep
1. Create virtual environment (e.g., python -m venv emodpy)
2. Activate virtual environment: run 'emodpy/bin/activate'
3. Update to the latest pip if prompted.
```
pip install pip --upgrade
```

## Installation
```
pip install emodpy-hiv
pip install keyrings.alt (Linux only)
git clone https://github.com/EMOD-Hub/emodpy-hiv.git
cd emodpy-hiv/examples/start_here
pip install eradicationpy
python -m eradicationpy.bootstrap
```

## Run
```
python example_pip_install_Eradication.py
```
(Enter necessary creds as prompted.)

## Study
Observe results on COMPS
