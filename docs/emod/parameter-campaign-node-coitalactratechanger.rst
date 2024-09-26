====================
CoitalActRateChanger
====================

The **CoitalActRateChanger** node intervention class allows the user to change 
the coital act rate for a particular relationship type in a node. This allows the 
user to model, for example, how an education program or other intervention might reduce 
the number of coital acts individuals have. This intervention overrides the 
**Coital_Act_Rate** value in the :doc:`software-demographics` that typically determines this rate. 
Note, this intervention does not expire; it causes an existing intervention to be removed. 
Hence, to reset the parameter, the user should submit a second intervention with the original 
value. This change impacts the relationships one time step after it was distributed.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-coitalactratechanger.csv

.. literalinclude:: ../json/campaign-coitalactratechanger.json
   :language: json