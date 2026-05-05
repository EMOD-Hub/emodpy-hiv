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

| Data channel | Data type | Description |
|---|---|---|
| Rel_ID | integer | A unique identifier for the relationship, different from the IDs of the participants. |
| Node_ID | integer | The identification number for the node. |
| Rel_start_time | float | The time (in days) during the simulation when the relationship started. |
| Rel_scheduled_end_time | float | The time (in days) during the simulation when the relationship was scheduled to end. The duration of the relationship is dependent on the relationship type; configure by updating the **Duration_Weibull_Heterogeneity** and **Duration_Weibull_Scale** parameters in the demographics file. See [parameter-demographics](parameter-demographics.md) for details. |
| Rel_actual_end_time | float | The actual end time of the relationship, in days since the start of the simulation. This may differ from the scheduled end time due to the death of a partner, migration, etc. |
| Rel_type (0 = TRANSITORY; 1 = INFORMAL; 2 = MARITAL; 3 = COMMERCIAL) | integer | The type of relationship formed between the participants. Values for 0-3 as indicated in the header. |
| Is_rel_outside_PFA | boolean | Indicates whether or not the relationship was created by the normal process using the Pair Forming Algorithm (PFA), where "F" indicates the relationship was created using the PFA, and "T" indicates the relationship was created using the **StartNewRelationship** intervention. |
| male_ID | integer | A unique identifying number for the male partner in the relationship. |
| female_ID | integer | A unique identifying number for the female partner in the relationship. |
| male_age | float | The age, in years, of the male partner in the relationship. |
| female_age | float | The age, in years, of the female partner in the relationship. |
| num_total_coital_acts | integer | The total number of coital acts by the couple during this relationship. |
| Termination_Reason | enum | The reason the relationship was terminated. Possible values are:<br><br>* NA<br>* BROKEUP<br>* SELF_MIGRATING<br>* PARTNER_DIED<br>* PARTNER_TERMINATED<br>* PARTNER_MIGRATING |

## Example

The following is an example of a RelationshipEnd.csv report:

{{ read_csv('RelationshipEnd-Example.csv') }}
