=========================
MultiEffectBoosterVaccine
=========================

The **MultiEffectBoosterVaccine** intervention class is derived from
:doc:`parameter-campaign-individual-multieffectvaccine` and preserves many of the same parameters.
Upon distribution and successful take, the vaccine’s effect in each immunity compartment
(acquisition, transmission,  and mortality) is determined by the recipient’s immune state. If the
recipient’s immunity modifier in the corresponding compartment is above a user-specified threshold,
then the vaccine’s initial effect will be equal to the corresponding priming parameter. If the
recipient’s immune modifier is below this threshold, then the vaccine’s initial effect will be equal
to the corresponding boost parameter. After distribution, the effect wanes, just like a
**MultiEffectVaccine**. The behavior is intended to mimic biological priming and boosting.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-multieffectboostervaccine.csv

.. literalinclude:: ../json/campaign-multieffectboostervaccine.json
   :language: json