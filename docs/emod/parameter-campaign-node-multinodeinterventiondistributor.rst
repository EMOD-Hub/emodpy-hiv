================================
MultiNodeInterventionDistributor
================================

The **MultiNodeInterventionDistributor** intervention class is a node-level intervention that
distributes multiple other node-level  interventions when the distributor only allows specifying one
intervention. This class can be thought of as an "adapter," where it can adapt interventions or
coordinators that were designed to distribute one intervention to instead distribute many.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-multinodeinterventiondistributor.csv

.. literalinclude:: ../json/campaign-multinodeinterventiondistributor.json
   :language: json