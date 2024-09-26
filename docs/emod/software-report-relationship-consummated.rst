=======================
RelationshipConsummated
=======================

The coital act report (RelationshipConsummated.csv) provides detailed information about each
coital act that occurs during the simulation. The report includes unique identifiers for each coital
act and relationship; the relationship type, number of acts, whether a condom was used, and whether
transmission occurred; and detailed information about each participant, including age, gender, infection status,
circumcision status, co-infection status, and treatment status. Each participant in a relationship is
referred to as either participant "A" or participant "B".

One row of data is returned per coital act, and results are ordered on a per-relationship basis. Note:
if a person is engaged in coital acts in multiple relationships during a time step, the order of those
acts is unknown, only in which relationship they occurred. Additionally, if a person gets infected during
a time step, they cannot re-transmit that infection during the same time step. The report does record
during which coital act transmission occurred.

If an uninfected person has coital acts with multiple infected partners during a time step, all
acts with the possibility of transmission are randomly ordered, so that the person has an equal chance
of getting infected from any one of their partners. The probability of transmission from any one of
these coital acts is still determined by the simulation parameters (number of acts, acquisition multipliers, etc.)


Configuration
=============


To generate the report, the following parameters must be configured in the config.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Report_Coital_Acts, boolean, NA, NA, 0, "Set this to 1 to generate the report."
    Report_Coital_Acts_Start_Year, float, 1900, 2200, 1900, "Simulation time in years to start collecting data."
    Report_Coital_Acts_End_Year, float, 1900, 2200, 2200, "Simulation time in years to stop collecting data."
    Report_Coital_Acts_Node_IDs_Of_Interest, float, 0, 2.14748e+09, [], "Data will be collected for the nodes in this list."
    Report_Coital_Acts_Min_Age_Years, float, 0, 9.3228e+35, 0, "The age that of one of the partners must be greater than or equal to for the coital act to be reported."
    Report_Coital_Acts_Max_Age_Years, float, 0, 9.3228e+35, 9.3228e+35, "The age that of one of the partners must be less than or equal to for the coital act to be reported."
    Report_Coital_Acts_Must_Have_IP_Key_Value, string, NA, NA, \"\", "A Key:Value pair that one of the partners must have for the coital act to be reported. Empty string means don't look at individual properties. For more information, see :doc:`model-properties`."
    Report_Coital_Acts_Must_Have_Intervention, string, NA, NA, \"\", "The name of an intervention that the one of the partners must have in order for the coital act to be reported. Empty string means don't look at the interventions. For more information, see :doc:`parameter-campaign-individual-interventions`."
    Report_Coital_Acts_Relationship_Type, enum, NA, NA, NA, "If not NA, data will only be collected on coital acts in relationships of this type. Possible values are:

    .. hlist::
        :columns: 1

        * TRANSITORY
        * INFORMAL
        * MARITAL
        * COMMERCIAL

    "
    Report_Coital_Acts_Has_Intervention_With_Name, string, NA, NA, \"\", "The name of an intervention that the one of the partners must have in order for the coital act to be reported. Empty string means don't look at the interventions. For more information, see :doc:`parameter-campaign-individual-interventions`."
    Report_Coital_Acts_Individual_Properties, array of strings, NA, NA, [], "A list of individual property (IP) keys that will
    be included in the report as applicable to each partner. One column will be added to the report for each partner, for each key in the list. Specify the IP keys by adding an **IndividualProperties** parameter in the demographics file. See :doc:`model-properties` for details on setting individual properties."
    Report_Coital_Acts_Partners_With_IP_Key_Value, array of strings, NA, NA, [], "A list of Key:Value pairs. Two columns will be added to the report for each Key:Value pair listed, one for each partner, indicating the number of that individual's partners for which the Key:Value pair applies."



.. code-block:: json

    {
        "Report_Coital_Acts": 1,
        "Report_Coital_Acts_Start_Year": 2000,
        "Report_Coital_Acts_End_Year": 2050,
        "Report_Coital_Acts_Node_IDs_Of_Interest": [ 1, 2, 3 ],
        "Report_Coital_Acts_Min_Age_Years": 30,
        "Report_Coital_Acts_Max_Age_Years": 90,
        "Report_Coital_Acts_Must_Have_IP_Key_Value": "Risk:LOW",
        "Report_Coital_Acts_Must_Have_Intervention": "",
        "Report_Coital_Acts_Relationship_Type": "MARITAL",
        "Report_Coital_Acts_Has_Intervention_With_Name": "",
        "Report_Coital_Acts_Individual_Properties": [],
        "Report_Coital_Acts_Partners_With_IP_Key_Value": ["Risk:HIGH"],
    }




Output file data
================

The output report will contain the following information.

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    Time, float, "The simulation time (in days) when the coital act occurred."
    Year, float, "The simulation time (in calendar years) when the coital act occurred."
    Node_ID, integer, "The numerical identifier of the node as defined in the demographics. See :doc:`parameter-demographics` for details on configuring the NodeID values."
    Coital_Act_ID, integer, "The unique identifier for the coital act."
    Rel_ID, integer, "The unique identifier for the relationship, different from the ID of the participants or the coital act."
    Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL), integer, "The type of relationship between individuals A and B. Values for 0-3 as indicated in the header."
    Is_rel_outside_PFA, boolean, "Indicates whether or not the relationship was created by the normal process using the Pair Forming Algorithm (PFA), where ""F"" indicates the relationship was created using the PFA, and ""T"" indicates the relationship was created using the **StartNewRelationship** intervention."
    "<A or B>_ID", integer, "The unique numerical identifier for the individual. There is a column for each partner."
    "<A or B>_gender", enum, "The gender of the individual (MALE or FEMALE). There is a column for each partner."
    "<A or B>_Age", float, "The age (in years) of the individual. There is a column for each partner."
    "<A or B>_Is_Infected", boolean, "Indicates whether or not the individual is infected: 0 for not infected, 1 for infected. There is a column for each partner."
    Did_Use_Condom, boolean, "Indicates if a condom was used for the coital act: 0 for no condom used, 1 for a condom was used."
    Risk_Multiplier, float, "Multiplier for the risk of transmission from the coital act. Determined by STI co-infection of either partner (via **ModifyStiCoInfectionStatus**). The multiplier starts as the maximum value of the **STI_Coinfection_Acquisition_Multiplier** and **STI_Coinfection_Transmission_Multiplier** parameters. This maximum is then multiplied by the coital act risk factors from each partner, if they have the **CoitalActRiskFactor** intervention distributed. See :doc:`parameter-configuration-scalars` and :doc:`parameter-campaign-individual-interventions` for more information."
    Transmission_Multiplier, float, "Multiplier for disease transmission risk from the infected partner. Determined by the transmitter's infectiousness, and any immunity-modifying interventions. See :doc:`parameter-campaign-individual-interventions` for more information."
    Acquisition_Multiplier, float, "Multiplier for disease acquisition risk for the uninfected partner. Determined by:

    .. hlist::
        :columns: 1

        * The **MaleCircumcision** intervention, if the uninfected partner is male
        * The **Male_To_Female_Relative_Infectivity_Ages** and **Male_To_Female_Relative_Infectivity_Multipliers** campaign parameters, if the uninfected partner is female, and
        * Any acquisition-blocking interventions

    See :doc:`parameter-campaign` and :doc:`parameter-campaign-individual-interventions` for more information."
    Infection_Was_Transmitted, boolean, "Indicates whether or not the uninfected partner became infected due to this coital act: 0 if the uninfected partner was not infected, 1 if they were."
    "<A or B>_Num_Current_Rels", integer, "The total number of active relationships the individual is currently in. There is a column for each partner."
    "<A or B>_Is_Circumcised", boolean, "Indicates whether or not the individual is circumcised (only applicable to males): 0 for not circumcised (and females), 1 for circumcised. There is a column for each partner"
    "<A or B>_Has_Coinfection", boolean, "Indicates whether or not the individual has an STI co-infection, as determined by the **ModifyStiCoInfectionStatus** intervention: 0 if they do not have an STI co-infection, 1 if they do have an STI co-infection. There is a column for each partner. Note: this is only included for HIV simulations."
    "<A or B>_HIV_Infection_Stage", enum, "Indicates the stage of HIV infection for the receiving individual. Possible values are:

    .. hlist::
        :columns: 1

        * 0 = Uninfected
        * 1 = Untreated acute HIV infection
        * 2 = Untreated latent HIV infection
        * 3 = Untreated late/AIDS stage
        * 4 = On ART

    There is a column for each partner. Note: this is only included for HIV simulations."
    "<A or B>_Is_On_ART", boolean, "Indicates whether or not the individual is on ART: 0 if they are not on ART, 1 if they are currently receiving ART. There is a column for each partner. Note: this is only included for HIV simulations."
    "<A or B>_IP=<IP Key>", string, "For each IP Key listed in **Report_Coital_Acts_Individual_Properties**, a column will be added to the report for each partner, indicating the value of that IP Key for that partner."
    "<A or B>_PartersWith_IP=<IP Key:Value>", integer, "For each IP Key:Value pair listed in **Report_Coital_Acts_Partners_With_IP_Key_Value**, a column will be added to the report for each partner, indicating the number of their partners for whom that IP Key:Value pair applies."



Example
=======

The following is an example of a RelationshipConsummated.csv report:

.. csv-table::
    :file: RelationshipConsummated-Example.csv