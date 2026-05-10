# HIVSimpleDiagnostic

The **HIVSimpleDiagnostic** intervention class is based on the [parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md)
intervention, but adds the ability to specify outcomes upon both positive and negative diagnosis
(whereas **SimpleDiagnostic** only allows for an outcome resulting from a positive diagnosis).
**HIVSimpleDiagnostic** tests for HIV status without logging the HIV test to the individual’s
medical history. To log the HIV test to the medical history, use [parameter-campaign-individual-hivrapidhivdiagnostic](parameter-campaign-individual-hivrapidhivdiagnostic.md)
instead.

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

{{ read_csv('../csv/campaign-hivsimplediagnostic.csv', keep_default_na=False) }}

```json
{
    "Events": [{
        "Event_Coordinator_Config": {
            "Demographic_Coverage": 1.0,
            "Intervention_Config": {
                "Base_Sensitivity": 1,
                "Base_Specificity": 1,
                "Days_to_Diagnosis": 0,
                "Event_or_Config": "Event",
                "Negative_Diagnosis_Event": "HIVNegativeTest",
                "Positive_Diagnosis_Event": "HIVPositiveTest",
                "Treatment_Fraction": 1,
                "class": "HIVSimpleDiagnostic"
            },
            "Number_Distributions": -1,
            "Number_Repetitions": 1,
            "Property_Restrictions": [],
            "Target_Group": "Everyone",
            "Timesteps_Between_Repetitions": 1,
            "class": "StandardInterventionDistributionEventCoordinator"
        },
        "Event_Name": "Test Everyone for HIV",
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Start_Day": 2,
        "class": "CampaignEvent"
    }],
    "Use_Defaults": 1
}
```
