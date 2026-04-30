# ReportHumanMigrationTracking

The human migration tracking report (ReportHumanMigrationTracking.csv) is a CSV-formatted report
that provides details about human travel during simulations. The finished report will provide one
line for each surviving individual that migrates during the simulation.

## Configuration

There are no special parameters that need to be configured to generate the report. However, the
simulation must have migration enabled (see the migration parameters in [parameter-configuration](parameter-configuration.md)).

## Report structure and channel descriptions

The file contains the following data channels:

## Example

The following is an example of ReportHumanMigrationTracking.csv.

{{ read_csv('reporthumanmigration.csv') }}
