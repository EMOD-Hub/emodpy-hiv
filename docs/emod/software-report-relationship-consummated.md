# RelationshipConsummated

The coital act report (RelationshipConsummated.csv) provides detailed information about each
coital act that occurs during the simulation. The report includes unique identifiers for each coital
act and relationship; the relationship type, number of acts, whether a condom was used, and whether
transmission occurred; and detailed information about each participant, including age, gender, infection status,
circumcision status, co-infection status, and treatment status. Each participant in a relationship is
referred to as either participant "A" or participant "B".

One row of data is returned per coital act, and results are ordered on a per-relationship basis. Note:
if a person is engaged in coital acts in multiple relationships during a time step, the order of those
acts is unknown, only in which relationship they occurred. Additionally, if a person gets infected during
a time step, they cannot re-transmit that infection during the same time step. The report does record
during which coital act transmission occurred.

If an uninfected person has coital acts with multiple infected partners during a time step, all
acts with the possibility of transmission are randomly ordered, so that the person has an equal chance
of getting infected from any one of their partners. The probability of transmission from any one of
these coital acts is still determined by the simulation parameters (number of acts, acquisition multipliers, etc.)

## Configuration

To generate the report, the following parameters must be configured in the config.json file:

```json
{
    "Report_Coital_Acts": 1,
    "Report_Coital_Acts_Start_Year": 2000,
    "Report_Coital_Acts_End_Year": 2050,
    "Report_Coital_Acts_Node_IDs_Of_Interest": [ 1, 2, 3 ],
    "Report_Coital_Acts_Min_Age_Years": 30,
    "Report_Coital_Acts_Max_Age_Years": 90,
    "Report_Coital_Acts_Must_Have_IP_Key_Value": "Risk:LOW",
    "Report_Coital_Acts_Must_Have_Intervention": "",
    "Report_Coital_Acts_Relationship_Type": "MARITAL",
    "Report_Coital_Acts_Has_Intervention_With_Name": "",
    "Report_Coital_Acts_Individual_Properties": [],
    "Report_Coital_Acts_Partners_With_IP_Key_Value": ["Risk:HIGH"],
}
```

## Output file data

The output report will contain the following information.

## Example

The following is an example of a RelationshipConsummated.csv report:

*See parameter table: [RelationshipConsummated-Example.csv](RelationshipConsummated-Example.csv)*
