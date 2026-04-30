# HIVSimpleDiagnostic

The **HIVSimpleDiagnostic** intervention class is based on the [parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md)
intervention, but adds the ability to specify outcomes upon both positive and negative diagnosis
(whereas **SimpleDiagnostic** only allows for an outcome resulting from a positive diagnosis).
**HIVSimpleDiagnostic** tests for HIV status without logging the HIV test to the individual’s
medical history. To log the HIV test to the medical history, use [parameter-campaign-individual-hivrapidhivdiagnostic](parameter-campaign-individual-hivrapidhivdiagnostic.md)
instead.

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

*See parameter table: [campaign-hivsimplediagnostic.csv](../csv/campaign-hivsimplediagnostic.csv)*

*See example: [campaign-hivsimplediagnostic.json](../json/campaign-hivsimplediagnostic.json)*
