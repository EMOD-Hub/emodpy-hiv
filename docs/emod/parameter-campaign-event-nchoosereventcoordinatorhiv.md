# NChooserEventCoordinatorHIV

The **NChooserEventCoordinatorHIV** coordinator class distributes an individual-level intervention to exactly N
people of a targeted demographic in HIV simulations. This contrasts with other event coordinators
that distribute an intervention to a percentage of the population, not to an exact count. This event
coordinator is similar to the **NChooserEventCoordinator** for other simulation types, but replaces
start and end days with start and end years and includes HIV-specific restrictions that individuals
must have in order to qualify for the intervention.

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

{{ read_csv('../csv/campaign-nchoosereventcoordinatorhiv.csv') }}

*See example: [campaign-nchoosereventcoordinatorhiv.json](../json/campaign-nchoosereventcoordinatorhiv.json)*
