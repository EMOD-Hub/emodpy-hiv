# emodpy-hiv
Python module for use as user-space front-end for doing research easily with EMOD (HIV_SIM) via idmtools


## Description

This package provides a Python scriptable interface for configuring EMOD for HIV modeling. This Python interface abstracts the process of creating JSON formatted files for parameter specification, demographics specification and intervention specification along as well as abstracting the process of creating binary climate and migration files.

## Get `emodpy-hiv`

The `emodpy-hiv` package (and its supporting packages) is currently hosted on IDM's Python package repository.

```shell
python3 -m pip install emodpy-hiv --index-url=https://packages.idmod.org/api/pypi/pypi-production/simple
```

Note: you may need to only use `python` on Windows machines rather than `python3`.

## Documentation

Documentation for both the EMOD HIV model and the emodpy-hiv package is available 
at https://docs.idmod.org/projects/emodpy-hiv/en/latest/.

To build the documentation locally, do the following:

1. Create and activate a venv.
2. Navigate to the root directory of the repo and enter the following

    ```
    pip install -r requirements.txt
    cd docs
    pip install -r requirements.txt
    cd ..
    pip install -e .
    cd docs
    make html
    ```

## FAQ

Frequently asked questions are answered in https://docs.idmod.org/projects/emodpy-hiv/en/latest/faq.html.

## Community

The EMOD Community is made up of researchers and software developers, primarily focused on malaria and HIV research.
We value mutual respect, openness, and a collaborative spirit. If these values resonate with you, 
we invite you to join our EMOD Slack Community by completing this form:

https://forms.office.com/r/sjncGvBjvZ

## Support and contributions

The code in this repository was developed by IDM to support our research in disease
transmission and managing epidemics. We’ve made it publicly available under the MIT
License to provide others with a better understanding of our research and an opportunity
to build upon it for their own work. We make no representations that the code works as
intended or that we will provide support, address issues that are found, or accept pull
requests. You are welcome to create your own fork and modify the code to suit your own
modeling needs as contemplated under the MIT License.

If you have feature requests, issues, or new code, please see our
'CONTRIBUTING <https://github.com/InstituteforDiseaseModeling/emodpy-hiv/blob/main/CONTRIBUTING.rst>' page
for how to provide your feedback.

Questions or comments can be directed to [idmsupport@gatesfoundation.org](<mailto:idmsupport@gatesfoundation.org>).

# Disclaimer

The code in this repository was developed by IDM and other collaborators to support our joint research on flexible agent-based modeling.
 We've made it publicly available under the MIT License to provide others with a better understanding of our research and an opportunity to build upon it for 
 their own work. We make no representations that the code works as intended or that we will provide support, address issues that are found, or accept pull requests.
 You are welcome to create your own fork and modify the code to suit your own modeling needs as permitted under the MIT License.

