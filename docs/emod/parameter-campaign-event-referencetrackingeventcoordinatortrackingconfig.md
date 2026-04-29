# ReferenceTrackingEventCoordinatorTrackingConfig

The **ReferenceTrackingEventCoordinatorTrackingConfig** coordinator class defines a particular prevalence of 
an individual-level attribute that should be present in a population over time, and a corresponding intervention 
that will cause individuals to acquire that attribute. The coordinator tracks the actual prevalence of that attribute against 
the desired prevalence; it will poll the population of nodes it has been assigned to determine how many people 
have the attribute. When coverage is less than the desired prevalence, it will distribute enough of the designated 
intervention to reach the desired prevalence. This coordinator is similar to the **ReferenceTrackingEventCoordinator**, but 
allows an *attribute* in the population to be polled, not only the intervention itself having been received. This allows for
tracking overall coverage when, potentially, multiple routes exist for individuals to have acquired the same target attribute.

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

*See parameter table: [campaign-referencetrackingeventcoordinatortrackingconfig.csv](../csv/campaign-referencetrackingeventcoordinatortrackingconfig.csv)*

Example: Use **Tracking_Config** to look at men who are not circumcised (by any route, not only via the **MaleCircumcision** 
intervention); if coverage is below the target level at the time of polling, apply the **MaleCircumcision** 
intervention to uncircumcised men to reach the target coverage.

*See example: [campaign-referencetrackingeventcoordinatortrackingconfig.json](../json/campaign-referencetrackingeventcoordinatortrackingconfig.json)*
