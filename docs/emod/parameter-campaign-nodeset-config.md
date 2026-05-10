# Nodeset_Config classes

The following classes determine in which nodes a campaign event will occur. Every
**CampaignEvent** requires a **Nodeset_Config** parameter specifying the target nodes.

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.

## NodeSetAll

The event will occur in all nodes in the simulation. This class has no parameters.

```json
{
    "Nodeset_Config": {
        "class": "NodeSetAll"
    }
}
```

## NodeSetNodeList

The event will occur only in the nodes specified by node ID.

{{ read_csv('../csv/campaign-nodesetnodelist.csv', keep_default_na=False) }}

```json
{
    "Events": [
        {
            "class": "CampaignEventByYear",
            "Start_Year": 2025,
            "Nodeset_Config": {
                "class": "NodeSetNodeList",
                "Node_List": [1, 2, 3]
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1.0,
                "Intervention_Config": {
                    "class": "ARTBasic"
                }
            }
        }
    ],
    "Use_Defaults": 1
}
```
