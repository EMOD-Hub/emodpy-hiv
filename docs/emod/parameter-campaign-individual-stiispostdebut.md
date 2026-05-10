# STIIsPostDebut

The **STIIsPostDebut** intervention class is based on **SimpleDiagnostic**, but adds a check to see
if the individual is post-STI debut. Note that this is not connected to **IndividualProperties** in
the demographics file.

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

{{ read_csv('../csv/campaign-stiispostdebut.csv') }}

```json
{
     "Use_Defaults": 1,
     "Campaign_Name": "IsPostDebutCensus",
     "Events": [
        {
            "class": "CampaignEvent",
            "Event_Name": "Is Post Debut?  Broadcast for event reporter.",
            "Start_Day": 14539,
            "Nodeset_Config": { "class": "NodeSetAll" },
            "Event_Coordinator_Config":
            {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Demographic_Coverage": 1,
                "Intervention_Config":
                {
                    "class": "STIIsPostDebut",
                    "Event_Or_Config": "Event",
                    "Positive_Diagnosis_Event": "PostDebut",
                    "Negative_Diagnosis_Event": "PreDebut"
                }
            }
        }
     ]
}
```
