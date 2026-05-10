# ModifyStiCoInfectionStatus

The **ModifyStiCoInfectionStatus** intervention class creates or removes STI co-infections (which
influence the rate of HIV transmission). This intervention can be used to represent things like STI
treatment programs or STI outbreaks.

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

{{ read_csv('../csv/campaign-modifysticoinfectionstatus.csv', keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "HIV Outbreak via Prevalence Increase",
    "Events": [
        {
            "Description": "Initial STI outbreak",
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": { "class": "NodeSetAll" },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1.00,
                "Target_Demographic": "ExplicitAgeRanges",
                "Target_Age_Min": 15,
                "Target_Age_Max": 30,
                "Intervention_Config": {
                    "class": "ModifyStiCoInfectionStatus",
                    "New_STI_CoInfection_Status": 1
                }
            }
        },
        {
            "Description": "STI Diagnostic",
            "class": "CampaignEvent",
            "Start_Day": 31,
            "Nodeset_Config": { "class": "NodeSetAll" },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1.0,
                "Target_Demographic": "ExplicitAgeRanges",
                "Target_Age_Min": 15,
                "Target_Age_Max": 30.1,
                "Intervention_Config": {
                    "class": "StiCoInfectionDiagnostic",
                    "Treatment_Fraction": 1.0,
                    "Event_Or_Config": "Config",
                    "Positive_Diagnosis_Config":
                    {
                        "class": "ModifyStiCoInfectionStatus",
                        "New_STI_CoInfection_Status": 0
                    }
                }
            }
        }
    ]
}
```
