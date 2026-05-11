# HIVPiecewiseByYearandSexDiagnostic

The **HIVPiecewiseByYearAndSexDiagnostic** intervention class builds on
[HIVSimpleDiagnostic](parameter-campaign-individual-hivsimplediagnostic.md) to configure the roll-out of an intervention
over time. Unlike [HIVSigmoidByYearAndSexDiagnostic](parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic.md),
which requires the time trend to have a sigmoid shape, this intervention allows for any trend of
time to be configured using piecewise or linear interpolation. The trends over time can be
configured differently for males and females. Note that the term "diagnosis" is used because this
builds on the diagnostic classes in EMOD. However, this intervention is typically used not like
a clinical diagnostic, but more like a trend in behavior or coverage over time.

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

{{ read_csv('../csv/campaign-hivpiecewisebyyearandsexdiagnostic.csv', keep_default_na=False) }}

```json
{
    "Campaign_Name": "4b_ImprovedRetention_To_BloodDraw",
    "Default_Campaign_Path": "defaults/hiv_default_campaign.json",
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEventByYear",
            "Event_Name": "ARTStaging: state 5 (random choice: Return for CD4 or LTFU)",
            "Start_Year": 1990,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": [
                        "ARTStaging5"
                    ],
                    "Actual_IndividualIntervention_Config": {
                        "class": "HIVPiecewiseByYearAndSexDiagnostic",
                        "Disqualifying_Properties": [
                            "InterventionStatus:LostForever",
                            "InterventionStatus:OnART",
                            "InterventionStatus:LinkingToART",
                            "InterventionStatus:OnPreART",
                            "InterventionStatus:LinkingToPreART"
                        ],
                        "New_Property_Value": "InterventionStatus:ARTStaging",
                        "Days_To_Diagnosis": 0,
                        "Default_Value": 0,
                        "Time_Value_Map": {
                            "Times": [
                                1990,
                                2020
                            ],
                            "Values": [
                                0.85,
                                0.9
                            ]
                        },
                        "Interpolation_Order": 0,
                        "Event_Or_Config": "Event",
                        "Positive_Diagnosis_Event": "ARTStaging6",
                        "Negative_Diagnosis_Event": "HCTUptakePostDebut9"
                    }
                }
            }
        }
    ]
}
```
