# HIVARTStagingByCD4Diagnostic

The **HIVARTStagingByCD4Diagnostic** intervention class builds on the [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
intervention by checking for treatment eligibility based on CD4
count. It uses the lowest-ever recorded CD4 count for that individual, based on the history of past
CD4 counts conducted using the HIVDrawBlood intervention. To specify the outcome based on age bins
instead of CD4 testing, use [parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic](parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic.md).

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

*See parameter table: [campaign-hivartstagingbycd4diagnostic.csv](../csv/campaign-hivartstagingbycd4diagnostic.csv)*

*See example: [campaign-hivartstagingbycd4diagnostic.json](../json/campaign-hivartstagingbycd4diagnostic.json)*
