# Individual-level interventions

Individual-level interventions determine *what* will be distributed to individuals to reduce the
spread of a disease. For example, distributing vaccines or drugs are individual-level interventions.
In the schema, these are labeled as **IndividualTargeted**.  

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births (the individual’s own
birth), GaveBirth, NewInfectionEvent, and more. It's also possible to have one intervention trigger
another intervention by asking the first intervention to broadcast a unique string, and having the
second intervention be triggered upon receipt of that string. See [parameter-campaign-event-list](parameter-campaign-event-list.md).

Individual-level interventions can be used as part of configuring a cascade of care along with the individual
properties set in the demographics file. Use **Disqualifying_Properties** to disqualify individuals
who would otherwise receive the intervention and **New_Property_Value** to assign a new value when
the intervention is received. For example, you can assign a property value after receiving the
first-line treatment for a disease and prevent anyone from receiving the second-line treatment
unless they have that property value and are still symptomatic.

- [parameter-campaign-individual-agediagnostic](parameter-campaign-individual-agediagnostic.md)
- [parameter-campaign-individual-antiretroviraltherapy](parameter-campaign-individual-antiretroviraltherapy.md)
- [parameter-campaign-individual-antiretroviraltherapyfull](parameter-campaign-individual-antiretroviraltherapyfull.md)
- [parameter-campaign-individual-artdropout](parameter-campaign-individual-artdropout.md)
- [parameter-campaign-individual-artmortalitytable](parameter-campaign-individual-artmortalitytable.md)
- [parameter-campaign-individual-broadcastevent](parameter-campaign-individual-broadcastevent.md)
- [parameter-campaign-individual-broadcasteventtoothernodes](parameter-campaign-individual-broadcasteventtoothernodes.md)
- [parameter-campaign-individual-cd4diagnostic](parameter-campaign-individual-cd4diagnostic.md)
- [parameter-campaign-individual-coitalactriskfactors](parameter-campaign-individual-coitalactriskfactors.md)
- [parameter-campaign-individual-controlledvaccine](parameter-campaign-individual-controlledvaccine.md)
- [parameter-campaign-individual-delayedintervention](parameter-campaign-individual-delayedintervention.md)
- [parameter-campaign-individual-femalecontraceptive](parameter-campaign-individual-femalecontraceptive.md)
- [parameter-campaign-individual-hivartstagingbycd4diagnostic](parameter-campaign-individual-hivartstagingbycd4diagnostic.md)
- [parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic](parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic.md)
- [parameter-campaign-individual-hivdelayedintervention](parameter-campaign-individual-hivdelayedintervention.md)
- [parameter-campaign-individual-hivdrawblood](parameter-campaign-individual-hivdrawblood.md)
- [parameter-campaign-individual-hivmuxer](parameter-campaign-individual-hivmuxer.md)
- [parameter-campaign-individual-hivpiecewisebyyearandsexdiagnostic](parameter-campaign-individual-hivpiecewisebyyearandsexdiagnostic.md)
- [parameter-campaign-individual-hivrandomchoice](parameter-campaign-individual-hivrandomchoice.md)
- [parameter-campaign-individual-hivrapidhivdiagnostic](parameter-campaign-individual-hivrapidhivdiagnostic.md)
- [parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic](parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic.md)
- [parameter-campaign-individual-hivsimplediagnostic](parameter-campaign-individual-hivsimplediagnostic.md)
- [parameter-campaign-individual-immunitybloodtest](parameter-campaign-individual-immunitybloodtest.md)
- [parameter-campaign-individual-individualimmunitychanger](parameter-campaign-individual-individualimmunitychanger.md)
- [parameter-campaign-individual-individualnondiseasedeathratemodifier](parameter-campaign-individual-individualnondiseasedeathratemodifier.md)
- [parameter-campaign-individual-interventionforcurrentpartners](parameter-campaign-individual-interventionforcurrentpartners.md)
- [parameter-campaign-individual-ivcalendar](parameter-campaign-individual-ivcalendar.md)
- [parameter-campaign-individual-malecircumcision](parameter-campaign-individual-malecircumcision.md)
- [parameter-campaign-individual-migrateindividuals](parameter-campaign-individual-migrateindividuals.md)
- [parameter-campaign-individual-modifysticoinfectionstatus](parameter-campaign-individual-modifysticoinfectionstatus.md)
- [parameter-campaign-individual-multieffectboostervaccine](parameter-campaign-individual-multieffectboostervaccine.md)
- [parameter-campaign-individual-multieffectvaccine](parameter-campaign-individual-multieffectvaccine.md)
- [parameter-campaign-individual-multiinterventiondistributor](parameter-campaign-individual-multiinterventiondistributor.md)
- [parameter-campaign-individual-outbreakindividual](parameter-campaign-individual-outbreakindividual.md)
- [parameter-campaign-individual-pmtct](parameter-campaign-individual-pmtct.md)
- [parameter-campaign-individual-propertyvaluechanger](parameter-campaign-individual-propertyvaluechanger.md)
- [parameter-campaign-individual-simpleboostervaccine](parameter-campaign-individual-simpleboostervaccine.md)
- [parameter-campaign-individual-simplediagnostic](parameter-campaign-individual-simplediagnostic.md)
- [parameter-campaign-individual-simplehealthseekingbehavior](parameter-campaign-individual-simplehealthseekingbehavior.md)
- [parameter-campaign-individual-simplevaccine](parameter-campaign-individual-simplevaccine.md)
- [parameter-campaign-individual-standarddiagnostic](parameter-campaign-individual-standarddiagnostic.md)
- [parameter-campaign-individual-startnewrelationship](parameter-campaign-individual-startnewrelationship.md)
- [parameter-campaign-individual-stibarrier](parameter-campaign-individual-stibarrier.md)
- [parameter-campaign-individual-sticoinfectiondiagnostic](parameter-campaign-individual-sticoinfectiondiagnostic.md)
- [parameter-campaign-individual-stiispostdebut](parameter-campaign-individual-stiispostdebut.md)
