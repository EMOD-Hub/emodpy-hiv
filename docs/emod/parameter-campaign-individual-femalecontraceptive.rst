===================
FemaleContraceptive
===================

The **FemaleContraceptive** intervention is used to reduce the fertility rate of females of 
reproductive age (14 to 45 years old), based on a distribution set by the user. This intervention 
can only be distributed to females, and ignores the waning condition expiration (as women could still 
use a contraceptive, even if it is ineffective). Note: the **Birth_Rate_Dependence** configuration parameter 
must be set to INDIVIDUAL_PREGNANCIES or INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR or an error will result.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-femalecontraceptive.csv

.. literalinclude:: ../json/campaign-femalecontraceptive.json
   :language: json