# PropertyReport

The property output report  (PropertyReport.json) is a JSON-formatted file with the *channel*
output results of the simulation, defined by the groups set up using **IndividualProperties** in the
demographics file. See [NodeProperties and IndividualProperties](parameter-demographics.md#nodeproperties-and-individualproperties) for more information.   The report contains the count
of individuals with each possible IP key-value combination. The < channel-title > tells you the
statistic and property that are being counted. For example, it allows you to compare disease deaths
for people in the high risk group versus the low risk group.

To generate the property report, set the **Enable_Property_Output** configuration
parameter to 1.

The file contains a header and a channels section.

## Header

The header section contains the following parameters.

## Channels

The channels section contains the following parameters.

### Channel_Title

The following information is available for the <Channel_Title> parameters. Note that these channels
will have separate sections for each **IndividualProperites** key:value pair.

## Example

The following is a sample of a PropertyReport.json file.

*See example: [report-property.json](../json/report-property.json)*
