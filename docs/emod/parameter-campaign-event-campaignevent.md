# CampaignEvent and CampaignEventByYear

!!! note
    Parameters are case-sensitive. For Boolean parameters, set to 1 for true or 0 for false.
    Minimum, maximum, or default values of "NA" indicate that those values are not applicable for
    that parameter.

    EMOD does not use true defaults; that is, if the dependency relationships indicate that a parameter is required, you must supply a value for it. However, many of the tools used to work with EMOD will use the default values provided below.

    JSON format does not permit comments, but you can add "dummy" parameters to add contextual
    information to your files. Any keys that are not EMOD parameter names will be ignored by the
    model.

## CampaignEvent

The **CampaignEvent** class determines when to distribute the intervention based on the first day of
the simulation. The table below describes all available parameters, followed by a JSON example.

{{ read_csv('../csv/campaign-campaignevent.csv') }}

*See example: [campaign-campaignevent.json](../json/campaign-campaignevent.json)*

## CampaignEventByYear

The **CampaignEventByYear** class determines when to distribute the intervention based on the
calendar year. Use this class instead of **CampaignEvent** when working with HIV simulations that
use calendar-year timelines. The table below describes all available parameters, followed by a JSON example.

{{ read_csv('../csv/campaign-campaigneventbyyear.csv') }}

*See example: [campaign-campaigneventbyyear.json](../json/campaign-campaigneventbyyear.json)*
