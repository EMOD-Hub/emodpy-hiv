=============
MigrateFamily
=============

The **MigrateFamily** intervention class tells family groups of residents of the targeted node to go
on a round trip migration ("family trip"). The duration of time residents wait before migration and
the time spent at the destination node can be configured; the pre-migration waiting timer does not
start until all residents are at the :term:`home node`.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-migratefamily.csv

.. literalinclude:: ../json/campaign-migratefamily.json
   :language: json