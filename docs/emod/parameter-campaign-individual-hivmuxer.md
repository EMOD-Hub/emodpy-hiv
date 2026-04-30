# HIVMuxer

The **HIVMuxer** intervention class is a method of placing groups of individuals into a waiting
pattern for the next event, and is based on [parameter-campaign-individual-delayedintervention](parameter-campaign-individual-delayedintervention.md).
**HIVMuxer** adds the ability to limit the number of times an individual can
be registered with the delay, which ensures that an individual is only provided with the delay one
time. For example, without **HIVMuxer**, an individual could be given an exponential delay twice,
effectively doubling the rate of leaving the delay.

> **NOTE:**
> Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
> Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
> that parameter.
>
> EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.
>
> JSON format does not permit comments, but you can add "dummy" parameters to add contextual
> information to your files. Any keys that are not EMOD parameter names will be ignored by the
> model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv('../csv/campaign-hivmuxer.csv') }}

*See example: [campaign-hivmuxer.json](../json/campaign-hivmuxer.json)*
