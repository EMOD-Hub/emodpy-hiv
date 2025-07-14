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
- [Community](#community)
- [FAQ](#faq)
- [Support and Contributions](#support)
- [Disclaimer](#disclaimer)

<a id="documentation"></a>
# Documentation

The emodpy-hiv code is intended to be self-documenting in order to keep the documentation fully up-to-date with the 
particular installed version. Additional documentation is available at:
https://docs.idmod.org/projects/emodpy-hiv/en/latest/

To build the documentation locally, do the following:

1. Create and activate a venv.
2. Navigate to the root directory of the repo and enter the following

    ```
    pip install -e .
    cd docs
    pip install -r requirements.txt
    make html
    ```

<a id="installation"></a>
# Installation

<a id="software-prerequisites"></a>
## Software Prerequisites
- Python 3.9.X x64
- Please ensure pip is updated as default-installed pip with python 3.9 is outdated:
```
python -m pip install --upgrade pip
```

<a id="install"></a>
## Install
```
python -m pip install emodpy-hiv --extra-index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

<a id="training-resources"></a>
# Training Resources

Tutorial Python code can be found in the [tutorials](tutorials) directory.


<a id="faq"></a>
# FAQ

Frequently asked questions are answered in https://docs.idmod.org/projects/emodpy-hiv/en/latest/faq.html.

<a id="community"></a>
# Community

The EMOD Community is made up of researchers and software developers, primarily focused on malaria and HIV research.
We value mutual respect, openness, and a collaborative spirit. If these values resonate with you, 
we invite you to join our EMOD Slack Community by completing this form:

https://forms.office.com/r/sjncGvBjvZ

<a id="support"></a>
# Support and contributions

The code in this repository was developed by IDM to support our research in disease
transmission and managing epidemics. We’ve made it publicly available under the MIT
License to provide others with a better understanding of our research and an opportunity
to build upon it for their own work. We make no representations that the code works as
intended or that we will provide support, address issues that are found, or accept pull
requests. You are welcome to create your own fork and modify the code to suit your own
modeling needs as contemplated under the MIT License.

If you have feature requests, issues, or new code, please see our
'CONTRIBUTING <https://github.com/EMOD-Hub/emodpy-hiv/blob/main/CONTRIBUTING.rst>' page
for how to provide your feedback.

Questions or comments can be directed to [idmsupport@gatesfoundation.org](<mailto:idmsupport@gatesfoundation.org>).

<a id="disclaimer"></a>
# Disclaimer

The code in this repository was developed by IDM and other collaborators to support our joint research on flexible agent-based modeling.
 We've made it publicly available under the MIT License to provide others with a better understanding of our research and an opportunity to build upon it for 
 their own work. We make no representations that the code works as intended or that we will provide support, address issues that are found, or accept pull requests.
 You are welcome to create your own fork and modify the code to suit your own modeling needs as permitted under the MIT License.

