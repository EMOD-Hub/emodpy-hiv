# CoitalActRiskFactors

The **CoitalActRiskFactors** intervention class provides a method of modifying an individual's 
risk/probability of acquiring or transmitting an STI. If other risk multipliers are active (across other interventions), 
the values will be multiplied together; the resulting value will be multiplied with any active 
STI co-infection factors. When the intervention expires, the individual's risk factor multiplier returns 
to one. Since this intervention persists, it can be used with a reference tracking event coordinator (see 
[parameter-campaign-event-coordinators](parameter-campaign-event-coordinators.md) for details).

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

{{ read_csv('../csv/campaign-coitalactriskfactors.csv') }}

*See example: [campaign-coitalactriskfactors.json](../json/campaign-coitalactriskfactors.json)*
