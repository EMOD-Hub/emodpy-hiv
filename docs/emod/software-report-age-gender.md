# ReportHIVByAgeAndGender

The age- and gender-stratified HIV report (ReportHIVByAgeAndGender.csv) provides a detailed set of
HIV-related statistics, with numerous ways to customize and stratify the output. The report format
facilitates further analysis using a pivot table.

Some results, such as population size or number infected, are reported as single "snapshots" at the end
of the reporting period. Other values, such as deaths or new infections, are aggregated for the entire
reporting period. Further information on the output data types can be seen in the [Output file data](#output-file-data) section.

See the [Configuration](#configuration) section, below, for customization options and instructions.

## Configuration

To generate this report, the following parameters must be configured in the config.json file:

```json
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
```

## Output file data

The output report has three types of columns: stratification, polling, and period. The [Stratification columns](#stratification-columns)
have a predetermined value such as true (1) or false (0). The individuals in the row must have
this attribute to be included. The [Polling columns](#polling-columns) are those that count statistics as a snapshot at the end of the
reporting period. That is, if **HIV_Reporting_Period** is set to 360, then at the end of every 180 days,
the report will take a survey/poll to count statistics on the population. The data reflects the counts
for that specific day. By contrast, the [Period columns](#period-columns) will contain counts for the entire reporting period,
stratified into the rows the individuals qualify for when the count occurs. It is possible that
an individual qualifies for one stratification when the count occurs, and another when the polling is done.

Data columns of each type are as follows.

### Stratification columns

### Polling columns

### Period columns

## Example

The following is an example of a ReportHIVByAgeAndGender.csv report:

*See parameter table: [ReportHIVByAgeAndGender-Example.csv](ReportHIVByAgeAndGender-Example.csv)*
