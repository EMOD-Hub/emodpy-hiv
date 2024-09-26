=============================================================
Generate a list of all available parameters (a schema)
=============================================================

You can generate a :term:`schema` from the |exe_l| or |linux_binary| that defines all configuration
parameters and campaign parameters available in the version of |EMOD_s| that is installed, for all
available simulation types. This includes parameter names, data types, defaults, ranges, and short
descriptions. The schema does not include demographics parameters.

Logging information is also produced as part of the schema. If you are using |EMOD_s| source and have
added or modified configuration parameters or intervention code, this logging information can help
you troubleshoot any errors that may occur.

.. include:: ../reuse/warning-schema.txt

Command options
===============

The following command-line options are available for providing information about |EMOD_s|.

.. csv-table:: |EMOD_s| information commands
   :header: "Long form", "Short form", "Description"
   :widths: 2,1,10

   ``--help``, ``-help``, "Shows help options for |exe_s|."
   ``--version``, ``-v``, "Shows the version information and supported simulation types. Note capitalization of short alternative."
   ``--get-schema``, ``--get-schema``, "Outputs the configuration and campaign parameters. Unless ``--schema-path`` or a redirect operator is used, the schema will print to the Command Prompt window."
   ``--schema-path``, ``>``, "When used with ``--get-schema``, if a TXT or JSON file is specified, the schema information will be written to the file instead of the Command Prompt window."

Usage
=====

#.  Open a Command Prompt window and navigate to the directory where |exe_s| is installed.
#.  To output the schema to the Command Prompt window, enter::

        Eradication.exe --get-schema

#.  To output the schema to a file, do one of the following (replacing <filename> with the
    desired filename):

    *   To output a text file that includes logging information, enter::

            Eradication.exe --get-schema > <filename>.txt

    *   To display logging in the Command Prompt window and output a text file
        that does not include logging information, enter::

            Eradication.exe --get-schema --schema-path <filename>.txt

    *   To output the schema to a JSON file that includes logging information, enter::

            Eradication.exe --get-schema > <filename>.json

    *   To display logging in the Command Prompt window and output a JSON file
        that does not include logging information, enter::

            Eradication.exe --get-schema --schema-path <filename>.json
