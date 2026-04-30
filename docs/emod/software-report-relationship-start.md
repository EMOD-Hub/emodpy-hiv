# RelationshipStart

The relationship formation report (RelationshipStart.csv)  provides information about each relationship
and its members, evaluated at the time of relationship formation. The report includes the relationship
type, start time, scheduled end time, and detailed information about each participant: ID, gender, age,
infection status, circumcision status for males, co-infections, number of relationships (active, recent,
lifetime), and individual properties. The male in the relationship is indicated on the report as participant
"A", and the female as participant "B".

## Configuration

To generate the report, the following parameters must be configured in the config.json file:

```json
{
    "Report_Relationship_Start": 1,
    "Report_Relationship_Start_Start_Year": 1900,
    "Report_Relationship_Start_End_Year": 2200,
    "Report_Relationship_Start_Max_Age_Years": 60,
    "Report_Relationship_Start_Min_Age_Years": 20,
    "Report_Relationship_Start_Node_IDs_Of_Interest": [ 1, 2, 3 ],
    "Report_Relationship_Start_Include_Other_Relationship_Statistics": 1,
    "Report_Relationship_Start_Individual_Properties": ["InterventionStatus"],
    "Report_Relationship_Start_Must_Have_IP_Key_Value": "Risk:HIGH",
    "Report_Relationship_Start_Must_Have_Intervention": "",
}
```

## Output file data

The output report will contain the following information.

## Example

The following is an example of a RelationshipStart.csv report:

{{ read_csv('RelationshipStart-Example.csv') }}
