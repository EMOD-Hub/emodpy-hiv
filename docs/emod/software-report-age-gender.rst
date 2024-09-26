=======================
ReportHIVByAgeAndGender
=======================

The age- and gender-stratified HIV report (ReportHIVByAgeAndGender.csv) provides a detailed set of
HIV-related statistics, with numerous ways to customize and stratify the output. The report format
facilitates further analysis using a pivot table.

Some results, such as population size or number infected, are reported as single "snapshots" at the end
of the reporting period. Other values, such as deaths or new infections, are aggregated for the entire
reporting period. Further information on the output data types can be seen in the `Output file data`_ section.

See the `Configuration`_ section, below, for customization options and instructions.

Configuration
=============

To generate this report, the following parameters must be configured in the config.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Report_HIV_ByAgeAndGender, boolean, NA, NA, 0, "Set to 1 to generate the report."
    Report_HIV_ByAgeAndGender_Start_Year, float, 1900, 2200, 1900, "The simulation time in years to start collecting data."
    Report_HIV_ByAgeAndGender_Stop_Year, float, 1900, 2200, 2200, "The simulation time in years to stop collecting data."
    Report_HIV_ByAgeAndGender_Collect_Gender_Data, boolean, NA, NA, 0, "When set to 1, the output report will be stratified by gender."
    Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data, array of floats, -3.40282e+38, 3.40282e+38, [], "A list of bins used to stratify the report by age. Each value defines the minimum value (inclusive) of that bin, while the next value defines the maximum value (exclusive) of the bin. The values cannot be equal and must be listed in ascending order. Leave the array empty to not stratify the report by age. The maximum number of age bins is 100."
    Report_HIV_ByAgeAndGender_Collect_Circumcision_Data, boolean, NA, NA, 0, "When set to 1, the IsCircumcised column is included in the output report. The report data will by stratified by those who do or do not have the MaleCircumcision intervention. Note: setting this to 1 doubles the number of rows in the output report."
    Report_HIV_ByAgeAndGender_Collect_HIV_Data, boolean, NA, NA, 0, "When set to 1, the HasHIV column is included in the output report. The report data will stratified by those who do or do not have HIV. Cannot be used with **Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data**. Note: setting this to 1 doubles the number of rows in the output report."
    Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data, boolean, NA, NA, 0, "When set to 1, the HIV_Stage column is included in the output report. The report data will be stratified by HIV Infection Stage (NOT_INFECTED, ACUTE, LATENT, AIDS, ON_ART). Cannot be used with **Report_HIV_ByAgeAndGender_Collect_HIV_Data** or **Report_HIV_ByAgeAndGender_Collect_On_Art_Data**."
    Report_HIV_ByAgeAndGender_Collect_On_Art_Data, boolean, NA, NA, 0, "When set to 1, the On_Art_Dim column is included in the output report. The report data will be stratified by those individuals who are on ART and those who are not. Cannot be used with **Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data**. Note: setting this to 1 doubles the number of rows in the output report."
    Report_HIV_ByAgeAndGender_Collect_IP_Data, array of strings, NA, NA, [], "A list of individual property (IP) keys used to stratify the report. A column will be added to the report for each IP listed. Specify the IP values by adding an **IndividualProperties** parameter in the demographics file. See :doc:`model-properties` for details on setting individual properties. Note: each IP key included here will also increase the number of rows in the report by several fold (once for each possible IP Key:Value pair)."
    Report_HIV_ByAgeAndGender_Collect_Intervention_Data, array of strings, NA, NA, [], "A list of interventions used to stratify the report. This allows for reporting on a subset (or all) of the interventions that an individual has been on, of those listed in the **Intervention_Name** campaign parameter. Note: this can only be used with interventions that remain with an individual for a period of time, such as VMMC, vaccine/PrEP, or those with a delay state in the cascade of care. See :doc:`parameter-campaign-individual-interventions` for a list of possible interventions."
    Report_HIV_ByAgeAndGender_Add_Transmitters, boolean, NA, NA, 0, "When set to 1, the Transmitters column is included in the output report. For a given row, this value indicates how many individuals that have transmitted the disease meet the specifications of that row."
    Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4, boolean, NA, NA, 0, "When set to 1, the number of infected individuals will be segregated into four columns based on CD4 count. When set to 0, the number of infected individuals are aggregated into one column regardless of CD4 count. Note: this creates additional polling columns, not more stratification rows."
    Report_HIV_ByAgeAndGender_Has_Intervention_With_Name, string, NA, NA, \"\", "This parameter is being deprecated. Use **Report_HIV_ByAgeAndGender_Collect_Intervention_Data** instead. If an intervention is listed for this parameter, one column will be added to the report, indicating how many individuals in the row have the intervention. See :doc:`parameter-campaign-individual-interventions` for possible intervention values. Note: this only works for interventions that remain with an individual for a period of time, such as VMMC, vaccine/PrEP, or those with a delay state in the cascade of care."
    Report_HIV_ByAgeAndGender_Event_Counter_List, array of strings, NA, NA, [], "A list of events used to stratify the report. A column will be added to the report for each event listed, showing the number of times the event occurred during the reporting period. To be counted, the individual must qualify for the row stratification at the time the event occurred, not necessarily at the end of the reporting period. See :doc:`parameter-campaign-event-list` for possible event values."
    Report_HIV_ByAgeAndGender_Add_Relationships, boolean, NA, NA, 0, "When set to 1, the report will contain data on the population currently in a relationship and ever in a relationship for each relationship type (TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL), eight columns total. Additionally, columns containing a sum of individuals in two or more partnerships (Has Concurrent Partners) and a sum of the lifetime number of relationships (Lifetime Partners) will be included."
    Report_HIV_ByAgeAndGender_Add_Concordant_Relationships, boolean, NA, NA, 0, "When set to 1, a Concordant column for each relationship type (TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL) is included in the output report. These contain totals for each relationship of each type where both partners have the same HIV status."



.. code-block:: json

    {
            "Report_HIV_ByAgeAndGender": 1,
            "Report_HIV_ByAgeAndGender_Start_Year": 2000,
            "Report_HIV_ByAgeAndGender_Stop_Year": 2050,
            "Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data": [ 15, 20, 25, 30, 35, 40, 125 ],
            "Report_HIV_ByAgeAndGender_Collect_Circumcision_Data": 0,
            "Report_HIV_ByAgeAndGender_Collect_Gender_Data": 1,
            "Report_HIV_ByAgeAndGender_Collect_HIV_Data": 1,
            "Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data": 0,
            "Report_HIV_ByAgeAndGender_Collect_IP_Data": ["InterventionStatus"],
            "Report_HIV_ByAgeAndGender_Collect_Intervention_Data": ["PrEP"],
            "Report_HIV_ByAgeAndGender_Collect_On_Art_Data": 1,
            "Report_HIV_ByAgeAndGender_Event_Counter_List": ["TestedNegative"],
            "Report_HIV_ByAgeAndGender_Has_Intervention_With_Name": "",
            "Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4": 1,
            "Report_HIV_ByAgeAndGender_Add_Concordant_Relationships": 1,
            "Report_HIV_ByAgeAndGender_Add_Relationships": 0,
            "Report_HIV_ByAgeAndGender_Add_Transmitters": 0,
    }




Output file data
================

The output report has three types of columns: stratification, polling, and period. The `Stratification columns`_
have a predetermined value such as true (1) or false (0). The individuals in the row must have
this attribute to be included. The `Polling columns`_ are those that count statistics as a snapshot at the end of the
reporting period. That is, if **HIV_Reporting_Period** is set to 360, then at the end of every 180 days,
the report will take a survey/poll to count statistics on the population. The data reflects the counts
for that specific day. By contrast, the `Period columns`_ will contain counts for the entire reporting period,
stratified into the rows the individuals qualify for when the count occurs. It is possible that
an individual qualifies for one stratification when the count occurs, and another when the polling is done.

Data columns of each type are as follows.

Stratification columns
----------------------

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 8, 5, 20


    Year, float, "The year at the end of the semiannual interval being recorded. For example, 1980.5 means that the counts in this row were aggregated over the first half of 1980, reported as a snapshot in the middle of the year 1980."
    NodeId, integer,  "The numerical identifier of the node as defined in the demographics. See :doc:`parameter-demographics` for details on configuring the NodeID values."
    Gender, boolean, "The gender of the individual.  0 indicates male, 1 indicates female."
    Age, float, "The age of the individual, as configured by the **Report_HIV_ByAgeAndGender_Collect_Age_Bins_Data** parameter."
    IP_Key:<IP_Key>, string, "For each IP key in the **Report_HIV_ByAgeAndGender_Collect_IP_Data** list, there will be a corresponding IP_Key column in the report. The individuals counted in that row will have that value for that key. See the `Configuration`_ section, above, for details on setting the **Report_HIV_ByAgeAndGender_Collect_IP_Data** values."
    HasIntervention:<Intervention>, string, "For each intervention name in the **Report_HIV_ByAgeAndGender_Collect_Intervention_Data** list, there will be a corresponding HasIntervention column in the report. Columns values will be 0 and 1, where 0 indicates that all individuals in that row do not have the intervention, and 1 indicates that they do. Note: The intervention names in the list are not checked for accuracy; errors will result in all zeros being returned for that column. Verify that each intervention name listed in this parameter is defined in the campaign file via the **Intervention_Name** parameter. The default of the **Intervention_Name** parameter is the class name of the intervention. See the `Configuration`_ section, above, for additional details on setting the **Report_HIV_ByAgeAndGender_Collect_Intervention_Data** values."
    IsCircumcised, integer, "If the **Report_HIV_ByAgeAndGender_Collect_Circumcision_Data** parameter is set to 1, then this column will be added to the report. The column values will be 0 or 1, where 0 indicates that all individuals in the row have not been circumcised, and 1 indicates that they have been."
    HasHIV, integer, "If the **Report_HIV_ByAgeAndGender_Collect_HIV_Data** parameter is set to 1, then this column will be added to the report. The column values will be 0 or 1, where 0 indicates that all individuals in that row are not infected with HIV, and 1 indicates they are."
    HIV_Stage, enum, "If the **Report_HIV_ByAgeAndGender_Collect_HIV_Stage_Data** parameter is set to 1, then this column will be added to the report. The values of the column will be NOT_INFECTED, ACUTE, LATENT, AIDS, and ON_ART, indicating the HIV stage of all individuals in that row."
    On_Art_Dim, integer, "If the **Report_HIV_ByAgeAndGender_Collect_On_Art_Data** parameter is set to 1, then this column will be added to the report. The values will be 0 or 1, where 0 indicates that all individuals in the row are not on ART, and 1 indicates they are."


Polling columns
---------------

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 8, 5, 20


    Population, float, "The total number of individuals that qualify for the stratification defined by the stratifying columns."
    Infected, float, "The number of HIV-infected individuals that qualify for the stratification defined by the stratifying columns."
    On_ART, float, "The number of individuals receiving ART that qualify for the stratification defined by the stratifying columns."
    Tested Past Year or On_ART, float, "The number of individuals receiving ART or having tested in the past year that qualify for the stratification defined by the stratifying columns."
    Tested Ever, float, "The number of individuals having ever been tested for HIV that qualify for the stratification defined by the stratifying columns."
    Diagnosed, float, "The number of HIV positive individuals. Equal to the number of new HIV positive diagnoses minus the number of individuals who died due to HIV."
    Infected CD4 Under 200 (Not On ART), float, "If the **Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals whose CD4 count is under 200 and who are not on ART."
    Infected CD4 200 to 349 (Not On ART), float, "If the **Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals whose CD4 count is between 200 and 349 and who are not on ART."
    Infected CD4 350 to 499 (Not On ART), float, "If the **Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals whose CD4 count is between 350 and 499 and who are not on ART."
    Infected CD4 500 Plus (Not On ART), float, "If the **Report_HIV_ByAgeAndGender_Stratify_Infected_By_CD4** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals whose CD4 count is greater than or equal to 500 and who are not on ART."
    HasIntervention(<Intervention>), float, "This parameter is being deprecated. Use **Report_HIV_ByAgeAndGender_Collect_IP_Data** instead; see `Configuration`_ for details. If a value is set for the **Report_HIV_ByAgeAndGender_Has_Intervention_With_Name** parameter, this column will be added to the report. It indicates the number of individuals in the row who have the specified intervention. Note: The intervention names in **Report_HIV_ByAgeAndGender_Has_Intervention_With_Name** are not checked for accuracy; errors will result in all zeros being returned for the column. Verify that the intervention name listed for this parameter is correct."
    Currently (TRANSITORY), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that are in at least one transitory relationship at the end of the reporting period."
    Currently (INFORMAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that are in at least one informal relationship at the end of the reporting period."
    Currently (MARITAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that are in at least one marital relationship at the end of the reporting period."
    Currently (COMMERCIAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that are in at least one commercial relationship at the end of the reporting period."
    Ever (TRANSITORY), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that have had at least one transitory relationship during their lifetime."
    Ever (INFORMAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that have had at least one informal relationship during their lifetime."
    Ever (MARITAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that have had at least one marital relationship during their lifetime."
    Ever (COMMERCIAL), float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row that have had at least one commercial relationship during their lifetime."
    Has Concurrent Partners, float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of individuals in the row who are in at least two relationships at the end of the reporting period."
    Current Partners, float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report.  It indicates the number of partners for the individuals that qualify for the row. That is, if an individual qualifies for the row, this column will include the number of partners they have at the end of the reporting period."
    Lifetime Partners, float, "If the **Report_HIV_ByAgeAndGender_Add_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the number of partners ever had by the individuals that qualify for the row. That is, if an individual that qualifies for the row has had 10 different partners during their life time at the end of the reporting period, then their 10 will be added to the value in the column."
    Num_TRANSITORY, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of transitory relationships at the end of the reporting period for individuals that qualify for the row. If two people are in a transitory relationship with each other and they both qualify for the row, both are counted separately (two total)."
    Num_INFORMAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of informal relationships at the end of the reporting period for individuals that qualify for the row. If two people are in an informal relationship with each other and they both qualify for the row, both are counted separately (two total)."
    Num_MARITAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of marital relationships at the end of the reporting period for individuals that qualify for the row. If two people are in a marital relationship with each other and they both qualify for the row, both are counted separately (two total)."
    Num_COMMERCIAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of commercial relationships at the end of the reporting period for individuals that qualify for the row. If two people are in a commercial relationship with each other and they both qualify for the row, both are counted separately (two total)."
    Num_Concordant_TRANSITORY, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of transitory relationships at the end of the reporting period where both partners have the same HIV status. If the person qualifying for the row is HIV negative and has two relationships—one with partner that is also HIV negative and one with a partner that is HIV positive—only the relationship where they are both HIV negative is counted."
    Num_Concordant_INFORMAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of informal relationships at the end of the reporting period where both partners have the same HIV status. If the person qualifying for the row is HIV negative and has two relationships—one with partner that is also HIV negative and one with a partner that is HIV positive—only the relationship where they are both HIV negative is counted."
    Num_Concordant_MARITAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of marital relationships at the end of the reporting period where both partners have the same HIV status. If the person qualifying for the row is HIV negative and has two relationships—one with partner that is also HIV negative and one with a partner that is HIV positive—only the relationship where they are both HIV negative is counted."
    Num_Concordant_COMMERCIAL, float, "If the **Report_HIV_ByAgeAndGender_Add_Concordant_Relationships** parameter is set to 1, then this column will be added to the report. It indicates the total number of commercial relationships at the end of the reporting period where both partners have the same HIV status. If the person qualifying for the row is HIV negative and has two relationships—one with partner that is also HIV negative and one with a partner that is HIV positive—only the relationship where they are both HIV negative is counted."

Period columns
--------------

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 8, 5, 20


    Newly Infected, float, "The number of newly infected individuals that qualify for the stratification defined by the stratifying columns, aggregated over the reporting period."
    Died, float, "The number of deaths among individuals that qualify for the stratification defined by the stratifying columns, aggregated over the reporting period."
    Died_from_HIV, float, "The number of deaths due to HIV (as opposed to background mortality) among individuals that qualify for the stratification defined by the stratifying columns, aggregated over the reporting period."
    Newly Tested Positive, float, "The number of positive HIV tests that occurred during the reporting period."
    Newly Tested Negative, float, "The number of negative HIV tests that occurred during the reporting period."
    Transmitters, float, "If the **Report_HIV_ByAgeAndGender_Add_Transmitters** parameter is set to 1, then this column will be added to the report. It indicates the total number of the individuals qualifying for that row who transmitted HIV during this reporting period. This may not add up to the number of new infections in the reporting period if any of the new infections were due to the OutbreakIndividual intervention or maternal transmission."
    <Event Name>, float, "If the **Report_HIV_ByAgeAndGender_Event_Counter_List** parameter has event names specified, there will be one column for each individual event name. The values in the column will be the count of the events that occurred during the reporting period for individuals qualifying for that row. For example, if the rows were stratified by HasHIV and the person was uninfected when the event occurred they would be counted in the HasHIV=0 row. However, if at the end of the reporting period the person had become infected, they would counted in the HasHIV=1 row."




Example
=======

The following is an example of a ReportHIVByAgeAndGender.csv report:

.. csv-table::
    :file: ReportHIVByAgeAndGender-Example.csv