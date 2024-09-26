=================
RelationshipStart
=================

The relationship formation report (RelationshipStart.csv)  provides information about each relationship
and its members, evaluated at the time of relationship formation. The report includes the relationship
type, start time, scheduled end time, and detailed information about each participant: ID, gender, age,
infection status, circumcision status for males, co-infections, number of relationships (active, recent,
lifetime), and individual properties. The male in the relationship is indicated on the report as participant
"A", and the female as participant "B".



Configuration
=============

To generate the report, the following parameters must be configured in the config.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Report_Relationship_Start, boolean, NA, NA, 0, "Set this to 1 to generate the report."
    Report_Relationship_Start_Start_Year, float, 1900, 2200, 1900, "Simulation time in years to start collecting data."
    Report_Relationship_Start_End_Year, float, 1900, 2200, 2200, "Simulation time in years to stop collecting data."
    Report_Relationship_Start_Max_Age_Years, float, 0, 9.3228e+35, 9.3228e+35, "The age that of one of the partners must be less than or equal to for the relationship to be reported."
    Report_Relationship_Start_Min_Age_Years, float, 0, 9.3228e+35, 0, "The age that of one of the partners must be greater than or equal to for the relationship to be reported."
    Report_Relationship_Start_Node_IDs_Of_Interest, array, 0, 2.14748e+09, [], "Data will be collected for the nodes in this list."
    Report_Relationship_Start_Include_HIV_Disease_Statistics, boolean, NA, NA, 1, "When set to 1, the report will include information
    on CD4 count, viral load, disease stage, HIV positivity, and HIV testing results for each partner in the relationship."
    Report_Relationship_Start_Include_Other_Relationship_Statistics, boolean, NA, NA, 1, "When set to 1, the report will include
    information on the number of active and lifetime relationships of each type (Transitory, Informal,
    Marital, and Commercial) for each partner in the relationship, as well as total relationships in the
    past six month and total lifetime relationships. Additionally, a bitmask column will indicate which
    types of concurrent relationships are allowed; these are configured using the **Concurrency_Configuration** parameter in the demographics file—see :doc:`parameter-demographics` for more information."
    Report_Relationship_Start_Individual_Properties, array of strings, NA, NA, [], "A list of individual property (IP) keys that will
    be included in the report as applicable to each partner at the start of the relationship. One column will be added to the report for each partner, for each key in the list. Specify the IP keys by adding an **IndividualProperties** parameter in the demographics file. See :doc:`model-properties` for details on setting individual properties."
    Report_Relationship_Start_Must_Have_IP_Key_Value, string, NA, NA, \"\", "A Key:Value pair that one of the partners must have for the relationship to be reported. Empty string means don't look at individual properties. For more information, see :doc:`model-properties`."
    Report_Relationship_Start_Must_Have_Intervention, string, NA, NA, \"\", "The name of an intervention that the one of the partners must have in order for the relationship to be reported. Empty string means don't look at the interventions. For more information, see :doc:`parameter-campaign-individual-interventions`."


.. code-block:: json

    {
        "Report_Relationship_Start": 1,
        "Report_Relationship_Start_Start_Year": 1900,
        "Report_Relationship_Start_End_Year": 2200,
        "Report_Relationship_Start_Max_Age_Years": 60,
        "Report_Relationship_Start_Min_Age_Years": 20,
        "Report_Relationship_Start_Node_IDs_Of_Interest": [ 1, 2, 3 ],
        "Report_Relationship_Start_Include_Other_Relationship_Statistics": 1,
        "Report_Relationship_Start_Individual_Properties": ["InterventionStatus"],
        "Report_Relationship_Start_Must_Have_IP_Key_Value": "Risk:HIGH",
        "Report_Relationship_Start_Must_Have_Intervention": "",
    }



Output file data
================

The output report will contain the following information.

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20


    Rel_ID, integer, "A unique identifier for the relationship, different from the IDs of the participants."
    Rel_start_time, float, "The time (in days) during the simulation when the relationship started."
    Rel_scheduled_end_time, float, "The time (in days) during the simulation when the relationship was scheduled to end. The duration of the relationship is dependent on the relationship type; configure by updating the **Duration_Weibull_Heterogeneity** and **Duration_Weibull_Scale** parameters in the demographics file. See :doc:`parameter-demographics` for details."
    "Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)", integer, "The type of relationship between individuals A and B. Values for 0-3 as indicated in the header."
    Is_rel_outside_PFA, character, "Indicates whether or not the relationship was created by the normal process using the Pair Forming Algorithm (PFA), where ""F"" indicates the relationship was created using the PFA, and ""T"" indicates the relationship was created using the **StartNewRelationship** intervention."
    Original_node_ID, integer, "The ID of the node where the relationship started."
    Current_node_ID, integer, "The ID of the node where the participants currently reside."
    "<A or B>_ID", integer, "The unique numerical identifier for the individual.  There is a column for each partner."
    "<A or B>_is_infected", boolean, "Indicates whether or not the individual is infected: 0 for not infected, 1 for infected. There is a column for each partner."
    "<A or B>_gender", boolean, "The gender of the individual: 0 is for male, 1 is for female. There is a column for each partner."
    "<A or B>_age", float, "The age of the individual in years. There is a column for each partner."
    "<A or B>_IP=<'IP_Key'>", depends on IP key, "For each individual property key in the **Report_Relationship_Start_Individual_Properties** parameter list, a column will be added. The value will be the value for the IP key that this partner has at this time. There is a column for each partner. See `Configuration`_ for additional details on designating the IP keys."
    "<A or B>_total_num_active_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of active relationships the individual is currently in. There is a column for each partner."
    "<A or B>_num_active_TRANSITORY_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of transitory relationships the individual is currently in. There is a column for each partner."
    "<A or B>_num_active_INFORMAL_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of informal relationships the individual is currently in. There is a column for each partner."
    "<A or B>_num_active_MARITAL_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of marital relationships the individual is currently in. There is a column for each partner."
    "<A or B>_num_active_COMMERCIAL_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of commercial relationships the individual is currently in. There is a column for each partner."
    "<A or B>_num_lifetime_rels", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of relationships the individual has had during their lifetime. There is a column for each partner."
    "<A or B>_num_rels_last_6_mo", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating the total number of relationships the individual has had in the last six months. There is a column for each partner."
    "<A or B>_extra_relational_bitmask", integer, "If the **Report_Relationship_Start_Include_Other_Relationship_Statistics** parameter is set to 1, this column will be included, indicating which types of relationships that individual is allowed to have when they have more than one active relationship. These values are configured using the **Concurrency_Configuration** parameter in the demographics file—see :doc:`parameter-demographics` for more information. These values can be updated when an individual migrates or has a value change in an individual property. The values are encoded in a 3-digit bitmask. In order, the digits correspond to Commercial (C), Marital (M), Informal (I), and Transitory (T) relationships. The following table provides example combinations:

    .. list-table::
        :header-rows: 1

        * - Relationships allowed
          - Binary
          - Decimal Value
        * - None
          - 0000
          - 0
        * - T
          - 0001
          - 1
        * - I
          - 0010
          - 2
        * - I, T
          - 0011
          - 3
        * - M
          - 0100
          - 4
        * - M, T
          - 0101
          - 5
        * - M, I
          - 0110
          - 6
        * - M, I, T
          - 0111
          - 7
        * - C
          - 1000
          - 8
        * - C, T
          - 1001
          - 9
        * - C, I
          - 1010
          - 10
        * - C, I, T
          - 1011
          - 11
        * - C, M
          - 1100
          - 12
        * - C, M, T
          - 1101
          - 13
        * - C, M, I
          - 1110
          - 14
        * - C, M, I, T
          - 1111
          - 15
    "
    "<A or B>_is_circumcised", boolean, "Indicates whether or not the individual is circumcised: 0 for not circumcised, 1 for circumcised. There is a column for each partner."
    "<A or B>_has_STI_coinfection", boolean, "Indicates whether or not the individual has an STI co-infection: 0 if they do not have an STI co-infection, 1 if they do have an STI co-infection. There is a column for each partner."
    "<A or B>_is_superspreader", boolean, "Indicates whether or not the individual is a super-spreader: 0 if they are not a super-spreader, 1 if they are a super-spreader. This status is configured using the **Probability_Person_Is_Behavioral_Super_Spreader** parameter in the demographics file—see :doc:`parameter-demographics` for more information. There is a column for each partner."
    "<A or B>_CD4_count", float, "If the **Report_Relationship_Start_Include_HIV_Disease_Statistics** parameter is set to 1, this column will be included, indicating the CD4 count for each partner. There is a column for each partner. Note: this is only included in HIV simulations."
    "<A or B>_viral_load", float, "This channel is not currently supported. If the **Include_HIV_Disease_Statistics** parameter is set to 1, this column will be included, where -1 indicates that the partner is not infected, 1000 indicates that the partner is infected. There is a column for each partner. Note: this is only included in HIV simulations."
    "<A or B>_HIV_disease_stage", float, "If the **Report_Relationship_Start_Include_HIV_Disease_Statistics** parameter is set to 1, this column will be included, indicating the stage of infection for each individual. There is a column for each partner. Possible values are:

    .. hlist::
        :columns: 1

        * 0 = Uninfected
        * 1 = Untreated acute HIV infection
        * 2 = Untreated latent HIV infection
        * 3 = Untreated late/AIDS stage
        * 4 = On ART

    Note: this only included in HIV simulations."
    "<A or B>_HIV_Tested_Positive", boolean, "If the **Report_Relationship_Start_Include_HIV_Disease_Statistics** parameter is set to 1, this column will be included, indicating whether or not the partner has ever tested positive for HIV using the results of the **HIVRapidHIVDiagnostic** campaign parameter. 0 indicates the partner has never tested positive, 1 indicates they have tested positive. See :doc:`emod-hiv:parameter-campaign-individual-hivrapidhivdiagnostic` for configuration details. There is a column for each partner. Note: this is only included in HIV simulations."
    "<A or B>_HIV_Received_Results", string, "If the **Include_HIV_Disease_Statistics** parameter is set to 1, this column will be included, indicating the results received by the individual from the latest HIV test using the **HIVRapidHIVDiagnostic** campaign parameter. Possible values are:


    UNKNOWN
      Indicates that the individual did not receive their results.

    NEGATIVE
      Indicates that the most recent results were negative.

    POSITIVE
      Indicates that the most recent results were positive.


    Whether or not the an individual receives their results is determined by the **Probability_Received_Results** campaign parameter—see :doc:`emod-hiv:parameter-campaign-individual-hivrapidhivdiagnostic` for configuration details. There is a column for each partner. Note: this is only included in HIV simulations."



Example
=======

The following is an example of a RelationshipStart.csv report:

.. csv-table::
    :file: RelationshipStart-Example.csv