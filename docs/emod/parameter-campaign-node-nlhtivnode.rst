==========
NLHTIVNode
==========

The **NLHTIVNode** intervention class distributes node-level interventions to nodes when a specific
user-defined node event occurs. For example, **NLHTIVNode** can be configured to have
**SurveillanceEventCoordinator** set to listen for **NewInfectionEvents**, and then broadcast a
node event when a certain number of events is reached, such as distributing **IndoorSpaceSpraying**
to a node with a high number of new infections.

**NLHTIVNode** is similar to :doc:`parameter-campaign-node-nodelevelhealthtriggerediv` but **NLHTIVNode**
is focused on *node* interventions and events while **NodeLevelHealthTriggeredIV** is focused on
*individual* interventions and events.



.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-nlhtivnode.csv

.. literalinclude:: ../json/campaign-nlhtivnode.json
   :language: json