===========================
RelationshipDurationChanger
===========================

The **RelationshipDurationChanger** node intervention class allows the user to change 
the duration of relationships of a particular type in a node. This allows the user to model, 
for example, how an education program or other intervention could cause a change in people's behavior. 
This intervention overrides the **Duration_Weibull_Heterogeneity** and **Duration_Weibull_Scale** 
values in the :doc:`software-demographics` that typically determine duration for each relationship type. Note, this 
intervention does not expire; it causes an existing intervention to be removed. Hence, to reset the 
parameter, the user should submit a second intervention with the original value. This change impacts the 
relationships one time step after it was distributed.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-relationshipdurationchanger.csv

.. literalinclude:: ../json/campaign-relationshipdurationchanger.json
   :language: json