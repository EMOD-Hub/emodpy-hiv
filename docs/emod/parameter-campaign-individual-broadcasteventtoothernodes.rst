==========================
BroadcastEventToOtherNodes
==========================

The **BroadcastEventToOtherNodes** intervention class allows events to be sent from one node to
another. For example, if an individual in one node has been diagnosed, drugs may be
distributed to individuals in surrounding nodes.

When this intervention is updated, the event to be broadcast is cached to be distributed to the
nodes. After the people have migrated, the event information is distributed to the nodes (i.e. it
does support multi-core). During the next time step, the nodes will update their node-level
interventions and then broadcast the events from other nodes to ALL the people in the node. This is
different from interventions that only broadcast the event in the current node for the person
who had the intervention. Distances between nodes use the Longitude and Latitude defined in the
demographics file, and use the Haversine Formula for calculating the great-circle distance.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-broadcasteventtoothernodes.csv

.. literalinclude:: ../json/campaign-broadcasteventtoothernodes.json
   :language: json
