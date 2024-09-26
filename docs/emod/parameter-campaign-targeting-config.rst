========================
Targeting_Config classes
========================

The following classes can be used to enhance the selection of people when distributing interventions.
Most event coordinators and node-level interventions that distribute interventions to people have a
parameter called **Targeting_Config**.  This allows you to not only target individuals based on their
gender, age, and **IndividualProperties** (See :ref:`demo-properties` parameters for more information),
but also on things such as whether or not they have a particular intervention or are in a relationship.

.. include:: ../reuse/warning-case.txt

Below is a simple example where we want to distribute a vaccine to 20% of the people that do not
already have the vaccine on the 100th day of the simulation.

.. code-block:: json

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

Below is a slightly more complicated example where we want to distribute a diagnostic to people
that are either high risk or have not been vaccinated.

.. code-block:: json

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

.. contents:: Contents
   :local:

HasIntervention
===============

This determines whether or not the individual has an intervention with the given name.  This will only
work for interventions that persist like **SimpleVaccine** and **DelayedIntervention**.  It will not work for
interventions like **BroadcastEvent** since it does not persist.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Intervention_Name**, string, NA, NA, """""", "The name of the intervention the person should have.  This cannot be an empty string but should be either the name of the class or the name given to the intervention of interest using the parameter Intervention_Name.  EMOD does not verify that this name exists."

Example
-------

Select the person if they do NOT have the MyVaccine intervention.

.. code-block:: json

    "Targeting_Config": {
        "class": "HasIntervention",
        "Is_Equal_To": 0,
        "Intervention_Name": "MyVaccine"
    }


HasIP
=====

This determines if the person has a particular value of a particular **IndividualProperties** (IP).
This is especially needed when determining if a partner has a particular IP (see **HasRelationship**).

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **IP_Key_Value**, string, NA, NA, """""", "An **IndividualProperties** Key:Value pair where the key/property name and one of its values is separated by a colon (':')."
    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    

Example
-------

Select the person if their **Risk** property is HIGH.

.. code-block:: json

    "Targeting_Config": {
        "class": "HasIP",
        "Is_Equal_To": 1,
        "IP_Key_Value": "Risk:HIGH"
    }


TargetingLogic
==============

In some cases, the you need to logically combine multiple restrictions.  In these situations,
you should use the **TargetingLogic** class where you can "and" and "or" the different questions.

NOTE: Each element is independent and is being asked of the individual in question.  For questions
that are about a partner of the individual, all of the qualifiers for that partner must be in the
element.  This will ensure that there is one partner that has all of the qualifications.  Otherwise,
you could have a situation where one partner satisfies one qualification and another partner
satisfies a different one, but no partner has all of the qualifications.


Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Logic**, 2D array of JSON objects, NA, NA, [], "This is a two-dimensional array of JSON objects.  The elements of the inner array will be AND'd together while the arrays themselves will be OR'd.  This is similar to **Property_Restrictions_Within_Node**.  This array and the inner arrays cannot be empty."

Example
-------
Select the person if they do not have the MyVaccine intervention OR do not have their **Risk** property set to HIGH.
Notice that **Logic** 2x1 where the first dimention contains two arrays with one JSON object.  These two
arrays are OR'd together.

.. code-block:: json

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

Select the person if they do not have the MyVaccine intervention AND do not have their **Risk** property set to HIGH.
Notice that **Logic** is 1x2 where the first dimension contains a single array with two JSON objects.  These two
objects are AND'd together.

.. code-block:: json

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


IsCircumcised
=============

Select the individual based on whether or not they are circumcised.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."

Example
-------
Select the person if they are NOT circumcised.

.. code-block:: json

    "Targeting_Config": {
        "class": "IsCircumcised",
        "Is_Equal_To": 0
    }


IsHivPositive
=============

Select the individual based on whether or not they have HIV.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **And_Has_Ever_Been_Tested**, enum, NA, NA, "'NA'", "If the user sets this Enum to 'YES', then the individual's true infection status must equal **Is_Equal_To** and the person must have been tested at least once.  Notice that this only tells if the person has been tested, NOT that they tested positive.  If set to 'NA' (default), then do not include this as part of the check. Possible values are 'YES', 'NO', and 'NA'."
    **And_Has_Ever_Tested_Positive**, enum, NA, NA, "'NA'", "If the user sets this Enum to 'YES', then the individual's true infection status must equal **Is_Equal_To** and the person must have tested POSITIVE at least once.  Notice that this is different than just having been tested.  However, it does not say the person received the results.  If set to 'NA' (default), then do not include this as part of the check. Possible values are 'YES', 'NO', and 'NA'."
    **And_Has_Recieved_Positive_Results**, enum, NA, NA, "'NA'", "If the user sets this Enum to 'YES', then the individual's true infection status must equal **Is_Equal_To** and the last test result received was positive. Possible values are 'YES', 'NO', and 'NA' (default)."

Example
-------
Select the person if they have HIV, have been tested, and have tested positive.  The 'NA' for **And_Has_Received_Positive_Results** means we are not concerned whether or not they received the results.

.. code-block:: json

    "Targeting_Config": {
        "class" : "IsHivPositive",
        "Is_Equal_To": 1,
        "And_Has_Ever_Been_Tested": "YES",
        "And_Has_Ever_Tested_Positive": "YES",
        "And_Has_Received_Positive_Results": "NA"
    }

IsOnART
=======

Select the individual based on whether or not they are actively on ART.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."

Example
-------
Select the person if they are NOT on ART.

.. code-block:: json

    "Targeting_Config": {
        "class" : "IsOnART",
        "Is_Equal_To": 0
    }

IsPostDebut
===========

Select the individual based on whether or not they have reached sexual debut.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."

Example
-------
Select the person if they have reached sexual debut.

.. code-block:: json

    "Targeting_Config": {
        "class" : "IsPostDebut",
        "Is_Equal_To": 1
    }

IsPregnant
==========

Select the individual based on whether or not they are pregnant.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."

Example
-------
Select the person if they are pregnant.

.. code-block:: json

    "Targeting_Config": {
        "class" : "IsPregnant",
        "Is_Equal_To": 1
    }

HasBeenOnArtMoreOrLessThanNumMonths
===================================

Determine if the individual has been on ART for less than "num" months.  It will be false if the individual is not on ART.  The test will be strictly less than.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Num_Months**, float, 0, 1500, 1500, "This is the number of months that will be used in the test.  The individual's duration on ART must be more or less than this value.  NOTE: 1500 months is about 12 months / year * 125 years of max age"
    **More_Or_Less**, enum, NA, NA, LESS, "This is used to determine if the check should be less than or greater than. Possible values are 'MORE' or 'LESS'."

Example
-------
Select the person if they have been on ART for more than 6 months.

.. code-block:: json

    "Targeting_Config": {
        "class" : "HasBeenOnArtMoreOrLessThanNumMonths",
        "Is_Equal_To": 1,
        "More_Or_Less": "MORE",
        "Num_Months": 6
    }


HasMoreOrLessThanNumPartners
============================

Determine if the individual has more or less than a specified number of active partners.  This includes relationships that are paused due to migration.  This test is strictly more or less than.


Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Num_Partners**, integer, 0, 62, 0, "This parameter allows the user to set the number of active partners/relationships that the individual must have more or less of."
    **Of_Relationship_Type**, enum, NA, NA, "'NA'", "If the user sets this value to one of the four specific types (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must have more or less relationships of this type.  When the value is set to 'NA' (default), then it will count the relationships regardless of type."
    **More_Or_Less**, enum, NA, NA, LESS, "This is used to determine if the check should be less than or greater than. Possible values are 'LESS' or 'MORE'."

Example
-------
Select the person if they have more than eight partners of any type.

.. code-block:: json

    "Targeting_Config": {
        "class": "HasMoreOrLessThanNumPartners",
        "Is_Equal_To": 1,
        "Of_Relationship_Type": "NA",
        "Num_Partners": 8,
        "More_Or_Less": "MORE"
    }

Select the person if they have less than three transitory partners.

.. code-block:: json

    "Targeting_Config": {
        "class": "HasMoreOrLessThanNumPartners",
        "Is_Equal_To": 1,
        "Of_Relationship_Type": "TRANSITORY",
        "Num_Partners": 3,
        "More_Or_Less": "LESS"
    }

HasHadMultiplePartnersInLastNumMonths
=====================================

Determine if the individual has had more than one relationship in the last "Num" months.
This could constitute as "high-risk" behavior.   The goal is to target people that have
had coital acts with more than one person during the last X months. This would count current
relationships, relationships that started in the last X months, and relationships that have
ended in the last X months.  Basically, all the relationships that have been active at
some point during the last X months.  NOTE:  This only counts unique partners.  Two
relationships with the same person during the time period will count as one.

Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Num_Months_Type**, enum, NA, NA, THREE_MONTHS, "This parameter allows the user to set the maximum number of months from the current day to consider if the individual had multiple relationships. Possible values are 'THREE_MONTHS', 'SIX_MONTHS', 'NINE_MONTHS', or 'TWELVE_MONTHS'."
    **Of_Relationship_Type**, enum, NA, NA, "'NA'", "If the user sets this value to one of the four specific types (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must have more or less relationships of this type.  When the value is set to 'NA' (default), then it will count the relationships regardless of type."

Example
-------
Select the person if they have NOT had multiple INFORMAL partners in the last six months.

.. code-block:: json

    "Targeting_Config": {
        "class" : "HasHadMultiplePartnersInLastNumMonths",
        "Is_Equal_To": 0,
        "Num_Months_Type": "SIX_MONTHS",
        "Of_Relationship_Type": "INFORMAL"
    }

Select the person if they have had multiple partners in the last year but not necessarily at the same time.

.. code-block:: json

    "Targeting_Config": {
        "class" : "HasHadMultiplePartnersInLastNumMonths",
        "Is_Equal_To": 1,
        "Num_Months_Type": "TWELVE_MONTHS",
        "Of_Relationship_Type": "NA"
    }


HasCd4BetweenMinAndMax
======================

Determine if the individual has a CD4 count that is between "min" and "max".  The test is inclusive for "min" and exclusive for "max".


Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Min_CD4**, float, 0, 1999, 0, "The minimum value of the test range.  The individual's CD4 can be equal to this value to be considered 'between'."
    **Max_CD4**, float, 1, 2000, 2000, "The maximum value of the test range.  The individual's CD4 must be strictly less than this value to be considered 'between'."

Example
-------
Select the person if their CD4 is currently between 530 and 600.  In other words, 530 <= current CD4 < 600.

.. code-block:: json

    "Targeting_Config": {
        "class" : "HasCd4BetweenMinAndMax",
        "Is_Equal_To": 1,
        "Min_CD4": 530.0,
        "Max_CD4": 600.0
    }


HasRelationship
===============

This is used to select people who have a partner/relationship that meets certain qualifications.
Except for when **That_Recently** = ENDED, the restriction will be considering all of the relationships.


Configuration
-------------

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    **Is_Equal_To**, boolean, 0, 1, 1, "This is used to determine if the individual is selected based on the result of the value of the question. Set to 1 for true and 0 for false."
    **Of_Relationship_Type**, enum, NA, NA, "'NA'", "If the user sets this value to one of the four specific types (TRANSITORY, INFORMAL, MARITAL, COMMERCIAL), then the individual must have more or less relationships of this type.  When the value is set to NA (default), then it will count the relationships regardless of type."
    **That_Recently**, enum, NA, NA, "'NA'", "This parameter is used if the relationship being considered must have recently been started or ended. Possible values are:

    NA (Default)
        Do no consider **That_Recently** in the selection process.
    STARTED
        Only consider relationships that have started within one time-step. One should note that the relationships you see will depend on whether you are using **NodeLevelHealthTriggeredIV** (NLHTIV) or an event coordinator. NLHTIV and the individuals will be updated after new relationships have been created so with this feature, NLHTIV will see relationships in the previous time step as well as the current time step. An event coordinator executes BEFORE new relationships are formed so it will only see the relationships created in the previous time step.
    ENDED
        Check the status of the relationship that just ended. Note: This can only be used with **NodeLevelHealthTriggeredIV** listening for the 'ExitedRelationship' event."
    **With_Partner_Who**, JSON object, NA, NA, {}, "Given that the parameters about the relationship are true, this parameter is used to look at the partner of the relationship.  It is a **Targeting_Config** so one uses the same classes to query the partner.  For example, to find out if person has a partner with HIV, you could use **IsHivPositive**."
    **That_Recently_Ended_Due_To**, enum, NA, NA, "'NA'", "If **That_Recently** is set to 'ENDED', this is used to look at the reason the relationship ended. Possible values are:

    NA (Default)
        The relationship has not been terminated.
    BROKEUP
        The relationship ended due to the duration settings.
    SELF_MIGRATING
        One of the partners in the relationship has decided to migrate and so the relationship is terminated. Note: the user can control what happens to a relationship when there is migration; it does not have to terminate.
    PARTNER_MIGRATING
        The relationship is being terminated because one of the partners has another partner that is migrating. For example, a married couple is moving because the wife got a new job. The husband must terminate his other relationships with 'PARTNER_MIGRATING'.
    PARTNER_DIED
        One of the partners died so the relationship was terminated.
    PARTNER_TERMINATED
        This happens when the couple is separated due to migration and one of the partners decides to terminate the relationship."

Examples
--------
Select the person if they have a partner that has HIV.

.. code-block:: json

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

Select the person if they have recently started a marital relationship with someone who is taking ART.

.. code-block:: json

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

Distribute a NodeLevelHealthTriggeredIV to a person if they recently ended a marital relationship because their partner died.

.. code-block:: json

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

Test a person for HIV if they have recently ended a martial relationship where the partner had tested positive for HIV.

.. code-block:: json

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

Imagine you want to select people to stop using PrEP because they either don't have any HIV postive
partners or their partner is virally surpressed because they been on ART for more than 6 months.
You would then want to select individuals that are HIV Negative, are on PrEP, and either have no
HIV Positive partners or their HIV Positive partners have been on ART for more than 6 months.

Notice how **HasRelationship** is "or'ing" HIV positive and not on ART with HIV postive and
on ART less than 6 months and then taking the negative of that.  Something like:

* not( (HIV+ & not OnART) or (HIV+ & (OnART < 6 monts) )

.. code-block:: json

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

