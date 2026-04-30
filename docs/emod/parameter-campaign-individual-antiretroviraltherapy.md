# AntiretroviralTherapy

The **AntiretroviralTherapy** intervention class begins antiretroviral therapy (ART) for specified individuals.
To remove an individual from ART, use [parameter-campaign-individual-artdropout](parameter-campaign-individual-artdropout.md).

Additional considerations when using this intervention:

* The model will not allow someone who is HIV negative to be put on ART.
* A person who has not previously been on ART is considered to be 'starting ART' at the time this intervention is applied; the model will track this start time/duration.
* If a person is already on ART from another intervention, receiving a second ART intervention will have no effect.
* If a person is on already ART and receives the [parameter-campaign-individual-artmortalitytable](parameter-campaign-individual-artmortalitytable.md) intervention, the original ART start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration since starting ART will not change; it will continue to increase.
* If a person is on ART and receives the [parameter-campaign-individual-artdropout](parameter-campaign-individual-artdropout.md) intervention, the person will go off ART and the duration will be reset; if receiving a new ART intervention, this new start time/duration will be used in any calculations.

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

{{ read_csv('../csv/campaign-antiretroviraltherapy.csv') }}

*See example: [campaign-antiretroviraltherapy.json](../json/campaign-antiretroviraltherapy.json)*
