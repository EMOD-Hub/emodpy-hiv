====================
CoitalActRiskFactors
====================

The **CoitalActRiskFactors** intervention class provides a method of modifying an individual's 
risk/probability of acquiring or transmitting an STI. If other risk multipliers are active (across other interventions), 
the values will be multiplied together; the resulting value will be multiplied with any active 
STI co-infection factors. When the intervention expires, the individual's risk factor multiplier returns 
to one. Since this intervention persists, it can be used with a reference tracking event coordinator (see 
:doc:`parameter-campaign-event-coordinators` for details).

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-coitalactriskfactors.csv

.. literalinclude:: ../json/campaign-coitalactriskfactors.json
   :language: json