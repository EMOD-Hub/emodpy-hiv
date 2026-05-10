# HIVRapidHIVDiagnostic

The **HIVRapidHIVDiagnostic** intervention class builds on [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
by also updating the individual's knowledge of their HIV status. This can affect their access to ART
in the future as well as other behaviors. This intervention should be used only if the individual’s
knowledge of their status should impact a voluntary male circumcision campaign.

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

{{ read_csv('../csv/campaign-hivrapidhivdiagnostic.csv') }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "Generic HIV Outbreak",
    "Events": [{
        "class": "CampaignEvent",
        "Event_Name": "Test for HIV",
        "Start_Day": 0,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "Intervention_Config": {
                "class": "HIVRapidHIVDiagnostic",
                "Days_To_Diagnosis": 1,
                "Probability_Received_Result": 0.9,
                "Disqualifying_Properties": [],
                "New_Property_Value": "",
                "Positive_Diagnosis_Event": "HCTTestingLoop2",
                "Negative_Diagnosis_Event": "HCTTestingLoop3"
            },
            "Target_Demographic": "Everyone",
            "Demographic_Coverage": 1.0,
            "Number_Repetitions": 35,
            "Timesteps_Between_Repetitions": 200,
            "class": "StandardInterventionDistributionEventCoordinator",
            "Travel_Linked": 0
        }
    }]
}
```
