# TransmissionReport

The HIV relationship transmission report (TransmissionReport.csv) provides detailed information about
each transmission event and relationship members, evaluated at the time of disease transmission within
the relationship. It includes the time/date of transmission and information about the transmitter and
recipient, including: age, gender, current and lifetime number of relationships, infection stage,
circumcision status for males, co-infections, and disease-specific biomarkers, if applicable.

## Configuration

To generate the report, set the **Report_Transmission** parameter to 1 in the config.json file.

## Output file data

The output report will contain the following information.

> **NOTE:**
> Note: Data channels with <SRC or DEST> indicated will return one column for each partner: SRC (the source/transmitting partner) and DEST (the destination/receiving partner).

## Example

The following is an example of a TransmissionReport.csv report:

{{ read_csv('TransmissionReport-Example.csv') }}
