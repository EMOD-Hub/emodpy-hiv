==============================
InterventionForCurrentPartners
==============================

The **InterventionForCurrentPartners** intervention class provides a mechanism for the partners of
individuals in the care system to also seek care. Partners do not need to seek testing at the same
time; a delay may occur between the initial test and the partner's test. If a relationship has been
paused, such as when a partner migrates to a different node, the partner will not be contacted.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-interventionforcurrentpartners.csv

.. literalinclude:: ../json/campaign-interventionforcurrentpartners.json
   :language: json