# StartNewRelationship

The **StartNewRelationship** intervention class provides a method of triggering the formation of 
a relationship following a user-specified event. The parameters of the relationship that is formed can 
also be customized by the user, such as individual properties required of the partner, or modified 
condom usage probability within the relationship. Note: These new relationships can be made by people of 
any age (the intervention disregards **IsPostDebut** and **Sexual_Debut_Age_Min**). Additionally, these 
relationships are considered outside of the Pair Formation Algorithm (PFA), and do not impact/are not impacted 
by concurrency or pair formation parameters. Coital act and condom usage rate are as per the corresponding 
relationship type, unless modified by the user.

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

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv('../csv/campaign-startnewrelationship.csv') }}

*See example: [campaign-startnewrelationship.json](../json/campaign-startnewrelationship.json)*
