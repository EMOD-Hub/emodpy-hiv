# PMTCT

The **PMTCT** (Prevention of Mother-to-Child Transmission) intervention class is used to define the
efficacy of **PMTCT** treatment at time of birth. This can only be used for mothers who are not on
suppressive ART and will automatically expire 40 weeks after distribution. Efficacy will be reset to
0 once it expires.

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

{{ read_csv('../csv/campaign-pmtct.csv', keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "DrawBlood validation",
    "Events": [
        {
            "Event_Name": "Nevarapine",
            "Event_Coordinator_Config": {
                "Demographic_Coverage": 1,
                "Intervention_Config": {
                    "Actual_IndividualIntervention_Config": {
                        "class": "PMTCT",
                        "Efficacy": 0.5
                    },
                    "Trigger_Condition_List": [
                        "FourteenWeeksPregnant"
                    ],
                    "Duration": 365,
                    "class": "NodeLevelHealthTriggeredIV"
                },
                "class": "StandardInterventionDistributionEventCoordinator"
            },
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Start_Day": 1,
            "class": "CampaignEvent"
        }
    ]
}
```
