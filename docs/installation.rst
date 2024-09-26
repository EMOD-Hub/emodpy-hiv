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


.. toctree::
    :titlesonly:

    emod/install-overview
    installation-py