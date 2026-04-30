# Tutorials

While the workings of the model are explained in detail, it is often more useful to learn through hands-on implementation. To illustrate many of the concepts and capabilities of EMOD, IDM provides tested files to
run example simulations that model a variety of disease scenarios. The directory for each scenario
contains the files needed to run a simulation and generate the output graphs. Click EMOD scenarios to download a zipped folder containing all required files. These scenarios are referenced throughout the documentation where relevant.

> **NOTE:**
> Because the EMOD model is *stochastic*, graphs you produce from the scenarios may
> appear slightly different from those included in the documentation.

## Included files

The compiled EMOD executable (Eradication.exe) is included. Unlike other executables, you *do not* double-click this file to
run simulations. Instead, EMOD simulations are run by calling Eradication.exe from the command line. For
these scenarios, you can simply double-click the runEMOD.cmd file in each scenario directory, which
contains the commands that will run the simulation.

Of course, you can also run simulations directly from the command line or using COmputational Modeling Platform Service (COMPS) if you
choose. Review [software-run-simulation](software-run-simulation.md) for complete information on running simulations from
the command line, or just open the runEMOD.cmd file in a text editor to see what commands it contains.

The Scenarios directory contains subdirectories that contain scenarios for different simulation
types. The README files in each of the scenario subdirectories describe what aspect of the model the
scenario illustrates. Each scenario subdirectory contains the configuration and campaign files
needed to run an EMOD simulation. Also included are plotting batch files that contain commands to
run Python scripts. You can simply double-click the batch files to run these scripts and produce graphs.

The Demographics_Files directory contains the demographics files for all scenarios. The demographics
files used with each scenario are listed in **Demographics_Filenames** in the configuration file.
This directory also contains a few climate files used with the malaria scenarios.

The Scripts directory contains the Python scripts used to plot the output of the EMOD simulations.
These are the scripts pointed to by the plotting batch files.

Most input files use *JSON (JavaScript Object Notation)* format. If you are unfamiliar with
this format, see [parameter-overview](parameter-overview.md).

## General EMOD information

The features of the model are described in greater detail elsewhere in the documentation, but this
provides a brief overview of the features most relevant to using these tutorials.

### Manipulating population size

It is often useful to re-use the same demographics files for running different simulations.
Depending on the dynamics of the simulation, or the output reports that are desired, it may be
important to change the size of the population. An alternative to modifying the demographics file
is to use the configuration parameter, **x_Base_Population**. This parameter lets you
adjust the population set by the demographics parameter, **InitialPopulation**.

### Overlay files

An alternative to changing parameter values or adding parameters to base files is to create what is
called an "overlay file." These files contain parameter settings or additional parameters that will
overwrite the settings configured in the base configuration and demographic files. When using
an overlay for configuration parameters, include the files in the working directory. For demographic
overlay files, all files to be used must be listed in the array for **Demographics_Filenames**.
The order of these files is important: the base file must be listed first, and the overlay listed
second. When there is more than one overlay file, the order of the overlays determines what information
will be overridden; the last file in order will overlay all files preceding it. Overlay files can
make it simple to swap out different parameter values without having to modify the base files, so
you can experiment with different settings. Demographic overlays make it simple to increase the
complexity of the population structure without having to create complex files.

### Weibull distributions

Many of the HIV parameters use a *Weibull distribution*. To explore the impact that the scale
and heterogeneity parameters have on the shape of the distribution, there is an Excel spreadsheet
called "Weibull.xlsx" included in the HIV scenarios folder.

### Creating campaigns

Much of the power and flexibility of EMOD comes from the customizable campaign interventions.
For more information on creating campaigns, see [model-campaign](model-campaign.md). Briefly, campaigns are created
through the hierarchical organization of JSON objects (parameter groups).

campaign event

Campaign events determine *when* and *where* an intervention is distributed during a campaign. "When"
can be the number of days after the beginning of the simulation or at a point during a particular
calendar year. "Where" is the geographic *node* or nodes in which the event takes place.

event coordinator

Event coordinators are nested within the campaign event JSON object and determine *who* receives the
intervention. "Who" is determined by filtering on age, gender, or on the individual properties
configured in the demographics files, such as risk group or sociodemographic category. See [model-properties](model-properties.md).

individual-level intervention

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

node-level intervention

Node-level interventions determine *what* will be distributed to each *node* to reduce the spread of a
disease. For example, spraying larvicide in a village to kill mosquito larvae is a node-level malaria
intervention. Sometimes this can be an intermediate intervention that schedules another
intervention. Node-level disease outbreaks are also configured as "interventions". In the schema,
these are labeled as **NodeTargeted**.

It is also possible (but not required) to configure *why* a particular intervention is distributed
by adding trigger conditions to the intervention. For example, interventions can be triggered by
notifications broadcast after some an event, such as Births, NewInfectionEvent, and more. It's also
possible to have one intervention trigger another intervention by asking the first intervention to
broadcast a unique string, and having the second intervention be triggered upon receipt of that
string. See [parameter-campaign-event-list](parameter-campaign-event-list.md).

All campaign events and event coordinators can be found in [parameter-campaign-event-coordinators](parameter-campaign-event-coordinators.md);
node-level interventions can be found in [parameter-campaign-node-interventions](parameter-campaign-node-interventions.md); and
individual-level interventions can be found in [parameter-campaign-individual-interventions](parameter-campaign-individual-interventions.md).

### Output reports

When you run a simulation using the runEMOD.cmd file, an output directory will be created that
contains the output reports from the model. Some of these will be in JSON format and others in CSV.
The standard report is InsetChart.json, which includes many different channels including
births, deaths, cumulative infections, new infections, and more. You can enable other built-in
reports by setting the appropriate parameter to 1 in the configuration file.

The HIV model includes a variety of different output reports created as .csv files. To create
particular reports, enable the parameter by setting the value to 1 for the desired report. Note
that some reports, such as the ReportHIVInfection.csv, will report information about each
individual at each time step; it is not recommended to enable these types of reports when
populations are large, as output files will become very large and the simulation will run very
slowly.

For a complete list of all available output reports, see [parameter-configuration-output](parameter-configuration-output.md).
