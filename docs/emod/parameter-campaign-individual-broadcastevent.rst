==============
BroadcastEvent
==============

The **BroadcastEvent** intervention class is an individual-level class that immediately broadcasts
the event trigger you specify. This campaign event is typically used with other classes that monitor
for a broadcast event, such as :doc:`parameter-campaign-node-nodelevelhealthtriggerediv` or
:doc:`parameter-campaign-event-communityhealthworkereventcoordinator`.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-broadcastevent.csv

.. literalinclude:: ../json/campaign-broadcastevent.json
   :language: json

