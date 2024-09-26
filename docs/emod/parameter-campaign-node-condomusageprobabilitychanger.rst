=============================
CondomUsageProbabilityChanger
=============================

The **CondomUsageProbabilityChanger** node intervention class allows the user to change 
the probability that a condom would be used during a coital act for a particular relationship 
type in a node. This intervention overrides the **Condom_Usage_Probablility** Sigmoid in the 
:doc:`software-demographics` that typically determines this probability. Note, this intervention 
does not expire; it causes an existing intervention to be removed. Hence, to reset the parameter, 
the user should submit a second intervention with the original value. This change impacts the 
relationships one time step after it was distributed.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-condomusageprobabilitychanger.csv

.. literalinclude:: ../json/campaign-condomusageprobablitychanger.json
   :language: json