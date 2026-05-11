# BinnedReport

The binned output report  (BinnedReport.json) is a JSON-formatted file where the channel data has
been sorted into age bins. It is very similar to an inset chart, however, with the binned report all
channels are broken down into sub-channels (bins) based on age. For example, instead of
having a single prevalence channel, you might have prevalence in the "0-3 years old bin" and the
"4-6 years old bin, and so forth.

The file contains a header and a channels section.

## Configuration

To generate the report, set the **Enable_Demographics_Reporting** configuration parameter to 1. The [DemographicsSummary](software-report-demographic-summary.md) report will also be generated.

## Header

The header section contains the following parameters.

| Parameter | Data type | Description |
|---|---|---|
| DateTime | string | The time stamp indicating when the report was generated. |
| DTK_Version | string | The version of EMOD used. |
| Report_Type | string | The type of output report. |
| Report_Version | string | The format version of the report. |
| Timesteps | integer | The number of time steps in this simulation. |
| Channels | integer | The number of channels in the simulation. |
| Subchannel_Metadata | nested JSON object | Metadata that describes the bins and axis information. The metadata includes the following parameters:<br><br>**AxisLabels** (array of strings): The name of each axis.<br>**NumBinsPerAxis** (array of integers): The number of bins per axis.<br>**ValuesPerAxis** (array of integers): The maximum age in days for each bin in the axis.<br>**MeaningPerAxis** (array of strings): Shows the ValuesPerAxis values binned by age range, such as younger than 5 years (&lt;5), 5 to 9 (5-9), and so on.<br>**Base_Year** (float): The absolute time in years when the simulation begins. |

## Channels

The channels section contains the following parameters.

| Parameter | Data type | Description |
|---|---|---|
| &lt;Channel_Title&gt; | string | The title of the particular channel. |
| Units | string | The units used for this channel. |
| Data | array | A list of the channel data at each time step. |
| Infected | integer | The number of individuals who are currently infected in that age bin on that day. |
| New Infections | integer | The number of individuals who became infected on that day in that age bin. |
| Population | integer | The total number of individuals in that age bin on that day. |

## Example

The following is an example of an HIV BinnedReport.json file.

*See example: [report-binned-HIV.json](../json/report-binned-HIV.json)*
