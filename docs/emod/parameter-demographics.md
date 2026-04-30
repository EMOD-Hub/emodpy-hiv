# Demographics

The parameters described in this reference section can be added to the *JSON (JavaScript Object Notation)* formatted demographics file to determine the demographics of the population within
each geographic *node* in a simulation. For example, the number of individuals and the
distribution for age, gender, immunity, risk, and mortality. These parameters work closely with the
[parameter-configuration-population](parameter-configuration-population.md) parameters in the *configuration file*, which are simulation-wide and
generally control whether certain events, such as births or deaths, are enabled in a simulation.

Generally, you will download a demographics file and modify it to meet the needs of your
simulation. You can use COmputational Modeling Platform Service (COMPS) to generate demographics and climate files for a particular
region. By convention, these are named using the name of the region appended with
"_demographics.json", but you may name the file anything you like.

Additionally, you can use more than one demographics file, with one serving as the base layer and
the one or more others acting as overlays that override the values in the base layer. This can be
helpful if you want to experiment with different values in the overlay without modifying your base
file. For more information, see [software-demographics](software-demographics.md).

At least one demographics file is required for every simulation unless you set the parameter
**Enable_Demographics_Builtin** to 1 (one) in the *configuration file*. This setting does not
represent a real location and is generally only used for testing and validating code pathways rather
than actual modeling of disease.

Demographics files are organized into four main sections: **Metadata**, **NodeProperties**,
**Defaults**, and **Nodes**. The following example shows the skeletal format of a demographics file.

*See example: [demographics-skeletal.json](../json/demographics-skeletal.json)*

All parameters except those in the **Metadata** and **NodeProperties** sections below can appear in
either the **Defaults** section or the **Nodes** section of the demographics file. Parameters under
**Defaults** will be applied to all nodes in the simulation. Parameters under **Nodes** will be
applied to specific nodes, overriding the values in **Defaults** if they appear in both. Each node in
the **Nodes** section is identified using a unique **NodeID**.

The tables below contain only parameters available when using the HIV *simulation type*.

> **NOTE:**
> Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
> Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
> that parameter.
>
> EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.
>
> JSON format does not permit comments, but you can add "dummy" parameters to add contextual
> information to your files. Any keys that are not EMOD parameter names will be ignored by the
> model.

## Metadata

Metadata provides information about data provenance. **IdReference** is the
only parameter used by EMOD, but you are encouraged to include information for your
own reference. For example, author, date created, tool used, NodeCount and more are commonly included
in the **Metadata** section. You can include any information you like here provided it is
in valid JSON format.  **IDReference** is used to connect the files together; the climate, migration, and demographics files all have **IdReference** so that there is some way to know that they go together (i.e. know about the same nodes).

If you generate *input files* using COMPS, the following **IdReference** values are
possible and indicate how the **NodeID** values are generated:

Gridded world grump30arcsec
    Nodes are approximately square regions defined by a 30-arc second grid and the **NodeID** values
    are generated from the latitude and longitude of the northwest corner.
Gridded world grump2.5arcmin
    Nodes are approximately square regions defined by a 2.5-arc minute grid and the **NodeID** values
    are generated from the latitude and longitude of the northwest corner.
Gridded world grump1degree
    Nodes are approximately square regions defined by a 1-degree grid and the **NodeID** values are
    generated from the latitude and longitude of the northwest corner.

The algorithm for encoding latitude and longitude into a **NodeID** is as follows:

```
unsigned int xpix = math.floor((lon + 180.0) / resolution)
unsigned int ypix = math.floor((lat + 90.0) / resolution)
unsigned int NodeID = (xpix << 16) + ypix + 1
```

This generates a **NodeID** that is a 4-byte unsigned integer; the first two bytes represent the
longitude of the node and the second two bytes represent the latitude. To reserve 0 to be used as a
null value, 1 is added to the **NodeID** as part of the final calculation.

{{ read_csv('../csv/demo-metadata-hiv.csv') }}

## NodeProperties and IndividualProperties

Node properties and individual properties are set similarly and share many of the same parameters.
Properties can be thought of as tags that are assigned to nodes or individuals and can then be used
to either target interventions to nodes or individuals with certain properties (or prevent them from
being targeted). For example, you could define individual properties for disease risk and then
target an intervention to only those at high risk. Similarly, you could define properties for node
accessibility and set lower intervention coverage for nodes that are difficult to access.

Individual properties are also used to simulate health care cascades. For example, you can
disqualify an individual who would otherwise receive an intervention; such as treating a segment of
the population with a second-line treatment but disqualifying those who haven't already received the
first-line treatment. Then you can change the property value after the treatment has been received.

The **NodeProperties** section is a top-level section at the same level as **Defaults** and **Nodes**
that contains parameters that assign properties to nodes in a simulation. The
**IndividualProperties** section is under either **Defaults** or **Nodes** and contains parameters
that assign properties to individuals in a simulation.

[model-properties](model-properties.md) provides more guidance.

*See parameter table: [demo-properties-hiv.csv](../csv/demo-properties-hiv.csv)*

## NodeAttributes

The **NodeAttributes** section contains parameters that add or modify information
regarding the location, migration, habitat, and population of node. Some **NodeAttributes**
depend on values set in the configuration parameters.

*See parameter table: [demo-nodeattributes-hiv.csv](../csv/demo-nodeattributes-hiv.csv)*

## IndividualAttributes

The **IndividualAttributes** section contains parameters that initialize the distribution of
attributes across individuals, such as the age or immunity. An initial value for an
individual is a randomly selected value from a given distribution. These distributions can be
configured using a simple flag system of three parameters or a complex system of
many more parameters. The following table contains the parameters that can be used with either
distribution system.

*See parameter table: [demo-individualattributes-hiv.csv](../csv/demo-individualattributes-hiv.csv)*

### Simple distributions

Simple distributions are defined by three parameters where one is a flag for the distribution type
and the other two are used to further define the distribution. For example, if you set the age flag
to a uniform distribution, the initial ages of individuals in the simulation will be evenly
distributed between some minimum and maximum value as defined by the other two parameters.

*See parameter table: [demo-simpledistro-hiv.csv](../csv/demo-simpledistro-hiv.csv)*

### Complex distributions

Complex distributions are more effort to configure, but are useful for representing real-world data
where the distribution does not fit a standard. Individual attribute values are drawn from a piecewise
linear distribution. The distribution is configured using arrays of axes (such as gender or age) and
values at points along each of these axes. This allows you to have different distributions for
different groups in the population.

*See parameter table: [demo-complexdistro-hiv.csv](../csv/demo-complexdistro-hiv.csv)*

## Society

The **Society** section defines the behavioral-based parameters of a relationship type in the STI
and HIV models, such as rates of partnership formation, partner preference, relationship duration,
or concurrent partnerships. It must contain the four sets of relationship type parameters and the
**Concurrency_Configuration** section. Note that the name used for each relationship type is only a
guide; EMOD does not include specific logic for each type and the settings for each depend only
upon the parameters you provide.

The section for each relationship type must include the **Relationship_Parameters**,
**Pair_Formation_Parameters**, and **Concurrency_Parameters** sections. These sections define the
settings for the specific relationship type they are nested under.

The **Concurrency_Configuration** section defines how the simultaneous relationship parameters are
used across all relationship types.

*See parameter table: [demo-society-hiv.csv](../csv/demo-society-hiv.csv)*

### Concurrency_Configuration

The **Concurrency_Configuration** section is at the same level as each relationship type section and
defines how the simultaneous relationship parameters are used across all relationship types. For
example, how flags that allow an individual to seek out different types of extra-relational
partnerships are distributed.

*See parameter table: [demo-concurrency-config-hiv.csv](../csv/demo-concurrency-config-hiv.csv)*

### Relationship_Parameters

The **Relationship_Parameters** section defines basic attributes such as relationship duration, what
happens if one member of a relationship migrates, and condom usage.

*See parameter table: [demo-relationship-hiv.csv](../csv/demo-relationship-hiv.csv)*

### Pair_Formation_Parameters

The **Pair_Formation_Parameters** section defines the rate at which new relationships are formed and
partnership preference using the main pair forming algorithm that finds potential
partners based on their age and the **Joint_Probabilities** matrix.

*See parameter table: [demo-pairing-hiv.csv](../csv/demo-pairing-hiv.csv)*

#### Assortivity

The **Assortivity** section refines who partners with whom. After the main pair forming algorithm
reduces the set of potential partners to a subset based on age, **Assortivity** allows for selection
based on other criteria.

*See parameter table: [demo-assortivity-hiv.csv](../csv/demo-assortivity-hiv.csv)*

### Concurrency_Parameters

The **Concurrency_Configuration** section at the top level of the **Society** section defines the
simultaneous relationship parameters for super spreader probabilities, whether simultaneous
relationships type probabilities are independent or correlated, and, if correlated, the order of the
relationship types. If you want to base concurrency on **IndividualProperties** settings, you can
list the relevant properties in **Individual_Property_Name**, using "NONE" if the properties are
irrelevant for concurrency.

Under each relationship type, the **Concurrency_Parameters** section defines simultaneous relationship
parameters for that relationship type. In this section, all parameters should be nested under the
name of the individual property relevant for setting concurrency. Again, if the properties are irrelevant,
use "NONE".

*See parameter table: [demo-concurrency-params-hiv.csv](../csv/demo-concurrency-params-hiv.csv)*
