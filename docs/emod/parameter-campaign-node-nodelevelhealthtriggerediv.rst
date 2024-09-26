==========================
NodeLevelHealthTriggeredIV
==========================

The **NodeLevelHealthTriggeredIV** intervention class is a node-level intervention that distributes
an intervention to individuals when a specific event occurs to those individuals.
**NodeLevelHealthTriggeredIV** monitors for event triggers from individuals, and when found, will
distribute the intervention. For example, **NodeLevelHealthTriggeredIV** can be configured such that
all individuals will be given a diagnostic intervention when they transition from susceptible to
infectious. During the simulation, when individuals become infected, they broadcast the
**NewInfectionEvent** trigger and **NodeLevelHealthTriggeredIV** distributes the diagnostic
intervention to them.

Notes and tips for this intervention:

*  This is the main tool for distributing an intervention to a person when an event happens to that person.
   Note that the intervention is distributed to *all* individuals in the node which experience the triggering event.
*  This is a node-level intervention and is not serialized. If interventions were distributed prior to
   serialization, in order to have those interventions continue after starting from the serialized file, they
   must be added to the new campaign file.
*  This can be used to distribute other node-level interventions. For example, it can be used to
   distribute SpaceSpraying to the node when someone becomes infected (e.g. by listening for for
   NewInfectionEvent or an event from a diagnostic).
*  A powerful feature of this intervention is that it can target specific groups of individuals who
   broadcast the event. Individuals, and subgroups of individuals, can be targeted by age, gender, and Individual Property.
*  Note that when distributing a node-level intervention parameters associated with targeting an
   individual (such as **Target_Demographic**, **Target_Gender**, **Property_Restriction_Within_Node**,
   etc.) do not apply.
*  **Blackout_Period** is a feature that can be useful when monitoring an event from the individual
   in a node. It enables reaction to some individuals experiencing an event but ignoring subsequent
   events for a period of time. For example, **SpaceSpraying** could be distributed to the node on the
   first occurrence of NewInfectionEvent, but after spraying has occurred all other infection events
   can be ignored for a specific period of time. Without **Blackout_Period**, each infection event
   would trigger another round of spraying.
*  The **Distribute_On_Return_Home** feature causes **NodeLevelHealthTriggeredIV** to keep track of
   residents when they leave the node and then return. If a person leaves the node and an intervention
   is distributed while the person is gone, **NodeLevelHealthTriggeredIV** gives the person the
   intervention (such as a vaccine dose) when they return to the node.


.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-nodelevelhealthtriggerediv.csv

.. literalinclude:: ../json/campaign-nodelevelhealthtriggerediv.json
   :language: json