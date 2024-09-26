import setuptools
import sys
import version

with open('requirements.txt') as requirements_file:
    lines = requirements_file.read().strip().split("\n")
requirements = []
arguments = []
develop_install = 'develop' in sys.argv
for line in lines:
    if line[0] == '-':
        # we have a flag to handle on the command line
        arguments.extend(line.split(' '))
    else:
        # we have an actual package requirement
        requirements.append(line)
if develop_install:
    sys.argv.extend(arguments)
    # for some reason, things are installed in reverse requirements.txt order
    requirements.reverse()

with open("README.md", "r") as fh:
    long_description = fh.read()
    ext_name = "emodpy_hiv"

setuptools.setup(
    name=ext_name,
    version=version.__version__,
    author="Clark Kirkman IV",
    author_email="ckirkman@idmod.org",
    description="IDM's HIV-specific EMOD-API binding code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstituteforDiseaseModeling/emodpy-hiv",
    packages=setuptools.find_packages(exclude=['*tests*', '*notebooks*', '*tutorials*', '*examples*']),
    package_data={'emodpy_hiv.country_data': ['**/*.csv']},
    exclude_package_data={'': ['tests', 'notebooks', 'tutorials', 'examples']},
    setup_requires=['wheel'],
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
