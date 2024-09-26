=====================================
IndividualNonDiseaseDeathRateModifier
=====================================

The **IndividualNonDiseaseDeathRateModifier** intervention class provides a method of modifying 
an individual's non-disease mortality rate over time, until an expiration event is reached. For example, 
this intervention could be given to people who have access to health care to model that 
they have a different life expectancy than those who do not. Different distribution patterns 
can be designated, and linear interpolation will be used to calculate values between time points.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-individualnondiseasedeathratemodifier.csv

.. literalinclude:: ../json/campaign-individualnondiseasedeathratemodifier.json
   :language: json