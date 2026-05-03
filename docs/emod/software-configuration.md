# Configuration file

The primary means of configuring the disease simulation is the *configuration file*. This
required file is a *JSON (JavaScript Object Notation)* formatted file that is typically named
config.json. The configuration file controls many different aspects of the simulation. For example,

* The names of the *campaign file* and other *input files* to use
* How to use additional demographics, climate, and migration data (such as enabling features or scaling values)
* General disease attributes such as infectivity, immunity, mortality, and so on
* Attributes specific to the disease type being modeled, such as infectivity and mortality
* The reports to output from the simulation

The simplest method of working with the configuration files is to use a text editor to directly edit
the parameters or parameter values in the JSON file. However, you may want to use Python or another
scripting language to make large modifications. 

For a complete list of configuration parameters that are available to use with this simulation type,
see [parameter-configuration](parameter-configuration.md). For more information about JSON, see [parameter-overview](parameter-overview.md).

