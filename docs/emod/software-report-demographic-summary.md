# DemographicsSummary

The demographic summary output report (DemographicsSummary.json) is a JSON-formatted file with the
demographic *channel* output results of the simulation, consisting of simulation-wide averages
by time step. The format is identical to the inset chart output report, except the channels reflect
demographic categories, such as gender ratio.

To generate the demographics summary report, set the **Enable_Demographics_Reporting** configuration
parameter to 1. The [software-report-binned](software-report-binned.md) will also be generated.

The file contains a header and a channels section.

## Header

The header section contains the following parameters.

## Channels

The channels section contains the following parameters.

## Example

The following is a sample of a DemographicsSummary.json file.

*See example: [report-demographic.json](../json/report-demographic.json)*
