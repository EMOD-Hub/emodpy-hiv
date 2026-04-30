# RelationshipFormationRateChanger

The **RelationshipFormationRateChanger** node intervention class allows the user to change 
the rate at which relationships form in a node. This allows the user to model, for example, how 
an education program or other intervention causes people to reduce the number of relationships they create. 
This intervention overrides the **Formation_Rate_Constant** value in the Demographics file that 
typically determines this rate (**Formation_Rate_Type** is assumed to be 'CONSTANT'). 
Note, this intervention does not expire; it causes an existing intervention to be removed. Hence, to reset the 
parameter, the user should submit a second intervention with the original value. This change impacts the 
relationships one time step after it was distributed.

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

*See parameter table: [campaign-relationshipformationratechanger.csv](../csv/campaign-relationshipformationratechanger.csv)*

*See example: [campaign-relationshipformationratechanger.json](../json/campaign-relationshipformationratechanger.json)*
