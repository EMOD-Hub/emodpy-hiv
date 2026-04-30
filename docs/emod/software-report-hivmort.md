# HIVMortality

The HIV mortality report (HIVMortality.csv) provides information about individuals at the time of
their death, including disease status, CD4 count, medical history, and relationship history.

## Configuration

To generate the report, set the **Report_HIV_Mortality** parameter to 1 in the config.json file.

## Output file data

The output report will contain the following information.

## Example

The following is an example of a HIVMortality.csv report:

{{ read_csv('HIVMortality.csv') }}
