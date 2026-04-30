# CD4Diagnostic

The **CD4Diagnostic** intervention class is similar to [parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md),
but adds the ability to divide individual populations based on configurable CD4
count ranges. It uses the individual’s current actual CD4 count, regardless of when a CD4 test has
been performed. An event can then be applied based on the Low or High group to which the individuals
have been moved.

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

{{ read_csv('../csv/campaign-cd4diagnostic.csv') }}

*See example: [campaign-cd4diagnostic.json](../json/campaign-cd4diagnostic.json)*
