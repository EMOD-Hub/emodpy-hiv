# Reports and other output

After the simulation finishes, a *reporter* extracts simulation data, aggregates it, and
outputs it to a file (known as an *output report*). You can use any of the reporters below
to get different information about your simulation, from memory usage to relationship pairing
to ART usage.

## General reports

| Report | Description |
|--------|-------------|
| [InsetChart](software-report-inset-chart.md) | Automatically generated; simulation-wide averages of key channels at each time step. |
| [DemographicsSummary](software-report-demographic-summary.md) | Demographic channel data aggregated across the simulation; enabled together with BinnedReport. |
| [BinnedReport](software-report-binned.md) | Channel data stratified by age, gender, or other properties; enabled together with DemographicsSummary. |
| [PropertyReport](software-report-property.md) | Channel data broken down by individual property values. |
| [ReportEventCounter](software-report-event-counter.md) | Counts how many times each event occurs per time step. |
| [ReportEventRecorder](software-report-event-recorder.md) | Records health events and interventions for each individual. |
| [ReportNodeDemographics](software-report-node-demographics.md) | Node-level demographic snapshot at each time step. |
| [SpatialReport](software-report-spatial.md) | Channel data broken down per geographic node. |
| [ReportHumanMigrationTracking](software-report-human-migration.md) | Tracks individual migration events across nodes. |
| [ReportInfectionDuration](software-report-infection-duration.md) | Records the duration of each infection at the time it clears. |
| [ReportSimulationStats](software-report-simulation-stats.md) | Tracks performance, memory usage, and simulation object counts at each time step. |
| [SqlReport](software-report-sql.md) | Outputs individual-level epidemiological data to a SQLite relational database. |

## HIV reports

| Report | Description |
|--------|-------------|
| [ReportHIVByAgeAndGender](software-report-age-gender.md) | Detailed HIV outcomes stratified by age and gender. |
| [ReportHIVART](software-report-hivart.md) | Records ART initiation and discontinuation events per individual. |
| [ReportHIVInfection](software-report-hivinfection.md) | Individual disease state at each time step, including CD4 count and ART status. |
| [HIVMortality](software-report-hivmort.md) | Individual data at the time of death. |
| [TransmissionReport](software-report-transmission.md) | HIV transmission events within sexual relationships. |

## Relationship reports

| Report | Description |
|--------|-------------|
| [RelationshipStart](software-report-relationship-start.md) | Records relationship formation events. |
| [RelationshipEnd](software-report-relationship-end.md) | Records relationship dissolution events. |
| [RelationshipConsummated](software-report-relationship-consummated.md) | Coital act data per relationship per time step. |
| [ReportRelationshipCensus](software-report-relationship-census.md) | Snapshot of all active relationships at a given time. |
| [ReportRelationshipMigrationTracking](software-report-relationship-migration-tracking.md) | Relationship status of individuals at the time of migration. |

## Other

| File | Description |
|------|-------------|
| [Error and logging files](software-error-logging.md) | Error output and logging information generated during a simulation run. |
| **stdout.txt** | Contains the logging output written by EMOD to standard output during a simulation run. |
| **stderr.txt** | Contains error messages written by EMOD or Python to standard error during a simulation run. |
| [Troubleshooting](troubleshooting.md) | Help resolving common simulation errors. |
