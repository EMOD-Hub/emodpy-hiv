# HIVDrawBlood

The **HIVDrawBlood** intervention class builds on [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
to represent phlebotomy for CD4 or viral load testing. It allows for a test
result to be recorded and used for future health care decisions, but does not intrinsically lead to
a health care event. A future health care decision will use this recorded CD4 count or viral load,
even if the actual CD4/viral load has changed since last phlebotomy. The result can be updated by
distributing another **HIVDrawBlood** intervention.

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

{{ read_csv('../csv/campaign-hivdrawblood.csv') }}

```json
{
  "Use_Defaults": 1,
  "Campaign_Name": "DrawBlood validation",
  "Events": [
    {
      "class": "CampaignEvent",
      "Event_Name": "starting on day 8, give everyone a repeated 2-day delayed intervention",
      "Start_Day": 8,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
          "class": "HIVDelayedIntervention",
          "Disqualifying_Properties": [
            "InterventionStatus:InterventionStatus_1",
            "InterventionStatus:InterventionStatus_2",
            "InterventionStatus:InterventionStatus_3"
          ],
          "New_Property_Value": "InterventionStatus:InterventionStatus_4",
          "Single_Use": 1,
          "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
          "Delay_Period_Constant": 2,
          "Broadcast_Event": "HIVNeedsHIVTest"
        }
      }
    },
    {
      "class": "CampaignEvent",
      "Event_Name": "DrawBlood event",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Event_Name": "DrawBlood constant test, broadcasts HIVPositiveHIVTest",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
          "class": "NodeLevelHealthTriggeredIV",
          "Trigger_Condition_List": [
            "HIVNeedsHIVTest"
          ],
          "Demographic_Coverage": 1,
          "Duration": 14600,
          "Actual_IndividualIntervention_Config": {
            "class": "HIVDrawBlood",
            "Positive_Diagnosis_Event": "HIVPositiveHIVTest",
            "Base_Specificity": 0,
            "Base_Sensitivity": 0,
            "Cost_To_Consumer": 10,
            "Days_To_Diagnosis": 0,
            "Disqualifying_Properties": [
              "InterventionStatus:InterventionStatus_1",
              "InterventionStatus:InterventionStatus_2",
              "InterventionStatus:InterventionStatus_3"
            ],
            "New_Property_Value": "InterventionStatus:InterventionStatus_4"
          }
        }
      }
    }
  ]
}
```
