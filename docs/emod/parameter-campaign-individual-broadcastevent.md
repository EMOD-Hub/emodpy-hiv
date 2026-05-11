# BroadcastEvent

The **BroadcastEvent** intervention class is an individual-level class that immediately broadcasts
the event trigger you specify. This campaign event is typically used with other classes that monitor
for a broadcast event, such as [NodeLevelHealthTriggeredIV](parameter-campaign-node-nodelevelhealthtriggerediv.md) or
[CommunityHealthWorkerEventCoordinator](parameter-campaign-event-communityhealthworkereventcoordinator.md).

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

{{ read_csv('../csv/campaign-broadcastevent.csv', keep_default_na=False) }}

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
