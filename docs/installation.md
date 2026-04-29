# Install

Follow the steps below to install emodpy-hiv.

## Prerequisites

First, ensure the following prerequisites are met.

* Windows 10 Pro or Enterprise, Linux, or Mac

* Python 3.13 64-bit (https://www.python.org/downloads/release)

## Installation instructions

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-emodpy-hiv", but you may use any desired name::

        python -m venv v-emodpy-hiv

#.  Activate the virtual environment:

    * For Windows, enter the following::

        v-emodpy-hiv\Scripts\activate

    * For Linux, enter the following::

        source v-emodpy-hiv/bin/activate

#.  Install emodpy-hiv packages::

        pip install emodpy-hiv

    If you are on Linux, also run::

        pip install keyrings.alt

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
