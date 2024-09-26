================
SimpleDiagnostic
================

The **SimpleDiagnostic** intervention class identifies infected individuals, regardless of disease state, based on specified diagnostic sensitivity and specificity. Diagnostics are a key component of modern disease control efforts, whether used to identify high-risk individuals, infected individuals, or drug resistance. This intervention class distributes a specified intervention to a fraction of individuals who test positive.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-simplediagnostic.csv

.. literalinclude:: ../json/campaign-simplediagnostic.json
   :language: json