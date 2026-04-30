# ReferenceTrackingEventCoordinator

The **ReferenceTrackingEventCoordinator** coordinator class defines a particular coverage of an individual-level
persistent intervention that should be present in a population over time. The coordinator tracks the actual
coverage with the desired coverage; it will poll the population of nodes it has been assigned to
determine how many people have the distributed intervention. When coverage is less than the desired
coverage, it will distribute enough interventions to reach the desired coverage.

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

*See parameter table: [campaign-referencetrackingeventcoordinator.csv](../csv/campaign-referencetrackingeventcoordinator.csv)*

*See example: [campaign-referencetrackingeventcoordinator.json](../json/campaign-referencetrackingeventcoordinator.json)*
