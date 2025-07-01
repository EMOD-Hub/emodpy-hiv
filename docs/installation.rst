=======
Install
=======

Follow the steps below to install |EMODPY_hiv|.

Prerequisites
=============

First, ensure the following prerequisites are met.

* Windows 10 Pro or Enterprise, Linux, or Mac

* |Python_supp| (https://www.python.org/downloads/release)

* A file that indicates the pip index-url:
    
    * For Windows, in C:\\Users\\Username\\pip\\pip.ini add the following::

        [global]
        index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

    * For Linux, in $HOME/.config/pip/pip.conf add the following::

        [global]
        index-url = https://packages.idmod.org/api/pypi/pypi-production/simple

Installation instructions
=========================

#.  Open a command prompt and create a virtual environment in any directory you choose. The
    command below names the environment "v-emodpy-hiv", but you may use any desired name::

        python -m venv v-emodpy-hiv

#.  Activate the virtual environment:

    * For Windows, enter the following::

        v-emodpy-hiv\Scripts\activate

    * For Linux, enter the following::

        source v-emodpy-hiv/bin/activate


#.  Install |EMODPY_hiv| packages::

        pip install emodpy-hiv

    If you are on Linux, also run::

        pip install keyrings.alt

#.  When you are finished, deactivate the virtual environment by entering the following at a command prompt::

        deactivate
