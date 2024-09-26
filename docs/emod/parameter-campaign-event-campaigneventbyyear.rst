===================
CampaignEventByYear
===================

The **CampaignEventByYear** event class determines when to distribute the intervention based on the
calendar year. See the following JSON example and table, which shows all available parameters for this
campaign event.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-campaigneventbyyear.csv


.. literalinclude:: ../json/campaign-campaigneventbyyear.json
   :language: json


Nodeset_Config classes
======================

The following classes determine in which nodes the event will occur.

NodeSetAll
----------

The event will occur in all nodes in the simulation. This class has no associated parameters. For example,

.. code-block:: json

    {
        "Nodeset_Config": {
            "class": "NodeSetAll"
        }
    }


NodeSetNodeList
---------------

The event will occur in the nodes listed by Node ID.

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-nodesetnodelist.csv

NodeSetPolygon
--------------

The event will occur in the nodes that fall within a given polygon.

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-nodesetpolygon.csv
