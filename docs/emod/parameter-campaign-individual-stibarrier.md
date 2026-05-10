# STIBarrier

The **STIBarrier** intervention is used to reduce the probability of STI or HIV transmission by
applying a time-variable probability of condom usage. Each **STIBarrier** intervention is directed
at a specific relationship type, and must be configured as a sigmoid trend over time.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv('../csv/campaign-stibarrier.csv', keep_default_na=False) }}

```json
{
    "Campaign_Name": "Baseline campaign for HIV-5 examples",
    "Events": [
        {
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "STIBarrier",
                    "Early": 1.0,
                    "Late": 1.0,
                    "Midyear": 1990,
                    "Rate": 1.0,
                    "Relationship_Type": "INFORMAL",
                    "Cost_To_Consumer": 1.0
                },
                "Target_Demographic": "Everyone",
                "class": "StandardInterventionDistributionEventCoordinator"
            },
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Year": 1992,
            "class": "CampaignEventByYear"
        },
        {
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "STIBarrier",
                    "Early": 1.0,
                    "Late": 1.0,
                    "Midyear": 1990,
                    "Rate": 1.0,
                    "Relationship_Type": "MARITAL",
                    "Cost_To_Consumer": 1.0
                },
                "Target_Demographic": "Everyone",
                "class": "StandardInterventionDistributionEventCoordinator"
            },
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Year": 1996,
            "class": "CampaignEventByYear"
        }
    ],
    "Use_Defaults": 1
}
```
