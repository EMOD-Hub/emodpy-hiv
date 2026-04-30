# ReportRelationshipMigrationTracking

The relationship migration tracking report (ReportRelationshipMigrationTracking.csv) provides information about the relationships a person has when they are migrating. It will give information when they are leaving and entering a node. When leaving a node, the information will be about the status of the relationships just before they leave. When entering the new node, the information will be about the relationships that have been updated. For example, a person could leave with a relationship paused, find their partner in the new node, and get their relationship back to normal. This helps to know about how the status of the relationships have changed—migrated, paused, or terminated.

The person initiating a migration event will first have their relationships listed in the state before migrating starts. If a partner is asked to migrate with them, then that partner's relationships will also be listed. When the people are immigrating into the new node, the list of relationships that are continuing in the new node will be listed. Any migrated partner should only have the relationship with the partner initiating migration. Their other relationships will have been terminated.

## Configuration

To generate this report, the following parameters must be configured in the custom_reports.json file:

```json
{
    "Reports": [
        {
            "Filename_Suffix": "example",
            "Start_Year": 1900,
            "End_Year": 2200,
            "Node_IDs_Of_Interest":[ 1, 2, 3 ],
            "Min_Age_Years": 20,
            "Max_Age_Years": 90,
            "Must_Have_IP_Key_Value": "",
            "Must_Have_Intervention": "",
            "class": "ReportRelationshipMigrationTracking"
        }
    ],
    "Use_Defaults": 1
}
```

## Output file data

The output report will contain the following information.

### Data columns

## Example

The following is an example of a ReportRelationshipMigrationTracking.csv file.

{{ read_csv('ReportRelationshipMigrationTracking-Example.csv') }}
