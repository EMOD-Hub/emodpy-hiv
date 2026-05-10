# HIVMuxer

The **HIVMuxer** intervention class is a method of placing groups of individuals into a waiting
pattern for the next event, and is based on [parameter-campaign-individual-delayedintervention](parameter-campaign-individual-delayedintervention.md).
**HIVMuxer** adds the ability to limit the number of times an individual can
be registered with the delay, which ensures that an individual is only provided with the delay one
time. For example, without **HIVMuxer**, an individual could be given an exponential delay twice,
effectively doubling the rate of leaving the delay.

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

{{ read_csv('../csv/campaign-hivmuxer.csv') }}

```json
{
  "Use_Defaults": 1,
  "Campaign_Name": "4C: HIVMuxer",
  "Events": [
    {
      "Description": "Drive initial population into a loop",
      "class": "CampaignEvent",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config": {
          "class": "BroadcastEvent",
          "Broadcast_Event": "Loop_Entry_InitialPopulation"
        }
      }
    },
    {
      "Description": "Drive births into the same loop",
      "class": "CampaignEvent",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config": {
          "class": "BirthTriggeredIV",
          "Actual_IndividualIntervention_Config": {
            "class": "BroadcastEvent",
            "Broadcast_Event": "Loop_Entry_Birth"
          }
        }
      }
    },
    {
      "Description": "Attempt to drive entire population into loop again, HIVMuxer should disallow entry",
      "class": "CampaignEvent",
      "Start_Day": 1095,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config": {
          "class": "BroadcastEvent",
          "Broadcast_Event": "Loop_Entry_InitialPopulation"
        }
      }
    },
    {
      "Description": "Wait one year, only one entry allowed at a time per individual",
      "class": "CampaignEvent",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config": {
          "class": "NodeLevelHealthTriggeredIV",
          "Trigger_Condition": "TriggerList",
          "Trigger_Condition_List": [
            "Loop_Entry_InitialPopulation",
            "Loop_Entry_Birth",
            "Done_Waiting"
          ],
          "Actual_IndividualIntervention_Config": {
            "class": "HIVMuxer",
            "Disqualifying_Properties": [
              "InterventionStatus:Abort_Infinite_Loop"
            ],
            "New_Property_Value": "InterventionStatus:Infinite_Loop",
            "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
            "Delay_Period_Constant": 365,
            "Muxer_Name": "Delay_Loop_Muxer",
            "Max_Entries": 1,
            "Broadcast_Event": "Done_Waiting"
          }
        }
      }
    }
  ]
}
```
