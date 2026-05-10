# AntiretroviralTherapy

The **AntiretroviralTherapy** intervention class begins antiretroviral therapy (ART) for specified individuals.
To remove an individual from ART, use [parameter-campaign-individual-artdropout](parameter-campaign-individual-artdropout.md).

Additional considerations when using this intervention:

* The model will not allow someone who is HIV negative to be put on ART.
* A person who has not previously been on ART is considered to be 'starting ART' at the time this intervention is applied; the model will track this start time/duration.
* If a person is already on ART from another intervention, receiving a second ART intervention will have no effect.
* If a person is on already ART and receives the [parameter-campaign-individual-artmortalitytable](parameter-campaign-individual-artmortalitytable.md) intervention, the original ART start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration since starting ART will not change; it will continue to increase.
* If a person is on ART and receives the [parameter-campaign-individual-artdropout](parameter-campaign-individual-artdropout.md) intervention, the person will go off ART and the duration will be reset; if receiving a new ART intervention, this new start time/duration will be used in any calculations.

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

{{ read_csv('../csv/campaign-antiretroviraltherapy.csv') }}

```json
{
    "Campaign_Name": "ARTBasic intervention test",
    "Use_Defaults": 1,
    "Events": [
        {
            "Description": "New infections get immediate ART",
            "class": "CampaignEvent",
            "Start_Day": 1,
            "Nodeset_Config": {
                "class": "NodeSetAll"
            },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Trigger_Condition_List": [
                        "NewInfectionEvent"
                    ],
                    "Demographic_Coverage": 1.0,
                    "Actual_IndividualIntervention_Config": {
                        "class": "AntiretroviralTherapy",
                        "Days_To_Achieve_Viral_Suppression": 1000000,
                        "ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality": 350,
                        "ART_Is_Active_Against_Mortality_And_Transmission": 1,
                        "ART_Survival_Hazard_Ratio_Female": 0.6775
                    }
                }
            }
        }
    ]
}
```
