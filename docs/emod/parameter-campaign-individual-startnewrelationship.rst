====================
StartNewRelationship
====================

The **StartNewRelationship** intervention class provides a method of triggering the formation of 
a relationship following a user-specified event. The parameters of the relationship that is formed can 
also be customized by the user, such as individual properties required of the partner, or modified 
condom usage probability within the relationship. Note: These new relationships can be made by people of 
any age (the intervention disregards **IsPostDebut** and **Sexual_Debut_Age_Min**). Additionally, these 
relationships are considered outside of the Pair Formation Algorithm (PFA), and do not impact/are not impacted 
by concurrency or pair formation parameters. Coital act and condom usage rate are as per the corresponding 
relationship type, unless modified by the user.


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-startnewrelationship.csv

.. literalinclude:: ../json/campaign-startnewrelationship.json
   :language: json