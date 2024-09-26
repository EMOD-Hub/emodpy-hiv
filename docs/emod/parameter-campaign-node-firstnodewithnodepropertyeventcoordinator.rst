=========================================
FirstNodeWithNodePropertyEventCoordinator
=========================================

The **FirstNodeWithNodePropertyEventCoordinator** coordinator class screens for
a desired node property (NP) and then broadcasts a coordinator event when found. When this 
event coordinator is triggered to start, it goes through the provided list of nodes and checks 
the NPs of each. (The nodes in the provided list must be defined in the CampaignEvent's **Nodeset_Config** 
parameter.) Once a node is found with the desired NP, the coordinator event is broadcast. An additional 
coordinator event can be broadcast if the desired NP is NOT found.


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-firstnodewithnodepropertyeventcoordinator.csv

.. literalinclude:: ../json/campaign-firstnodewithnodepropertyeventcoordinator.json
   :language: json
