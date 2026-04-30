# AntiretroviralTherapyFull

The **AntriretroviralTherapyFull** intervention class begins antiretroviral therapy (ART) 
on the person receiving the intervention. This class is similar to the standard 
**AntiretroviralTherapy**, but enhances it with two key features: 1) a built-in delay 
timer such that when the delay expires, the person will come off of ART (**ARTDropout** 
should NOT be used with this intervention), and 2) persistance with the individual so the 
user can track this intervention using **ReferenceTrackingEventCoordinator**. 

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

{{ read_csv('../csv/campaign-antiretroviraltherapyfull.csv') }}

*See example: [campaign-antiretroviraltherapyfull.json](../json/campaign-antiretroviraltherapyfull.json)*
