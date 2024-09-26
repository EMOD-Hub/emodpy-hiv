=================
ControlledVaccine
=================

The **ControlledVaccine** intervention class is a subclass of :doc:`parameter-campaign-individual-simplevaccine`
so it contains all functionality of **SimpleVaccine**, but provides more control over
additional events and event triggers. This intervention can be configured so that specific events
are broadcast when individuals receive an intervention or when the intervention expires. Further,
individuals can be re-vaccinated, using a configurable wait time between vaccinations.

Note that one of the controls of this intervention is to not allow a person to receive an additional
dose if they received a dose within a certain amount of time. This applies only to **ControlledVaccine**
interventions with the same **Intervention_Name**, so people can be given multiple vaccines as long
as each vaccine has a different value for **Intervention_Name**.


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-controlledvaccine.csv

.. literalinclude:: ../json/campaign-controlledvaccine.json
   :language: json
