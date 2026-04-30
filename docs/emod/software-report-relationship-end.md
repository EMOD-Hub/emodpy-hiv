# RelationshipEnd

The relationship dissolution report (RelationshipEnd.csv) provides detailed information about each
relationship and its members, evaluated at the time of relationship dissolution. The report includes
the relationship type, start time, scheduled end time, actual end time (which may differ from the
scheduled end time, for instance, due to the death of a partner), and information about
each participant.

## Configuration

To generate the report, set the **Report_Relationship_End** parameter to 1 in config.json file.

## Output file data

The output report will contain the following information.

## Example

The following is an example of a RelationshipEnd.csv report:

{{ read_csv('RelationshipEnd-Example.csv') }}
