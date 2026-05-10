# SetSexualDebutAge

The **SetSexualDebutAge** intervention class sets the age at which an individual will sexually
debut — that is, when the individual becomes eligible to enter relationships where coital acts
can occur. The intervention expires immediately after it is applied. Note that sexual debut
determines when a person can begin forming relationships; the first coital act may occur some
time after debut.

When using this intervention, you must set the config parameter **Sexual_Debut_Age_Setting_Type**
to FROM_INTERVENTION. With the default WEIBULL setting, each person's debut age is initialized
from a Weibull distribution using the **Sexual_Debut_Age_XXX_Weibull_Heterogeneity** and
**Sexual_Debut_Age_XXX_Weibull_Scale** parameters. With FROM_INTERVENTION, an individual's
debut age is not set unless the **SetSexualDebutAge** intervention is applied to them.

This intervention is typically used together with
[ReferenceTrackingEventCoordinatorTrackingConfig](parameter-campaign-event-referencetrackingeventcoordinatortrackingconfig.md)
and a **Tracking_Config** of class **IsPostDebut** to achieve a target fraction of the
population debuted by a given age and year. For an example of this approach applied to
published research, see Akullian et al. (2025), which used this feature to model cohort-based
estimates of the proportion of individuals who had initiated sex by age and sex, and found that
increasing age at sexual debut was the largest driver of HIV incidence decline among adolescent
girls aged 15–19 in Uganda ([PLOS Medicine](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1004993)).

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.

The table below describes all possible parameters with which this class can be configured. The JSON
example that follows shows one potential configuration.

{{ read_csv('../csv/campaign-setsexualdebutage.csv') }}

*See example: [campaign-setsexualdebutage.json](../json/campaign-setsexualdebutage.json)*
