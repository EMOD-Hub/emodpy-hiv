# HIVARTStagingByCD4Diagnostic

The **HIVARTStagingByCD4Diagnostic** intervention class builds on the [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
intervention by checking for treatment eligibility based on CD4
count. It uses the lowest-ever recorded CD4 count for that individual, based on the history of past
CD4 counts conducted using the HIVDrawBlood intervention. To specify the outcome based on age bins
instead of CD4 testing, use [parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic](parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic.md).

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

{{ read_csv('../csv/campaign-hivartstagingbycd4diagnostic.csv', keep_default_na=False) }}

```json
{
    "Campaign_Name": "2a_UniversalART",
    "Default_Campaign_Path": "defaults/hiv_default_campaign.json",
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEventByYear",
        "Event_Name": "ARTStaging: state 6 (check eligibility for ART by CD4)",
        "Start_Year": 1990,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "NodeLevelHealthTriggeredIV",
                "Trigger_Condition_List": [
                    "ARTStaging6"
                ],
                "Actual_IndividualIntervention_Config": {
                    "class": "HIVARTStagingByCD4Diagnostic",
                    "Disqualifying_Properties": [
                        "InterventionStatus:LostForever",
                        "InterventionStatus:OnART",
                        "InterventionStatus:LinkingToART",
                        "InterventionStatus:OnPreART",
                        "InterventionStatus:LinkingToPreART"
                    ],
                    "New_Property_Value": "InterventionStatus:ARTStaging",
                    "Threshold": {
                        "Times": [
                            2004,
                            2011.8,
                            2015,
                            2020
                        ],
                        "Values": [
                            200,
                            350,
                            500,
                            1000000
                        ]
                    },
                    "If_Pregnant": {
                        "Times": [
                            2010.34,
                            2015
                        ],
                        "Values": [
                            350,
                            1000
                        ]
                    },
                    "If_Breastfeeding": {
                        "Times": [
                            2004
                        ],
                        "Values": [
                            0
                        ]
                    },
                    "Event_Or_Config": "Event",
                    "Positive_Diagnosis_Event": "LinkingToART0",
                    "Negative_Diagnosis_Event": "LinkingToPreART0"
                }
            }
        }
    }]
}
```
