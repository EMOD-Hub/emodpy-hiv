# ReportHIVInfection

The HIV disease progression report (ReportHIVInfection.csv) provides information on each individual's disease state at each time step, including age, gender, CD4 count, survival prognosis, ART status, and factors impacting transmission and acquisition.

## Configuration

To generate the report, the following parameters must be configured in the config.json file:

```json
{
    "Report_HIV_Infection": 1,
    "Report_HIV_Infection_Start_Year": 1940,
    "Report_HIV_Infection_Stop_Year": 2000
}
```

## Output file data

The output report will contain the following information.

### Data columns

## Example

The following is an example of a ReportHIVInfection.csv file.

{{ read_csv('ReportHIVInfection-Example.csv') }}
