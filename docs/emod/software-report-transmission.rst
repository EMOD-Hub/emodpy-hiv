==================
TransmissionReport
==================

The HIV relationship transmission report (TransmissionReport.csv) provides detailed information about
each transmission event and relationship members, evaluated at the time of disease transmission within
the relationship. It includes the time/date of transmission and information about the transmitter and
recipient, including: age, gender, current and lifetime number of relationships, infection stage,
circumcision status for males, co-infections, and disease-specific biomarkers, if applicable.



Configuration
=============

To generate the report, set the **Report_Transmission** parameter to 1 in the config.json file.



Output file data
================

The output report will contain the following information.

.. note::
  Note: Data channels with <SRC or DEST> indicated will return one column for each partner: SRC (the source/transmitting partner) and DEST (the destination/receiving partner).


.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    SIM_TIME, float, "The time of simulation, in days, when the infection was transmitted."
    YEAR, float, "The time of the simulation, in units of calendar year, when the infection was transmitted. For STI simulations, this is the simulation time divided by 365. For HIV simulations, this is the simulation time divided by 365, added to the **Base_Year** value. If no base year is specified in the config.json file, the default value 2015 will be used."
    NODE_ID, integer, "The identification number of the node where the transmission event occurred."
    REL_ID, integer, "The unique ID of the relationship in which the transmission event occurred. This ID can be used between reports such as RelationshipStart.csv, RelationshipEnd.csv, and RelationshipConsummated.csv to cross-reference specific relationships."
    "REL_TYPE (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL)", integer, "The type of relationship the participants were in at the time of the transmission event. Values for 0-3 as indicated in the header."
    Is_rel_outside_PFA, boolean, "Indicates whether or not the relationship was created by the normal process using the Pair Forming Algorithm (PFA), where 0 indicates the relationship was created using the PFA, and 1 indicates the relationship was created using the **StartNewRelationship** intervention."
    "<SRC or DEST>_ID", integer, "The unique identification number of the individual. There is a column for each partner."
    "<SRC or DEST>_INFECTED", boolean, "Describes whether or not the individual is infected: 0 for not infected, 1 for infected. There is a column for each partner."
    "<SRC or DEST>_GENDER", boolean, "Describes the gender of the individual: 0 for male, 1 for female. There is a column for each partner."
    "<SRC or DEST>_AGE", float, "The age of the individual in days, including fractions of days up to two decimal places. There is a column for each partner."
    "<SRC or DEST>_IP", string, "A string of Key:Value pairs indicating the individual properties (IPs) that the individual has. The IP key and value are separated by a colon and the different Key:Value pairs are separated by commas (key1:value1,key2:value2,key3:value3). There is a column for each partner."
    "<SRC or DEST>_current_relationship_count", integer, "The total number of relationships (of all types) that the individual was in at the time of the transmission event. There is a column for each partner."
    "<SRC or DEST>_lifetime_relationship_count", integer, "The cumulative number of relationships (of all types) that the individual has been in prior to the transmission event. There is a column for each partner."
    "<SRC or DEST>_relationships_in_last_6_months", integer, "The number of relationships (of all types) that the individual has had in the 6 months prior to the transmission event. There is a column for each partner."
    "<SRC or DEST>_FLAGS", integer, "Indicates which types of relationships the individual is allowed to have when they have more than one active relationship. These values are configured using the **Concurrency_Configuration** parameter in the demographics file—see :doc:`parameter-demographics` for more information. These values can be updated when an individual migrates or has a value change in an individual property. The values are encoded in a 3-digit bitmask. In order, the digits correspond to Commercial (C), Marital (M), Informal (I), and Transitory (T) relationships. The following table provides example combinations:

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

    There is a column for each partner."
    "<SRC or DEST>_CIRCUMCISED", boolean, "Indicates whether or not the individual is circumcised (only applicable to males): 0 for not circumcised (and females), 1 for circumcised. There is a column for each partner."
    "<SRC or DEST>_STI", boolean, "Indicates whether or not the individual has an STI co-infection at the time of the transmission event, as determined by the **ModifyStiCoInfectionStatus** intervention: 0 if they do not have an STI co-infection, 1 if they do have an STI co-infection. There is a column for each partner."
    "<SRC or DEST>_SUPERSPREADER", boolean, "Indicates whether or not the individual is a superspreader, as determined by the **Probability_Person_Is_Behavioral_Super_Spreader** demographics parameter. 0 for not a superspreader, 1 for the individual is a superspreader. There is a column for each partner."
    SRC_INF_AGE, integer, "The age in days at which the transmitting individual acquired their infection. One column is returned, as this only applies to the transmitting individual."
    "<SRC or DEST>_CD4", float, "The CD4 count of the individual at the time of the transmission event. There is a column for each partner."
    "<SRC or DEST>_VIRAL_LOAD", float, "Not currently supported; 10000 indicates that the individual is infected. There is a column for each partner."
    "<SRC or DEST>_STAGE", enum, "Indicates the stage of HIV infection for the individual. Possible values are:

    .. hlist::
        :columns: 1

        * 0 = Uninfected
        * 1 = Untreated acute HIV infection
        * 2 = Untreated latent HIV infection
        * 3 = Untreated late/AIDS stage
        * 4 = On ART

    There is a column for each partner."



Example
=======

The following is an example of a TransmissionReport.csv report:

.. csv-table::
    :file: TransmissionReport-Example.csv