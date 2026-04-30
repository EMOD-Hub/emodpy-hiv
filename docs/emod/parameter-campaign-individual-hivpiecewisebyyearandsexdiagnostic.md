# HIVPiecewiseByYearandSexDiagnostic

The **HIVPiecewiseByYearAndSexDiagnostic** intervention class builds on
[parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md) to configure the roll-out of an intervention
over time. Unlike [parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic](parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic.md),
which requires the time trend to have a sigmoid shape, this intervention allows for any trend of
time to be configured using piecewise or linear interpolation. The trends over time can be
configured differently for males and females. Note that the term "diagnosis" is used because this
builds on the diagnostic classes in EMOD. However, this intervention is typically used not like
a clinical diagnostic, but more like a trend in behavior or coverage over time.

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

{{ read_csv('../csv/campaign-hivpiecewisebyyearandsexdiagnostic.csv') }}

*See example: [campaign-hivpiecewisebyyearandsexdiagnostic.json](../json/campaign-hivpiecewisebyyearandsexdiagnostic.json)*
