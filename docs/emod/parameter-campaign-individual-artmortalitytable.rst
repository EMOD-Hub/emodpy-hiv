=================
ARTMortalityTable
=================

The **ARTMortalityTable** intervention class allows the user to modify an individual’s life expectancy 
based on different levels of ART adherence; the user defines parameters for age, CD4 count, and time on ART 
in a multi-dimensional table which is then used to determine mortality rate. Note: If you have have different adherence levels for each gender, then you will need to configure your campaign to distribute an **ARTMortalityTable** for each gender and adherence level.

.. include:: ../reuse/ART-usage-notes.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-artmortalitytable.csv

.. literalinclude:: ../json/campaign-artmortalitytable.json
   :language: json