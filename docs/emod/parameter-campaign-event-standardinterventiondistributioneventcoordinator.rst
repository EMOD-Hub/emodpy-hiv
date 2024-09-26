================================================
StandardInterventionDistributionEventCoordinator
================================================

The **StandardInterventionDistributionEventCoordinator** coordinator class distributes an individual-level or
node-level intervention to a specified fraction of individuals or nodes within a node set. Recurring
campaigns can be created by specifying the number of times distributions should occur and the time
between repetitions. 

Demographic restrictions such as **Demographic_Coverage** and **Target_Gender** do not apply when
distributing node-level interventions. The node-level intervention must handle the demographic
restrictions.

See the following JSON example and table, which shows all available parameters
for this event coordinator.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-standardinterventiondistributioneventcoordinator.csv

.. literalinclude:: ../json/campaign-standardinterventiondistributioneventcoordinator.json
   :language: json

