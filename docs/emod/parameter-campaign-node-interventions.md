# Node-level interventions

Node-level interventions determine *what* will be distributed to each node to reduce the spread of a
disease. For example, spraying larvicide in a village to kill mosquito larvae is a node-level malaria
intervention. Sometimes this can be an intermediate intervention that schedules another
intervention. Node-level disease outbreaks are also configured as "interventions". In the schema,
these are labeled as **NodeTargeted**.

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after an event, such as Births, NewInfectionEvent, and more. It's also
possible to have one intervention trigger another intervention by asking the first intervention to
broadcast a unique string, and having the second intervention be triggered upon receipt of that
string. See [Event list](parameter-campaign-event-list.md).

## HIV/STI relationship modifiers

| Intervention | Short description |
| --- | --- |
| [CoitalActRateChanger](parameter-campaign-node-coitalactratechanger.md) | Change the coital act rate for a relationship type in a node |
| [CondomUsageProbabilityChanger](parameter-campaign-node-condomusageprobabilitychanger.md) | Change the probability of condom use during coital acts for a relationship type in a node |
| [RelationshipDurationChanger](parameter-campaign-node-relationshipdurationchanger.md) | Change the duration of relationships of a particular type in a node |
| [RelationshipFormationRateChanger](parameter-campaign-node-relationshipformationratechanger.md) | Change the rate at which relationships form in a node |

## Outbreak / Seeding

| Intervention | Short description |
| --- | --- |
| [ImportPressure](parameter-campaign-node-importpressure.md) | Import infected individuals into a node at a configurable rate over specified time periods |
| [Outbreak](parameter-campaign-node-outbreak.md) | Introduce a disease outbreak by adding new infected or susceptible individuals to a node |

## Triggered distribution

| Intervention | Short description |
| --- | --- |
| [BirthTriggeredIV](parameter-campaign-node-birthtriggerediv.md) | Distribute an individual-level intervention to each newborn in a node |
| [NodeLevelHealthTriggeredIV](parameter-campaign-node-nodelevelhealthtriggerediv.md) | Distribute an individual-level intervention when a specific event occurs to individuals in a node |
| [NLHTIVNode](parameter-campaign-node-nlhtivnode.md) | Distribute a node-level intervention when a specific node event occurs |

## General utilities

| Intervention | Short description |
| --- | --- |
| [BroadcastCoordinatorEventFromNode](parameter-campaign-node-broadcastcoordinatoreventfromnode.md) | Broadcast an event for coordinators from a node |
| [BroadcastNodeEvent](parameter-campaign-node-broadcastnodeevent.md) | Broadcast a node event |
| [MigrateFamily](parameter-campaign-node-migratefamily.md) | Schedule a round-trip family migration for residents of a node |
| [MultiNodeInterventionDistributor](parameter-campaign-node-multinodeinterventiondistributor.md) | Distribute multiple node-level interventions simultaneously |
| [NodePropertyValueChanger](parameter-campaign-node-nodepropertyvaluechanger.md) | Set a node property to a new value |
