# HIVARTStagingCD4AgnosticDiagnostic

The **HIVARTStagingCD4AgnosticDiagnostic** intervention class is similar to the
[parameter-campaign-individual-hivartstagingbycd4diagnostic](parameter-campaign-individual-hivartstagingbycd4diagnostic.md) intervention, but it uses age bins to
specify outcomes instead of the results of CD4 testing.

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

{{ read_csv('../csv/campaign-hivartstagingcd4agnosticdiagnostic.csv') }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "DrawBlood validation",
    "Events": [
        {
            "class": "CampaignEvent",
            "Event_Name": "OnART1-triggered piecewise event",
            "Start_Day": 1,

            "Nodeset_Config":
            {
                "class": "NodeSetAll"
            },

            "Event_Coordinator_Config":
            {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Event_Name": "DrawBlood constant test, broadcasts HIVPositiveHIVTest",
                "Demographic_Coverage": 1,
                "Intervention_Config":
                {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": [ "HIVNeedsHIVTest" ],

                    "Demographic_Coverage": 1,
                    "Duration": 14600,

                    "Actual_IndividualIntervention_Config":
                    {
                        "class"                    : "HIVARTStagingCD4AgnosticDiagnostic",
                        "Positive_Diagnosis_Event" : "HIVPositiveHIVTest",
                        "Base_Specificity"         : 0,
                        "Base_Sensitivity"         : 0,
                        "Cost_To_Consumer"         : 10,
                        "Days_To_Diagnosis"        : 5,
                        "Disqualifying_Properties"             : [ "InterventionStatus:InterventionStatus_1", "InterventionStatus:InterventionStatus_2", "InterventionStatus:InterventionStatus_3" ],
                        "New_Property_Value"            : "InterventionStatus:InterventionStatus_4",
                        "Individual_Property_Active_TB_Key" : "HasActiveTB",
                        "Individual_Property_Active_TB_Value" : "YES",
                        "Adult_Treatment_Age"    : 1865,
                        "Adult_By_WHO_Stage"                       : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                4.1, 2,   3, 4
                            ]
                        },
                        "Adult_By_TB"                              : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                0,   1,   1, 1
                            ]
                        },
                        "Adult_By_Pregnant"                        : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                1,   1,   1, 0
                            ]
                        },
                        "Child_Treat_Under_Age_In_Years_Threshold" : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                1,   2,   5, 3.2
                            ]
                        },
                        "Child_By_WHO_Stage"                       : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                1.1, 1.5, 2, 2.5
                            ]
                        },
                        "Child_By_TB"                              : {
                            "Times": [
                                1990, 1995, 2000, 2005
                            ],
                            "Values": [
                                1,   1,   1, 0
                            ]
                        }
                    }
                }
            }
        }
    ]
}
```
