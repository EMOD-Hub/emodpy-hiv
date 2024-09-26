==================
MigrateIndividuals
==================

The **MigrateIndividuals** intervention class is an individual-level intervention used to force
migration and is separate from the normal migration system. However, it does require that human
migration is enabled by setting the configuration parameters **Migration_Model** to
FIXED_RATE_MIGRATION and **Migration_Pattern** to SINGLE_ROUND_TRIP.

As individuals migrate, there are three ways to categorize nodes:

* Home: the node where the individuals reside; each individual has a single home node.
* Origin: the "starting point" node for each leg of the migration. The origin updates as individuals
  move between nodes.
* Destination: the node the individual is traveling to. The destination updates as individuals move
  between nodes.

For example, Individual 1 has a home node of Node A. They migrate from Node A to Node B. Node A is
both the home node and the origin node, and Node B is the destination node. If Individual 1 migrates
from Node B to Node C, Node A remains the home node, but now Node B is the origin node, and Node C
is the destination node. If Individual 1 migrates from Node C back to Node A, Node C is the origin
node, and Node A becomes the destination node and still remains the home node.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-migrateindividuals.csv

.. literalinclude:: ../json/campaign-migrateindividuals.json
   :language: json