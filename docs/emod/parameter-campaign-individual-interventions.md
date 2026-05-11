# Individual-level interventions

Individual-level interventions determine *what* will be distributed to individuals to reduce the
spread of a disease. For example, distributing vaccines or drugs are individual-level interventions.
In the schema, these are labeled as **IndividualTargeted**.  

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births (the individual’s own
birth), GaveBirth, NewInfectionEvent, and more. It's also possible to have one intervention trigger
another intervention by asking the first intervention to broadcast a unique string, and having the
second intervention be triggered upon receipt of that string. See [Event list](parameter-campaign-event-list.md).

Individual-level interventions can be used as part of configuring a cascade of care along with the individual
properties set in the demographics file. Use **Disqualifying_Properties** to disqualify individuals
who would otherwise receive the intervention and **New_Property_Value** to assign a new value when
the intervention is received. For example, you can assign a property value after receiving the
first-line treatment for a disease and prevent anyone from receiving the second-line treatment
unless they have that property value and are still symptomatic.

## ART / Treatment

| Intervention | Short description |
| --- | --- |
| [AntiretroviralTherapy](parameter-campaign-individual-antiretroviraltherapy.md) | Begin ART for an individual |
| [AntiretroviralTherapyFull](parameter-campaign-individual-antiretroviraltherapyfull.md) | Begin ART with full parameter control |
| [ARTDropout](parameter-campaign-individual-artdropout.md) | Remove an individual from ART |
| [ARTMortalityTable](parameter-campaign-individual-artmortalitytable.md) | Modify life expectancy based on ART adherence using a multi-dimensional table |

## Diagnostics

| Intervention | Short description |
| --- | --- |
| [AgeDiagnostic](parameter-campaign-individual-agediagnostic.md) | Test based on age threshold |
| [CD4Diagnostic](parameter-campaign-individual-cd4diagnostic.md) | Test based on CD4 count ranges |
| [HIVARTStagingByCD4Diagnostic](parameter-campaign-individual-hivartstagingbycd4diagnostic.md) | Determine ART eligibility based on CD4 count |
| [HIVARTStagingCD4AgnosticDiagnostic](parameter-campaign-individual-hivartstagingcd4agnosticdiagnostic.md) | Determine ART eligibility using age bins instead of CD4 |
| [HIVDrawBlood](parameter-campaign-individual-hivdrawblood.md) | Represent phlebotomy for CD4 or viral load testing |
| [HIVPiecewiseByYearAndSexDiagnostic](parameter-campaign-individual-hivpiecewisebyyearandsexdiagnostic.md) | Configure intervention roll-out over time by sex |
| [HIVRapidHIVDiagnostic](parameter-campaign-individual-hivrapidhivdiagnostic.md) | Rapid HIV test that updates the individual's knowledge of their HIV status |
| [HIVSigmoidByYearAndSexDiagnostic](parameter-campaign-individual-hivsigmoidbyyearandsexdiagnostic.md) | Configure probability of positive diagnosis sigmoidally over time |
| [HIVSimpleDiagnostic](parameter-campaign-individual-hivsimplediagnostic.md) | Test with configurable outcomes for both positive and negative diagnosis |
| [ImmunityBloodTest](parameter-campaign-individual-immunitybloodtest.md) | Check if an individual's immunity meets a specified threshold |
| [SimpleDiagnostic](parameter-campaign-individual-simplediagnostic.md) | Test based on sensitivity and specificity |
| [StandardDiagnostic](parameter-campaign-individual-standarddiagnostic.md) | Test based on sensitivity and specificity with more features than SimpleDiagnostic |
| [STICoinfectionDiagnostic](parameter-campaign-individual-sticoinfectiondiagnostic.md) | Diagnose STI co-infection |

## HIV/STI prevention

| Intervention | Short description |
| --- | --- |
| [CoitalActRiskFactors](parameter-campaign-individual-coitalactriskfactors.md) | Modify an individual's risk of acquiring or transmitting an STI during coital acts |
| [FemaleContraceptive](parameter-campaign-individual-femalecontraceptive.md) | Reduce the fertility rate of females of reproductive age |
| [MaleCircumcision](parameter-campaign-individual-malecircumcision.md) | Introduce male circumcision to reduce HIV transmission |
| [ModifySTICoinfectionStatus](parameter-campaign-individual-modifysticoinfectionstatus.md) | Create or remove STI co-infections |
| [PMTCT](parameter-campaign-individual-pmtct.md) | Define efficacy of prevention of mother-to-child transmission at time of birth |
| [STIBarrier](parameter-campaign-individual-stibarrier.md) | Reduce STI/HIV transmission probability via time-variable condom usage |
| [STIIsPostDebut](parameter-campaign-individual-stiispostdebut.md) | Check if an individual is post-STI debut |

## Relationships

| Intervention | Short description |
| --- | --- |
| [InterventionForCurrentPartners](parameter-campaign-individual-interventionforcurrentpartners.md) | Distribute interventions to an individual's current partners |
| [SetSexualDebutAge](parameter-campaign-individual-setsexualdebutage.md) | Set the age at which an individual will sexually debut |
| [StartNewRelationship](parameter-campaign-individual-startnewrelationship.md) | Trigger formation of a new relationship |

## Care cascade

| Intervention | Short description |
| --- | --- |
| [HIVDelayedIntervention](parameter-campaign-individual-hivdelayedintervention.md) | Delay before distributing an HIV-specific intervention with additional HIV features |
| [HIVMuxer](parameter-campaign-individual-hivmuxer.md) | Place individuals in a waiting pattern for the next care event |
| [HIVRandomChoice](parameter-campaign-individual-hivrandomchoice.md) | Randomly distribute interventions based on specified probabilities |
| [SimpleHealthSeekingBehavior](parameter-campaign-individual-simplehealthseekingbehavior.md) | Model the time delay between symptom onset and care-seeking |

## Vaccines

| Intervention | Short description |
| --- | --- |
| [ControlledVaccine](parameter-campaign-individual-controlledvaccine.md) | Vaccine with control over additional events and triggers |
| [MultiEffectBoosterVaccine](parameter-campaign-individual-multieffectboostervaccine.md) | Boost an existing vaccine's multiple effects |
| [MultiEffectVaccine](parameter-campaign-individual-multieffectvaccine.md) | Implement a vaccine with multiple simultaneous effects |
| [SimpleBoosterVaccine](parameter-campaign-individual-simpleboostervaccine.md) | Boost an existing vaccine's single effect |
| [SimpleVaccine](parameter-campaign-individual-simplevaccine.md) | Implement a basic vaccine campaign |

## General utilities

| Intervention | Short description |
| --- | --- |
| [BroadcastEvent](parameter-campaign-individual-broadcastevent.md) | Immediately broadcast an event trigger to an individual |
| [BroadcastEventToOtherNodes](parameter-campaign-individual-broadcasteventtoothernodes.md) | Send events from one node to another |
| [DelayedIntervention](parameter-campaign-individual-delayedintervention.md) | Introduce a delay before distributing an intervention |
| [IndividualImmunityChanger](parameter-campaign-individual-individualimmunitychanger.md) | Modify an individual's immunity |
| [IndividualNonDiseaseDeathRateModifier](parameter-campaign-individual-individualnondiseasedeathratemodifier.md) | Modify an individual's non-disease mortality rate |
| [IVCalendar](parameter-campaign-individual-ivcalendar.md) | Distribute an intervention when an individual reaches a specific age |
| [MigrateIndividuals](parameter-campaign-individual-migrateindividuals.md) | Force migration of an individual outside the normal migration system |
| [MultiInterventionDistributor](parameter-campaign-individual-multiinterventiondistributor.md) | Distribute multiple interventions simultaneously |
| [OutbreakIndividual](parameter-campaign-individual-outbreakindividual.md) | Seed infections in existing individuals |
| [PropertyValueChanger](parameter-campaign-individual-propertyvaluechanger.md) | Change an individual's **IndividualProperty** value |
