# HIVDrawBlood

The **HIVDrawBlood** intervention class builds on [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
to represent phlebotomy for CD4 or viral load testing. It allows for a test
result to be recorded and used for future health care decisions, but does not intrinsically lead to
a health care event. A future health care decision will use this recorded CD4 count or viral load,
even if the actual CD4/viral load has changed since last phlebotomy. The result can be updated by
distributing another **HIVDrawBlood** intervention.

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

{{ read_csv('../csv/campaign-hivdrawblood.csv') }}

*See example: [campaign-hivdrawblood.json](../json/campaign-hivdrawblood.json)*
