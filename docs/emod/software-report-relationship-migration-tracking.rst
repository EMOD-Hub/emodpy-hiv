===================================
ReportRelationshipMigrationTracking
===================================

The relationship migration tracking report (ReportRelationshipMigrationTracking.csv) provides information about the relationships a person has when they are migrating. It will give information when they are leaving and entering a node. When leaving a node, the information will be about the status of the relationships just before they leave. When entering the new node, the information will be about the relationships that have been updated. For example, a person could leave with a relationship paused, find their partner in the new node, and get their relationship back to normal. This helps to know about how the status of the relationships have changed—migrated, paused, or terminated.

The person initiating a migration event will first have their relationships listed in the state before migrating starts. If a partner is asked to migrate with them, then that partner's relationships will also be listed. When the people are immigrating into the new node, the list of relationships that are continuing in the new node will be listed. Any migrated partner should only have the relationship with the partner initiating migration. Their other relationships will have been terminated.



Configuration
=============

To generate this report, the following parameters must be configured in the custom_reports.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Filename_Suffix, string, NA, NA, \"\", "Augments the filename of the report. If multiple reports are being generated, this allows you to distinguish among the multiple reports."
    Start_Year, float, 1900, 2200, 1900, "Simulation time in years to start collecting data, including fractions of years. For example, 2025.0 means January 1st, 2025."
    End_Year, float, 1900, 2200, 2200, "Simulation time in years to stop collecting data, including fractions of years. For example, 2025.0 means January 1st, 2025."
    Node_IDs_Of_Interest, array, 0, 2.14748e+09, [], "Data will be collected for the nodes in this list. Leave the array empty (default value) to include all nodes."
    Min_Age_Years, float, 0, 9.3228e+35, 0, "Minimum age in years of people to collect data on."
    Max_Age_Years, float, 0, 9.3228e+35, 9.3228e+35, "Maximum age in years of people to collect data on."
    Must_Have_IP_Key_Value, string, NA, NA, \"\", "A Key:Value pair that the individual must have in order to be included. Leave the string empty (default value) to not look at individual properties. For more information, see :doc:`model-properties`."
    Must_Have_Intervention, string, NA, NA, \"\", "The name of an intervention that the person must have in order to be included. Leave the string empty (default value) to not look at the interventions. For more information, see :doc:`parameter-campaign-individual-interventions`."



.. code-block:: json

    {
        "Reports": [
            {
                "Filename_Suffix": "example",
                "Start_Year": 1900,
                "End_Year": 2200,
                "Node_IDs_Of_Interest":[ 1, 2, 3 ],
                "Min_Age_Years": 20,
                "Max_Age_Years": 90,
                "Must_Have_IP_Key_Value": "",
                "Must_Have_Intervention": "",
                "class": "ReportRelationshipMigrationTracking"
            }
        ],
        "Use_Defaults": 1
    }



Output file data
================

The output report will contain the following information.


Data columns
------------

.. csv-table::
    :header: Parameter, Data type, Description
    :widths: 8, 5, 20

    Time, float, "The simulation time of the migration event—emigrating or immigrating."
    Year, float, "The simulation time of the migration event in years."
    IndividualID, integer, "The unique ID of the migrating individual."
    AgeYears, float, "The age in years of the migrating individual."
    Gender, string, "The gender of the individual. Possible values are ""M"" or ""F."""
    From_NodeID, string, "The external ID of the node the individual is moving from."
    To_NodeID, string, "The external ID of the node the individual is moving to, as defined in the demographics. This can be zero when the person has immigrated into the destination node."
    MigrationType, enum, "The type of migration that is occurring at the time of the triggering event (see the Event column). If the triggering event is SimulationEnd, possible MigrationType values are either ""home"" or ""away,"" indicating if the individual was in their home node or not when the simulation ended. For all other events, the possible values are: air, local, sea, or regional."
    Event, enum, "The event triggering the migration information to be reported. Possible values are: STIPreEmigrating, STIPostImmigrating, NonDiseaseDeaths, DiseaseDeaths. Emigrating means the individual is moving, SimulationEnd means the simulation has finished. One row of data will be recorded for each event."
    IsInfected, boolean, "Describes whether or not the individual is infected: 0 for not infected, 1 for infected."
    Rel_ID, integer, "The unique ID of the relationship that is migrating."
    NumCoitalActs, integer, "The total number of coital acts this couple has had within this relationship up to this time."
    IsDiscordant, boolean, "Describes whether or not both individuals in a relationship are infected: 0 indicates that the partners are either both infected or both uninfected, 1 indicates that one of the partners is infected and the other is not."
    HasMigrated, boolean, "0 indicates false, 1 indicates that the person identified by IndividualID has completed migrating. Will be true when the event is STIPostImmigrating."
    RelationshipType, enum, "The type of relationship whose information is being added to the report. Options are: TRANSITORY, INFORMAL, MARITAL, COMMERCIAL."
    RelationshipState, enum, "The state of the relationship. Possible values are:

    NORMAL
        Both partners are in the same node and can have coital acts.

    MIGRATING
        The partners are migrating together to a new node.

    PAUSED
        One of the partners is not in the same node so the couple will pause their coital acts.

    TERMINATED
        This is when the relationship ends. This value is unlikely to be seen in this report."
    PartnerID, integer, "The unique ID of the partner in the relationship with that of IndividualID."
    Male_NodeID, integer, "The node that the male of the relationship is in. If the value is zero, then IndividualID is a female and the male's location is unknown. The relationship will be in the PAUSE state."
    Female_NodeID, integer, "The node that the female of the relationship is in. If the value is zero, then IndividualID is a male and the female's location is unknown. The relationship will be in the PAUSE state."


Example
=======

The following is an example of a ReportRelationshipMigrationTracking.csv file.


.. csv-table::
    :header: Time, Year, IndividualID, AgeYears, Gender, From_NodeID, To_NodeID, MigrationType, Event, IsInfected, Rel_ID, NumCoitalActs, IsDiscordant, HasMigrated, RelationshipType, RelationshipState, PartnerID, Male_NodeID, Female_NodeID
    :file: ReportRelationshipMigrationTracking-Example.csv

