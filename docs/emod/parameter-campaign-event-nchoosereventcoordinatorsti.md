# NChooserEventCoordinatorSTI

The **NChooserEventCoordinatorSTI** coordinator class distributes an individual-level intervention to exactly N
people of a targeted demographic in STI simulations. This contrasts with other event coordinators
that distribute an intervention to a percentage of the population, not to an exact count. This event
coordinator is similar to the **NChooserEventCoordinator** for other simulation types, but replaces
start and end days with start and end years. See the following JSON example and table, which shows
all available parameters for this event coordinator.

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

{{ read_csv('../csv/campaign-nchoosereventcoordinatorsti.csv', keep_default_na=False) }}

```json
{
    "Use_Defaults": 1,
    "Events": [{
        "class": "CampaignEvent",
        "Start_Day": 1,
        "Nodeset_Config": {
            "class": "NodeSetAll"
        },
        "Event_Coordinator_Config": {
            "class": "NChooserEventCoordinatorSTI",
            "Distributions": [{
                    "Start_Year": 1961,
                    "End_Year": 1961.25,
                    "Property_Restrictions_Within_Node": [],
                    "Age_Ranges_Years": [{
                        "Min": 10,
                        "Max": 19
                    }, {
                        "Min": 40,
                        "Max": 49
                    }],
                    "Num_Targeted": [600000, 300000]
                },
                {
                    "Start_Year": 1963,
                    "End_Year": 1963.5,
                    "Property_Restrictions_Within_Node": [],
                    "Age_Ranges_Years": [{
                        "Min": 20,
                        "Max": 29
                    }, {
                        "Min": 50,
                        "Max": 59
                    }],
                    "Num_Targeted_Males": [400000, 200000],
                    "Num_Targeted_Females": [300000, 100000]
                },
                {
                    "Start_Year": 1965,
                    "End_Year": 1965.25,
                    "Property_Restrictions_Within_Node": [],
                    "Age_Ranges_Years": [{
                        "Min": 10,
                        "Max": 19
                    }, {
                        "Min": 30,
                        "Max": 39
                    }, {
                        "Min": 50,
                        "Max": 59
                    }],
                    "Num_Targeted_Males": [600000, 400000, 200000],
                    "Num_Targeted_Females": [500000, 300000, 100000]
                }
            ],
            "Intervention_Config": {
                "class": "ControlledVaccine",
                "Cost_To_Consumer": 10,
                "Vaccine_Type": "AcquisitionBlocking",
                "Vaccine_Take": 1.0
            }
        }
    }]
}
```
