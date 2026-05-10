# MaleCircumcision

The **MaleCircumcision** intervention class introduces male circumcision as a method to control HIV
transmission. Voluntary medical male circumcision (VMMC) permanently reduces a male's likelihood of
acquiring HIV; successful distribution results in a reduction in the probability of transmission.

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

{{ read_csv('../csv/campaign-malecircumcision.csv') }}

```json
{
    "Use_Defaults": 1,
    "Campaign_Name": "HIV 3B: VMMC",
    "Events": [{
        "class": "CampaignEventByYear",
        "Event_Name": "Male circumcision at birth starting in 2025",
        "Start_Year": 2025,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Intervention_Config": {
                "class": "BirthTriggeredIV",
                "Demographic_Coverage": 1,
                "Target_Demographic": "ExplicitGender",
                "Target_Gender": "Male",
                "Actual_IndividualIntervention_Config": {
                    "class": "MaleCircumcision",
                    "Circumcision_Reduced_Acquire": 0.6
                }
            }
        }
    }]
}
```
