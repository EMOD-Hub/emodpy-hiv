# ARTDropout

The **ARTDropout** intervention class removes an individual from antiretroviral therapy (ART) and
interrupts their progress through the cascade of care. The individual's infectiousness will return
to a non-suppressed level, and a new prognosis will be assigned.

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

{{ read_csv('../csv/campaign-artdropout.csv') }}

*See example: [campaign-artdropout.json](../json/campaign-artdropout.json)*
