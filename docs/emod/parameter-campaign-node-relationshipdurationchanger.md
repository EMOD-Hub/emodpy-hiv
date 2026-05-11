# RelationshipDurationChanger

The **RelationshipDurationChanger** node intervention class allows the user to change 
the duration of relationships of a particular type in a node. This allows the user to model, 
for example, how an education program or other intervention could cause a change in people's behavior. 
This intervention overrides the **Duration_Weibull_Heterogeneity** and **Duration_Weibull_Scale** 
values in the [Demographics file](software-demographics.md) that typically determine duration for each relationship type. Note, this 
intervention does not expire; it causes an existing intervention to be removed. Hence, to reset the 
parameter, the user should submit a second intervention with the original value. This change impacts the 
relationships one time step after it was distributed.

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

{{ read_csv('../csv/campaign-relationshipdurationchanger.csv', keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 40,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Node_Property_Restrictions": [{
                "HasHealthCare": "YES"
            }],
            "Intervention_Config": {
                "class": "RelationshipDurationChanger",
                "Relationship_Type": "COMMERCIAL",
                "Overriding_Duration_Weibull_Heterogeneity": 0.6,
                "Overriding_Duration_Weibull_Scale": 22.0
            }
        }
    }]
}
```
