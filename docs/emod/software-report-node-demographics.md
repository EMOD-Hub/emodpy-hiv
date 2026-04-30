# ReportNodeDemographics

The node demographics report (ReportNodeDemographics.csv) is a CSV-formatted report that provides
population information stratified by node. For each time step, the report will collect data on each
node and age bin.

## Configuration

To generate this report, the following parameters must be configured in the custom_reports.json file:

```json
{
    "Reports": [
        {
            "class": "ReportNodeDemographics",
            "Age_Bins": [
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100,
                125
            ],
            "IP_Key_To_Collect": "",
            "Stratify_by_Gender": 1
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data

The report will contain the following output data, divided between stratification columns and data
columns.

### Stratification columns

### Data columns

## Example

The following is an example of ReportNodeDemographics.csv.

*See parameter table: [report-node-demographics.csv](report-node-demographics.csv)*
