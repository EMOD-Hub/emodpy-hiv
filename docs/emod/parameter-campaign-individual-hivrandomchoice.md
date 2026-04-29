# HIVRandomChoice

The **HIVRandomChoice** intervention class is based on
[parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md), but adds parameters to change the logic in
how and where treatment is applied to individuals based on specified probabilities.

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

*See parameter table: [campaign-hivrandomchoice.csv](../csv/campaign-hivrandomchoice.csv)*

*See example: [campaign-hivrandomchoice.json](../json/campaign-hivrandomchoice.json)*
