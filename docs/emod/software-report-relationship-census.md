# ReportRelationshipCensus

The relationship census report (ReportRelationshipCensus.csv) is a CSV-formatted report
that extracts relationship numbers for each person during each taking of the census. The census
is a one day event collecting data for that person as of that day.

## Configuration

To generate this report, the following parameters must be configured in the custom_reports.json file:

```json
{
    "Reports": [
        {
            "class": "ReportRelationshipCensus",
            "Report_File_Name": "MyCensusReport.csv",
            "Start_Year": 2020,
            "End_Year": 2050,
            "Reporting_Interval_Years": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data

The output report will contain the following information.

### Data columns

## Example

The following is an example of a ReportRelationshipCensus.csv file.

{{ read_csv('ReportRelationshipCensus-Example.csv') }}
