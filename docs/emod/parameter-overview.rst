============================
|EMOD_s| parameter reference
============================

The configurable parameters described in this reference section determine the behavior of a
particular simulation and interventions. The parameter descriptions are intended to guide you in
correctly configuring simulations to match your disease scenario of interest.

This reference section contains only the parameters supported for use with the HIV simulation
type. To see the parameters for a different simulation type, see the corresponding
documentation.

These parameters include three major groups: parameters for the :term:`demographics file`,
parameters for the :term:`configuration file`, and parameters for the :term:`campaign file`.


If you would rather use a text file for parameter reference than this web documentation, you can
also generate a :term:`schema` with the |exe_l| that defines all configuration and campaign
parameters that can be used in a simulation, including names, data types, defaults, ranges, and
short descriptions.


JSON formatting overview
========================

All of these parameters are contained in :term:`JSON (JavaScript Object Notation)` formatted files.
JSON is a data format that is human-readable and easy for software to read and generate. It
can be created and edited using a simple text editor.

JSON has two basic structures: a collection of key-value pairs or an ordered list of values (an
array). These structures are within a JSON object, which is enclosed in a set of braces. You
will notice that each of these files begins with a left brace ({) and ends with a right brace
(}).

A value can be a string, number, Boolean, array, or an object. The campaign and data input files
often use nested objects and arrays. See www.json.org_ for more information on JSON.

.. _www.json.org: http://www.json.org

A few important details to call out when creating JSON files:

* Add a comma after every key-value pair or array except for the last key-value pair in an array or object.
* The keys (parameters) are case-sensitive. For example, "NodeID" is not the same as "NodeId".
* Decimals require a 0 (zero) before the decimal point.
* |EMOD_s| does not support Booleans ("True", "False"). Instead, |EMOD_s| use the integer 1 for "True" and 0 for "False".
* Every opening curly brace or square bracket ({ or [) requires a corresponding closing brace or bracket (} or ]).

The following is an example of a JSON formatted file.

.. code-block:: json

    {
        "A_Complex_Key": {
            "An_Array_with_a_Nested_Object_Value": [
                {
                    "A_Simple_Key": "Value",
                    "A_Simple_Array": [ "Value1", "Value2" ],
                    "An_Array_with_Number_Values": [ 0.1, 0.2 ],
                    "A_Nested_Object": {
                        "Another_Simple_Key": "Value",
                        "Nested_Arrays": [
                            [ 10, 0.1 ],
                            [ 0.1, 1 ]
                        ]
                    }
                }
            ]
        }
    }

JSON resources
==============

The website https://jsonlint.com provides validation of JSON formatting. This can be very helpful in
identifying missing commas, unbalanced curly braces, missing quotation marks, and other common JSON
syntax errors. Another helpful site is http://jsondiff.com/, which highlights differences between
two uploaded JSON files.

.. toctree::
   :maxdepth: 2
   :titlesonly:

   parameter-demographics
   parameter-configuration
   parameter-campaign
   parameter-schema
   software-outputs

