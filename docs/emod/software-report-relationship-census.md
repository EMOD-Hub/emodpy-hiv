# ReportRelationshipCensus

The relationship census report (ReportRelationshipCensus.csv) is a CSV-formatted report
that extracts relationship numbers for each person during each taking of the census. The census
is a one day event collecting data for that person as of that day.

## Configuration

To generate this report, the following parameters must be configured in the custom_reports.json file:

{{ read_csv('../csv/report-relationship-census.csv', keep_default_na=False) }}

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

| Parameter | Data type | Description |
|---|---|---|
| Year | float | Current time of the census in years. |
| NodeID | integer | The External ID of the node that the data is being collected for. |
| IndividualID | integer | The unique ID of the person whose information is being collected. |
| Gender | string | The gender of the individual. Possible values are "M" or "F." |
| AgeYears | float | The age in years of the person whose information is being collected. |
| IndividualProperties | string | A single string with the person's properties. The string will have a format where a key and value are separated by colons and the key-value pairs are separated by semi-colons. For example: KeyA:ValueA1;KeyB:ValueB1;KeyC:ValueC1. |
| NumRels_Last6Months_TRANSITORY | integer | The number of transitory relationships that the person has started in the last 6 months. |
| NumRels_Last6Months_INFORMAL | integer | The number of informal relationships that the person has started in the last 6 months. |
| NumRels_Last6Months_MARITAL | integer | The number of marital relationships that the person has started in the last 6 months. |
| NumRels_Last6Months_COMMERCIAL | integer | The number of commercial relationships that the person has started in the last 6 months. |
| NumRels_Active_TRANSITORY | integer | The number of transitory relationships the person has on the day of the census. |
| NumRels_Active_INFORMAL | integer | The number of active informal relationships the person has on the day of the census. |
| NumRels_Active_MARITAL | integer | The number of active marital relationships the person has on the day of the census. |
| NumRels_Active_COMMERCIAL | integer | The number of active commercial relationships the person has on the day of the census. |
| NumRels_Last12Months_TRANSITORY | integer | The number of transitory relationships that the person has started in the last 12 months. |
| NumRels_Last12Months_INFORMAL | integer | The number of informal relationships that the person has started in the last 12 months. |
| NumRels_Last12Months_MARITAL | integer | The number of marital relationships that the person has started in the last 12 months. |
| NumRels_Last12Months_COMMERCIAL | integer | The number of commercial relationships that the person has started in the last 12 months. |
| NumUniquePartners_Last-3-Months_TRANSITORY | integer | The number of different people that this person has had a transitory relationship in the last 3 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-3-Months_INFORMAL | integer | The number of different people that this person has had a informal relationship in the last 3 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-3-Months_MARITAL | integer | The number of different people that this person has had a marital relationship in the last 3 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-3-Months_COMMERCIAL | integer | The number of different people that this person has had a commercial relationship in the last 3 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-6-Months_TRANSITORY | integer | The number of different people that this person has had a transitory relationship in the last 6 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-6-Months_INFORMAL | integer | The number of different people that this person has had a informal relationship in the last 6 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-6-Months_MARITAL | integer | The number of different people that this person has had a marital relationship in the last 6 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-6-Months_COMMERCIAL | integer | The number of different people that this person has had a commercial relationship in the last 6 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-9-Months_TRANSITORY | integer | The number of different people that this person has had a transitory relationship in the last 9 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-9-Months_INFORMAL | integer | The number of different people that this person has had a informal relationship in the last 9 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-9-Months_MARITAL | integer | The number of different people that this person has had a marital relationship in the last 9 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-9-Months_COMMERCIAL | integer | The number of different people that this person has had a commercial relationship in the last 9 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-12-Months_TRANSITORY | integer | The number of different people that this person has had a transitory relationship in the last 12 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-12-Months_INFORMAL | integer | The number of different people that this person has had a informal relationship in the last 12 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-12-Months_MARITAL | integer | The number of different people that this person has had a marital relationship in the last 12 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |
| NumUniquePartners_Last-12-Months_COMMERCIAL | integer | The number of different people that this person has had a commercial relationship in the last 12 months. This is different than just the number of relationships because one could start and stop relationships with the same person. |

## Example

The following is an example of a ReportRelationshipCensus.csv file.

{{ read_csv('ReportRelationshipCensus-Example.csv', keep_default_na=False) }}
