# FemaleContraceptive

The **FemaleContraceptive** intervention is used to reduce the fertility rate of females of 
reproductive age (14 to 45 years old), based on a distribution set by the user. This intervention 
can only be distributed to females, and ignores the waning condition expiration (as women could still 
use a contraceptive, even if it is ineffective). Note: the **Birth_Rate_Dependence** configuration parameter 
must be set to INDIVIDUAL_PREGNANCIES or INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR or an error will result.

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

{{ read_csv('../csv/campaign-femalecontraceptive.csv', keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [
        {
            "class": "CampaignEvent",
            "Start_Day": 730,
            "Nodeset_Config": { "class": "NodeSetAll" },
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Target_Demographic": "ExplicitGender",
                "Target_Gender": "Female",
                "Demographic_Coverage": 0.1,
                "Intervention_Config": {
                    "class": "FemaleContraceptive",
                    "Cost_To_Consumer": 1,
                    "Waning_Config": {
                        "class": "WaningEffectConstant",
                        "Initial_Effect": 0.25
                    },
                    "Usage_Duration_Distribution": "CONSTANT_DISTRIBUTION",
                    "Usage_Duration_Constant": 730,
                    "Usage_Expiration_Event": "StopUsingContraceptive"
                }
            }
        }
    ]
}
```
