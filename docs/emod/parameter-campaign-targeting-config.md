# Targeting_Config classes

The following classes can be used to enhance the selection of people when distributing interventions.
Most event coordinators and node-level interventions that distribute interventions to people have a
parameter called **Targeting_Config**.  This allows you to not only target individuals based on their
gender, age, and **IndividualProperties** (See [NodeProperties and IndividualProperties](parameter-demographics.md#nodeproperties-and-individualproperties) parameters for more information),
but also on things such as whether or not they have a particular intervention or are in a relationship.

> **NOTE:**
> Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
> Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
> that parameter.
>
> EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.
>
> JSON format does not permit comments, but you can add "dummy" parameters to add contextual
> information to your files. Any keys that are not EMOD parameter names will be ignored by the
> model.

Below is a simple example where we want to distribute a vaccine to 20% of the people that do not
already have the vaccine on the 100th day of the simulation.

```json
{
    "class": "CampaignEvent",
    "Start_Day": 100,
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 0.2,
        "Targeting_Config": {
            "class": "HasIntervention",
            "Is_Equal_To": 0,
            "Intervention_Name": "MyVaccine"
        },
        "Intervention_Config": {
            "class": "SimpleVaccine",
            "Intervention_Name" : "MyVaccine",
            "Cost_To_Consumer": 1,
            "Vaccine_Take": 1,
            "Vaccine_Type": "AcquisitionBlocking",
            "Waning_Config": {
                "class": "WaningEffectConstant",
                "Initial_Effect" : 1.0
            }
        }
    }
}
```

Below is a slightly more complicated example where we want to distribute a diagnostic to people
that are either high risk or have not been vaccinated.

```json
{
    "class": "CampaignEvent",
    "Start_Day": 100,
    "Nodeset_Config": {
        "class": "NodeSetAll"
    },
    "Event_Coordinator_Config": {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Target_Demographic": "Everyone",
        "Demographic_Coverage": 0.2,
        "Targeting_Config": {
            "class" : "TargetingLogic",
            "Logic" : [
                [
                    {
                        "class": "HasIntervention",
                        "Is_Equal_To": 0,
                        "Intervention_Name": "MyVaccine"
                    }
                ],
                [
                    {
                        "class": "HasIP",
                        "Is_Equal_To": 1,
                        "IP_Key_Value": "Risk:HIGH"
                    }
                ]
            ]
        },
        "Intervention_Config": {
            "class": "SimpleDiagnostic",
            "Treatment_Fraction": 1.0,
            "Base_Sensitivity": 1.0,
            "Base_Specificity": 1.0,
            "Event_Or_Config": "Event",
            "Positive_Diagnosis_Event": "TestedPositive"
        }
    }
}
```

## HasIntervention

This determines whether or not the individual has an intervention with the given name.  This will only
work for interventions that persist like **SimpleVaccine** and **DelayedIntervention**.  It will not work for
interventions like **BroadcastEvent** since it does not persist.

### Configuration

### Example

Select the person if they do NOT have the MyVaccine intervention.

```json
"Targeting_Config": {
    "class": "HasIntervention",
    "Is_Equal_To": 0,
    "Intervention_Name": "MyVaccine"
}
```

## HasIP

This determines if the person has a particular value of a particular **IndividualProperties** (IP).
This is especially needed when determining if a partner has a particular IP (see **HasRelationship**).

### Configuration

### Example

Select the person if their **Risk** property is HIGH.

```json
"Targeting_Config": {
    "class": "HasIP",
    "Is_Equal_To": 1,
    "IP_Key_Value": "Risk:HIGH"
}
```

## TargetingLogic

In some cases, the you need to logically combine multiple restrictions.  In these situations,
you should use the **TargetingLogic** class where you can "and" and "or" the different questions.

NOTE: Each element is independent and is being asked of the individual in question.  For questions
that are about a partner of the individual, all of the qualifiers for that partner must be in the
element.  This will ensure that there is one partner that has all of the qualifications.  Otherwise,
you could have a situation where one partner satisfies one qualification and another partner
satisfies a different one, but no partner has all of the qualifications.

### Configuration

### Example

Select the person if they do not have the MyVaccine intervention OR do not have their **Risk** property set to HIGH.
Notice that **Logic** 2x1 where the first dimention contains two arrays with one JSON object.  These two
arrays are OR'd together.

```json
"Targeting_Config": {
    "class" : "TargetingLogic",
    "Logic" : [
        [
            {
                "class": "HasIntervention",
                "Is_Equal_To": 0,
                "Intervention_Name": "MyVaccine"
            }
        ],
        [
            {
                "class": "HasIP",
                "Is_Equal_To": 0,
                "IP_Key_Value": "Risk:HIGH"
            }
        ]
    ]
}
```

Select the person if they do not have the MyVaccine intervention AND do not have their **Risk** property set to HIGH.
Notice that **Logic** is 1x2 where the first dimension contains a single array with two JSON objects.  These two
objects are AND'd together.

```json
"Targeting_Config": {
    "class" : "TargetingLogic",
    "Logic" : [
        [
            {
                "class": "HasIntervention",
                "Is_Equal_To": 0,
                "Intervention_Name": "MyVaccine"
            },
            {
                "class": "HasIP",
                "Is_Equal_To": 0,
                "IP_Key_Value": "Risk:HIGH"
            }
        ]
    ]
}
```

## IsCircumcised

Select the individual based on whether or not they are circumcised.

### Configuration

### Example

Select the person if they are NOT circumcised.

```json
"Targeting_Config": {
    "class": "IsCircumcised",
    "Is_Equal_To": 0
}
```

## IsHivPositive

Select the individual based on whether or not they have HIV.

### Configuration

### Example

Select the person if they have HIV, have been tested, and have tested positive.  The 'NA' for **And_Has_Received_Positive_Results** means we are not concerned whether or not they received the results.

```json
"Targeting_Config": {
    "class" : "IsHivPositive",
    "Is_Equal_To": 1,
    "And_Has_Ever_Been_Tested": "YES",
    "And_Has_Ever_Tested_Positive": "YES",
    "And_Has_Received_Positive_Results": "NA"
}
```

## IsOnART

Select the individual based on whether or not they are actively on ART.

### Configuration

### Example

Select the person if they are NOT on ART.

```json
"Targeting_Config": {
    "class" : "IsOnART",
    "Is_Equal_To": 0
}
```

## IsPostDebut

Select the individual based on whether or not they have reached sexual debut.

### Configuration

### Example

Select the person if they have reached sexual debut.

```json
"Targeting_Config": {
    "class" : "IsPostDebut",
    "Is_Equal_To": 1
}
```

## IsPregnant

Select the individual based on whether or not they are pregnant.

### Configuration

### Example

Select the person if they are pregnant.

```json
"Targeting_Config": {
    "class" : "IsPregnant",
    "Is_Equal_To": 1
}
```

## HasBeenOnArtMoreOrLessThanNumMonths

Determine if the individual has been on ART for less than "num" months.  It will be false if the individual is not on ART.  The test will be strictly less than.

### Configuration

### Example

Select the person if they have been on ART for more than 6 months.

```json
"Targeting_Config": {
    "class" : "HasBeenOnArtMoreOrLessThanNumMonths",
    "Is_Equal_To": 1,
    "More_Or_Less": "MORE",
    "Num_Months": 6
}
```

## HasMoreOrLessThanNumPartners

Determine if the individual has more or less than a specified number of active partners.  This includes relationships that are paused due to migration.  This test is strictly more or less than.

### Configuration

### Example

Select the person if they have more than eight partners of any type.

```json
"Targeting_Config": {
    "class": "HasMoreOrLessThanNumPartners",
    "Is_Equal_To": 1,
    "Of_Relationship_Type": "NA",
    "Num_Partners": 8,
    "More_Or_Less": "MORE"
}
```

Select the person if they have less than three transitory partners.

```json
"Targeting_Config": {
    "class": "HasMoreOrLessThanNumPartners",
    "Is_Equal_To": 1,
    "Of_Relationship_Type": "TRANSITORY",
    "Num_Partners": 3,
    "More_Or_Less": "LESS"
}
```

## HasHadMultiplePartnersInLastNumMonths

Determine if the individual has had more than one relationship in the last "Num" months.
This could constitute as "high-risk" behavior.   The goal is to target people that have
had coital acts with more than one person during the last X months. This would count current
relationships, relationships that started in the last X months, and relationships that have
ended in the last X months.  Basically, all the relationships that have been active at
some point during the last X months.  NOTE:  This only counts unique partners.  Two
relationships with the same person during the time period will count as one.

### Configuration

### Example

Select the person if they have NOT had multiple INFORMAL partners in the last six months.

```json
"Targeting_Config": {
    "class" : "HasHadMultiplePartnersInLastNumMonths",
    "Is_Equal_To": 0,
    "Num_Months_Type": "SIX_MONTHS",
    "Of_Relationship_Type": "INFORMAL"
}
```

Select the person if they have had multiple partners in the last year but not necessarily at the same time.

```json
"Targeting_Config": {
    "class" : "HasHadMultiplePartnersInLastNumMonths",
    "Is_Equal_To": 1,
    "Num_Months_Type": "TWELVE_MONTHS",
    "Of_Relationship_Type": "NA"
}
```

## HasCd4BetweenMinAndMax

Determine if the individual has a CD4 count that is between "min" and "max".  The test is inclusive for "min" and exclusive for "max".

### Configuration

### Example

Select the person if their CD4 is currently between 530 and 600.  In other words, 530 <= current CD4 < 600.

```json
"Targeting_Config": {
    "class" : "HasCd4BetweenMinAndMax",
    "Is_Equal_To": 1,
    "Min_CD4": 530.0,
    "Max_CD4": 600.0
}
```

## HasRelationship

This is used to select people who have a partner/relationship that meets certain qualifications.
Except for when **That_Recently** = ENDED, the restriction will be considering all of the relationships.

### Configuration

### Examples

Select the person if they have a partner that has HIV.

```json
"Targeting_Config": {
    "class" : "HasRelationship",
    "Is_Equal_To": 1,
    "Of_Relationship_Type":  "NA",
    "That_Recently":  "NA",
    "That_Recently_Ended_Due_To": "NA"
    "With_Partner_Who" : {
        "class" : "IsHivPositive",
        "Is_Equal_To" : 1
    }  
}
```

Select the person if they have recently started a marital relationship with someone who is taking ART.

```json
"Targeting_Config": {
    "class" : "HasRelationship",
    "Is_Equal_To": 1,
    "Of_Relationship_Type":  "MARITAL",
    "That_Recently":  "STARTED",
    "That_Recently_Ended_Due_To": "NA"
    "With_Partner_Who" : {
        "class" : "IsOnART",
        "Is_Equal_To" : 1
    }
}
```

Distribute a NodeLevelHealthTriggeredIV to a person if they recently ended a marital relationship because their partner died.

```json
{    
    "class": "NodeLevelHealthTriggeredIV",
    "Trigger_Condition_List": [
        "ExitedRelationship"
    ],
    "Targeting_Config": {
        "class" : "HasRelationship",
        "Is_Equal_To": 1,
        "Of_Relationship_Type":  "MARITAL",
        "That_Recently":  "ENDED",
        "That_Recently_Ended_Due_To": "PARTNER_DIED",
        "With_Partner_Who" : {
        }
    },
}
```

Test a person for HIV if they have recently ended a martial relationship where the partner had tested positive for HIV.

```json
{
    "class": "CampaignEvent",
    "Start_Day": 140,
    "Nodeset_Config": { "class": "NodeSetAll" },
    "Event_Coordinator_Config":
    {
        "class": "StandardInterventionDistributionEventCoordinator",
        "Intervention_Config":
        {
            "class": "NodeLevelHealthTriggeredIV",
            "Target_Demographic": "Everyone",
            "Trigger_Condition_List": [
                "ExitedRelationship"
            ],
            "Targeting_Config" :
            {
                "class" : "HasRelationship",
                "Is_Equal_To": 1,
                "Of_Relationship_Type":  "MARITAL",
                "That_Recently":  "ENDED",
                "That_Recently_Ended_Due_To": "NA"
                "With_Partner_Who" : {
                    "class" : "IsHivPositive",
                    "Is_Equal_To" : 1,
                    "And_Has_Ever_Been_Tested": "YES",
                    "And_Has_Ever_Tested_Positive": "YES",
                    "And_Has_Received_Positive_Results": "NA"
                }
            },
            "Actual_IndividualIntervention_Config": {
                "class": "HIVRapidHIVDiagnostic"
                "Positive_Diagnosis_Event": "Tested_Positive",
                "Negative_Diagnosis_Event": "Tested_Negative"
            }
        }
    }
}
```

Imagine you want to select people to stop using PrEP because they either don't have any HIV postive
partners or their partner is virally surpressed because they been on ART for more than 6 months.
You would then want to select individuals that are HIV Negative, are on PrEP, and either have no
HIV Positive partners or their HIV Positive partners have been on ART for more than 6 months.

Notice how **HasRelationship** is "or'ing" HIV positive and not on ART with HIV postive and
on ART less than 6 months and then taking the negative of that.  Something like:

* not( (HIV+ & not OnART) or (HIV+ & (OnART < 6 monts) )

```json
"Targeting_Config" :
{
   "class" : "TargetingLogic",
   "Logic":
   [
      [
         {
            "class" : "IsHivPositive",
            "Is_Equal_To" : 0
         },
         {
            "class" : "HasIntervention",
            "Intervention_Name" : "PrEP",
            "Is_Equal_To" : 1
         },
         {
            "class" : "HasRelationship",
            "Is_Equal_To" : 0
            "With_Partner_Who" :
            {
               "class" : "TargetingLogic",
               "Logic":
               [
                  [
                     {
                        "class" : "IsHivPositive",
                        "Is_Equal_To" : 1,
                        "And_Has_Ever_Tested_Positive": "YES"
                     },
                     {
                        "class" : "IsOnART",
                        "Is_Equal_To" : 0
                     }
                  ],
                  [
                     {
                        "class" : "IsHivPositive",
                        "Is_Equal_To" : 1,
                        "And_Has_Ever_Tested_Positive": "YES"
                     },
                     {
                        "class" : "HasBeenOnArtMoreOrLessThanNumMonths",
                        "Is_Equal_To" : 1,
                        "More_Or_Less" : "LESS",
                        "Num_Months" : 6.0
                     }
                  ]
               ]
            }
         }
      ]
   ]
}
```
