================================
RelationshipFormationRateChanger
================================

The **RelationshipFormationRateChanger** node intervention class allows the user to change 
the rate at which relationships form in a node. This allows the user to model, for example, how 
an education program or other intervention causes people to reduce the number of relationships they create. 
This intervention overrides the **Formation_Rate_Constant** value in the Demographics file that 
typically determines this rate (**Formation_Rate_Type** is assumed to be 'CONSTANT'). 
Note, this intervention does not expire; it causes an existing intervention to be removed. Hence, to reset the 
parameter, the user should submit a second intervention with the original value. This change impacts the 
relationships one time step after it was distributed.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-relationshipformationratechanger.csv

.. literalinclude:: ../json/campaign-relationshipformationratechanger.json
   :language: json