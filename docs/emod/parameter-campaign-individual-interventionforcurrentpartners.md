# InterventionForCurrentPartners

The **InterventionForCurrentPartners** intervention class provides a mechanism for the partners of
individuals in the care system to also seek care. Partners do not need to seek testing at the same
time; a delay may occur between the initial test and the partner's test. If a relationship has been
paused, such as when a partner migrates to a different node, the partner will not be contacted.

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

{{ read_csv('../csv/campaign-interventionforcurrentpartners.csv') }}

*See example: [campaign-interventionforcurrentpartners.json](../json/campaign-interventionforcurrentpartners.json)*
