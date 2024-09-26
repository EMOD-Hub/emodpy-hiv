===============
Output settings
===============

.. include:: ../reuse/config-output.txt


The following figures are examples for the parameter **Report_HIV_Period**.

When **Report_HIV_Period** is set to a value that is less than the **Simulation_Timestep**, a record
will be written during the next time step after the reported period. More than  one period may occur
before the next time step.

.. figure:: ../images/hiv/Report_HIV_Period-timeline-example1.png

   Figure 1: **Report_HIV_Period < **Simulation_Timestep**


When **Report_HIV_Period** is greater than **Simulation_Timestep**, a record will be written during
the next time step after the period occurs. This means that a record may not be written at all time
steps.

.. figure:: ../images/hiv/Report_HIV_Period-timeline-example2.png

   Figure 2: **Report_HIV_Period > **Simulation_Timestep**


.. include:: ../reuse/warning-case.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/config-output-configfile-hiv.csv
