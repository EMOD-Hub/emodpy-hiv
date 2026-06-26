# ARTMortalityTable

The **ARTMortalityTable** intervention class allows the user to modify an individual’s life expectancy 
based on different levels of ART adherence; the user defines parameters for age, CD4 count, and time on ART 
in a multi-dimensional table which is then used to determine mortality rate. Note: If you have different adherence levels for each gender, then you will need to configure your campaign to distribute an **ARTMortalityTable** for each gender and adherence level.

Additional considerations when using this intervention:

* The model will not allow someone who is HIV negative to be put on ART.
* A person who has not previously been on ART is considered to be 'starting ART' at the time this intervention is applied; the model will track this start time/duration.
* If a person is already on ART from another intervention, receiving a second ART intervention will have no effect.
* If a person is on already ART and receives the [ARTMortalityTable](parameter-campaign-individual-artmortalitytable.md) intervention, the original ART start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration since starting ART will not change; it will continue to increase.
* If a person is on ART and receives the [ARTDropout](parameter-campaign-individual-artdropout.md) intervention, the person will go off ART and the duration will be reset; if receiving a new ART intervention, this new start time/duration will be used in any calculations.

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

{{ read_csv('../csv/campaign-artmortalitytable.csv', keep_default_na=False) }}

```json
{
    "class": "ARTMortalityTable",
    "Cost_To_Consumer" : 1,
    "ART_Multiplier_On_Transmission_Prob_Per_Act" : 0.08,
    "ART_Is_Active_Against_Mortality_And_Transmission" : 1,
    "Days_To_Achieve_Viral_Suppression" : 183.0,
    "ART_Duration_Bins" : [ 0, 6, 12, 24, 36 ],
    "Age_Bins" : [ 0, 40 ],
    "CD4_Count_Bins" : [ 0, 25, 74.5, 149.5, 274.5, 424.5, 624.5 ],
    "MortalityTable" :
    [
        [
            [ 0.2015, 0.2015, 0.1128, 0.0625, 0.0312, 0.0206, 0.0162 ],
            [ 0.0875, 0.0875, 0.0490, 0.0271, 0.0136, 0.0062, 0.0041 ]
        ],
        [
            [ 0.0271, 0.0271, 0.0184, 0.0149, 0.0074, 0.0048, 0.0048 ],
            [ 0.0171, 0.0171, 0.0116, 0.0094, 0.0047, 0.0030, 0.0030 ]
        ],
        [
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ],
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ]
        ],
        [
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ],
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ]
        ],
        [
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ],
            [ 0.0119, 0.0119, 0.0081, 0.0066, 0.0033, 0.0033, 0.0033 ]
        ]
    ]
}
```
