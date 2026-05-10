# HIVDelayedIntervention

**HIVDelayedIntervention** is an intermediate intervention class based on [parameter-campaign-individual-delayedintervention](parameter-campaign-individual-delayedintervention.md),
but adds several features that are specific to the HIV model.
This intervention provides new types of distributions for setting the delay and also enables event
broadcasting after the delay period expires.

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

{{ read_csv('../csv/campaign-hivdelayedintervention.csv', keep_default_na=False) }}

```json
{
  "Use_Defaults": 1,
  "Campaign_Name": "35_HIV_Delayed_Intervention",
  "Events": [
    {
      "class": "CampaignEvent",
      "Event_Name": "LTFU0 broadcasts should proceed the expiration period of 9 days",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
          "class": "HIVDelayedIntervention",
          "Disqualifying_Properties": [],
          "New_Property_Value": "",
          "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
          "Delay_Period_Constant": 8,
          "Expiration_Period": 9,
          "Broadcast_Event": "LTFU0"
        }
      }
    },
    {
      "class": "CampaignEvent",
      "Event_Name": "LTFU1 broadcasts should be truncated by the expiration period of 7 days",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
          "class": "HIVDelayedIntervention",
          "Disqualifying_Properties": [],
          "New_Property_Value": "",
          "Delay_Period_Distribution": "CONSTANT_DISTRIBUTION",
          "Delay_Period_Constant": 8,
          "Expiration_Period": 7,
          "Broadcast_Event": "LTFU1"
        }
      }
    }
  ]
}
```
