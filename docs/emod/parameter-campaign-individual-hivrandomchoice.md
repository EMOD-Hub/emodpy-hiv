# HIVRandomChoice

The **HIVRandomChoice** intervention class is based on
[SimpleDiagnostic](parameter-campaign-individual-simplediagnostic.md), but adds parameters to change the logic in
how and where treatment is applied to individuals based on specified probabilities.

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

{{ read_csv('../csv/campaign-hivrandomchoice.csv', keep_default_na=False) }}

```json
{
  "Use_Defaults": 1,
  "Campaign_Name": "RandomChoice validation",
  "Events": [
    {
      "class": "CampaignEvent",
      "Event_Name": "RandomChoice event",
      "Start_Day": 1,
      "Nodeset_Config": {
        "class": "NodeSetAll"
      },
      "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Demographic_Coverage": 1,
        "Intervention_Config": {
          "class": "HIVRandomChoice",
          "Days_To_Diagnosis": 0,
          "Event_Or_Config": "Event",
          "Disqualifying_Properties": [],
          "New_Property_Value": "InterventionStatus:None",
          "Choice_Names": [
            "OnART1",
            "OnART2",
            "OnART4",
            "OnART5"
          ],
          "Choice_Probabilities": [
            0.1,
            0.2,
            0.3,
            0.4
          ]
        }
      }
    }
  ]
}
```
