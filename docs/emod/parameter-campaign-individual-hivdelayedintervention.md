# HIVDelayedIntervention

**HIVDelayedIntervention** is an intermediate intervention class based on [parameter-campaign-individual-delayedintervention](parameter-campaign-individual-delayedintervention.md),
but adds several features that are specific to the HIV model.
This intervention provides new types of distributions for setting the delay and also enables event
broadcasting after the delay period expires.

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

{{ read_csv('../csv/campaign-hivdelayedintervention.csv') }}

*See example: [campaign-hivdelayedintervention.json](../json/campaign-hivdelayedintervention.json)*
