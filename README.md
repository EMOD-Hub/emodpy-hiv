# emodpy-hiv
emodpy-hiv is an extension to emodpy that contains HIV-specific campaign, demographics, and reporting classes for 
configuring EMOD-HIV simulations. Standard country-specific configurations are wrapped into "country model" classes, 
providing easily accessible, modifiable, and consistent starting points for new projects. HIV-specific plotting tools 
are also provided to aid in exploring model output.

### Table of Contents

- [Documentation](#documentation)
- [Installation](#installation)
  - [Software Prerequisites](#software-prerequisites)
  - [Install](#install)
- [Training Resources](#training-resources)
- [Support and Contributions](#support)
- [Disclaimer](#disclaimer)

<a id="documentation"></a>
# Documentation

The emodpy-hiv code is intended to be self-documenting in order to keep the documentation fully up-to-date with the 
particular installed version. Additional documentation is available at the [emodpy-hiv documentation](https://emod-hub.github.io/emodpy-hiv/).

To build the documentation locally, do the following:

1. Create and activate a venv.
2. Navigate to the root directory of the repo and enter the following

    ```
    python -m pip install .[docs]
	python -m sphinx -T --keep-going -b html ./docs ./site
    ```

<a id="installation"></a>
# Installation

<a id="software-prerequisites"></a>
## Software Prerequisites
- Python 3.13.X x64 (also supports Python 3.11-3.14)
- Please ensure pip is updated:
```
python -m pip install --upgrade pip
```

<a id="install"></a>
## Install
```
python -m pip install emodpy-hiv
```

<a id="training-resources"></a>
# Training Resources

Tutorial Python code can be found in the [tutorials](tutorials) directory.


<a id="support"></a>
# Support and Contributions

The code in this repository was developed by IDM to support our research in disease
transmission and managing epidemics. We’ve made it publicly available under the MIT
License to provide others with a better understanding of our research and an opportunity
to build upon it for their own work. We make no representations that the code works as
intended or that we will provide support, address issues that are found, or accept pull
requests. You are welcome to create your own fork and modify the code to suit your own
modeling needs as contemplated under the MIT License.

If you have feature requests, issues, or new code, please see our
[CONTRIBUTING](https://github.com/EMOD-Hub/emodpy-hiv/blob/main/CONTRIBUTING.rst) page for how to provide your feedback.

Questions or comments are welcome in [Discussions](https://github.com/orgs/EMOD-Hub/discussions).

<a id="disclaimer"></a>
# Disclaimer

The code in this repository was developed by IDM and other collaborators to support our joint research on flexible agent-based modeling.
 We've made it publicly available under the MIT License to provide others with a better understanding of our research and an opportunity to build upon it for 
 their own work. We make no representations that the code works as intended or that we will provide support, address issues that are found, or accept pull requests.
 You are welcome to create your own fork and modify the code to suit your own modeling needs as permitted under the MIT License.

