=========================
AntiretroviralTherapyFull
=========================

The **AntriretroviralTherapyFull** intervention class begins antiretroviral therapy (ART) 
on the person receiving the intervention. This class is similar to the standard 
**AntiretroviralTherapy**, but enhances it with two key features: 1) a built-in delay 
timer such that when the delay expires, the person will come off of ART (**ARTDropout** 
should NOT be used with this intervention), and 2) persistance with the individual so the 
user can track this intervention using **ReferenceTrackingEventCoordinator**. 

.. include:: ../reuse/ART-usage-notes.txt

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-antiretroviraltherapyfull.csv

.. literalinclude:: ../json/campaign-antiretroviraltherapyfull.json
   :language: json
