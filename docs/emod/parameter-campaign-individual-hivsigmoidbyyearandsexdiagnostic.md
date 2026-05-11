# HIVSigmoidByYearAndSexDiagnostic

The **HIVSigmoidByYearAndSexDiagnostic** intervention class builds on [HIVSimpleDiagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
by allowing the probability of "positive diagnosis" to be configured sigmoidally in time. For a linear approach, use
[HIVPiecewiseByYearAndSexDiagnostic](parameter-campaign-individual-hivpiecewisebyyearandsexdiagnostic.md).

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

{{ read_csv('../csv/campaign-hivsigmoidbyyearandsexdiagnostic.csv', keep_default_na=False) }}

```json
{
    "Campaign_Name": "1d_MaleCircumcision_at_Age_18",
    "Default_Campaign_Path": "defaults/hiv_default_campaign.json",
    "Use_Defaults": 1,
    "Events":
    [
        {
            "class": "CampaignEventByYear",
            "Event_Name": "Male circumcision at birth",
            "Start_Year": 1990,
            "Nodeset_Config":
            {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config":
            {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config":
                {
                    "class": "BirthTriggeredIV",
                    "Target_Demographic": "ExplicitGender",
                    "Target_Gender": "Male",
                    "Demographic_Coverage": 1,
                    "Actual_IndividualIntervention_Config":
                    {
                        "class": "HIVSigmoidByYearAndSexDiagnostic",
                        "New_Property_Value": "InterventionStatus:None",
                        "Ramp_Min": 0.0,
                        "Ramp_Max": 0.3,
                        "Ramp_MidYear": 2002.0,
                        "Ramp_Rate": 0.5,
                        "Positive_Diagnosis_Event": "HIVNeedsMaleCircumcision"
                    }
                }
            }
        }
    ]
}
```
