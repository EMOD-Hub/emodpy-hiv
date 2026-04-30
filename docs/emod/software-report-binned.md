# BinnedReport

The binned output report  (BinnedReport.json) is a JSON-formatted file where the channel data has
been sorted into age bins. It is very similar to an inset chart, however, with the binned report all
channels are broken down into sub-channels (bins) based on age. For example, instead of
having a single prevalence channel, you might have prevalence in the "0-3 years old bin" and the
"4-6 years old bin, and so forth.

To generate the binned report, set the **Enable_Demographics_Reporting** configuration parameter
to 1. The demographics summary output report will also be generated.

The file contains a header and a channels section.

## Header

The header section contains the following parameters.

## Channels

The channels section contains the following parameters.

## Example

The following is an example of an HIV BinnedReport.json file.

*See example: [report-binned-HIV.json](../json/report-binned-HIV.json)*
