from emod_api import campaign as api_campaign
from emodpy.campaign.base_intervention import IndividualIntervention
from emodpy.campaign.event import create_campaign_event

from emodpy_hiv.campaign.common import (TargetDemographicsConfig, PropertyRestrictions, NChooserTargetedDistributionHIV,
                                        ValueMap, CommonInterventionParameters as CIP)
from emodpy_hiv.campaign.event_coordinator import NChooserEventCoordinatorHIV, ReferenceTrackingEventCoordinatorTrackingConfig
from emodpy_hiv.utils.emod_enum import TargetDiseaseState
from emodpy_hiv.utils.targeting_config import AbstractTargetingConfig, HasIntervention

import pandas as pd
import warnings

# ported from emodpy/campaign/distributor.py

# This function adds the intervention(s) to the campaign at scheduled time with the given parameters.
# The start_year parameter is only allowed to be used in HIV, and it is recommended that HIV modelers use it to schedule
# the intervention(s) at the specified year instead of start_day.
from emodpy.campaign.distributor import add_intervention_scheduled

# This function configures the campaign to distribute an intervention to an individual when that individual broadcasts
# an event.
# The start_year parameter is only allowed to be used in HIV, and it is recommended that HIV modelers use it to define
# the specified year when the simulation starts to listen to the event instead of start_day.
from emodpy.campaign.distributor import add_intervention_triggered


def add_intervention_nchooser_df(campaign: api_campaign,
                                 intervention_list: list[IndividualIntervention],
                                 distribution_df: pd.DataFrame,
                                 property_restrictions: PropertyRestrictions = None,
                                 target_disease_state: list[list[TargetDiseaseState]] = None,
                                 target_disease_state_has_intervention_name: str = None,
                                 event_name: str = None,
                                 node_ids: list[int] = None) -> None:
    """
    # Overview:

    Distributes a list of individual-level interventions to exactly N people of a targeted demographic in HIV
    simulations. This contrasts with other event coordinators that distribute an intervention to a percentage of the
    population, not to an exact count.

    # Population Scaling:

    'N' is assumed to be a number that is for the non-scaled population. This means you can make it the number actually
    used in the real world. The 'N' values entered will be multiplied by the config parameter `x_Base_Population`.

    For example:
        - If you wanted to model how the real world distributed 2,000 male circumcisions in 1990 when the total
          population was 400,000, and your demographic parameters are configured such that EMOD has about 400,000 people
          in 1990, you would distribute 2,000 male circumcisions.
        - If the simulation is taking a long time, and you change `config.x_Base_Population` to 0.5 to cut the agents in
          the simulation in half, you would also want to reduce the number of male circumcisions being distributed.
          This feature will automatically adjust the number being targeted by `config.x_Base_Population` to only hand
          out 1,000 male circumcisions.

    # Distribution Over Time:

    NChooser will also spread out the number of interventions being distributed over the entire time period.

    For example:
        - Let's assume that you are trying to distribute MaleCircumcision to 9 men over five update periods. NChooser
          will give out two interventions the first four update periods and one during the last update period.

    # DataFrame Requirements:

    This function takes in a DataFrame containing the distribution data:
        - Required columns: `year`, `min_age`, `max_age`
        - At least one of the following columns is required: `num_targeted`, `num_targeted_female`, `num_targeted_male`

    The data in the DataFrame is used to create a list of `NChooserTargetedDistributionHIV` objects specifying:
        - When: with the `year` data
        - To whom: with the `min_age` and `max_age` data
        - How many interventions are distributed: with the `num_targeted` data, or the `num_targeted_female` for female
          individuals and `num_targeted_male` for male individuals

    Args:
        campaign (emod_api.campaign, required):
            - The campaign object to which the event will be added.
            - This should be an instance of the emod_api.campaign class.
        intervention_list (list[IndividualIntervention], required):
            - A list of IndividualIntervention objects. NodeIntervention is not supported in this feature.
            - Refer to the emodpy_hiv.campaign.individual_intervention module for available IndividualIntervention derived classes.
        distribution_df (pd.DataFrame, required):
            - A DataFrame containing the data for these columns: year, min_age, max_age, num_targeted,
              num_targeted_female, num_targeted_male.
            - The first three columns are required, and at least one of the last three columns is required.
            - num_targeted: The number of individuals to be targeted, gender-agnostic. It can't be used with
              num_targeted_female or num_targeted_male.
            - num_targeted_female: The number of female individuals to be targeted. It can't be used with num_targeted.
            - num_targeted_male: The number of male individuals to be targeted. It can't be used with num_targeted.
        target_disease_state (list[list[TargetDiseaseState]], optional):
            - A two-dimensional list of disease states using the TargetDiseaseState enum.
            - To qualify for the intervention, an individual must match at least one of the inner lists of disease states.
            - Each entry in the inner array is an "and" requirement, meaning an individual must match all states in one
              inner list to qualify.
            - Each inner list is combined with an "or" relationship with other inner list, meaning an individual needs
              to match at least one of the inner list to qualify.
            - Possible values: Refer to the TargetDiseaseState enum for the possible values.
            - Default value: None.
        target_disease_state_has_intervention_name (str, optional):
            - The name of the intervention to look for in an individual when targeting specific disease states.
            - It's required when using TargetDiseaseState.HAS_INTERVENTION or TargetDiseaseState.NOT_HAS_INTERVENTION in target_disease_state.
        property_restrictions (PropertyRestrictions, optional):
            - A PropertyRestrictions to define the individual-level property restrictions in the coordinator.
            - Please note that node property restrictions are not supported in this feature.
            - Default value: None.
        event_name (str, optional):
            - The name of the campaign event.
            - Default value: None
        node_ids (list[int], optional):
            - A list of node IDs where the event will be applied.
            - If None, the event applies to all nodes.
            - Default value: None.

    Returns:
            None: This function does not return anything. It modifies the campaign object in place.

    Examples:
        Example 1: This example demonstrates how to distribute a MaleCircumcision intervention to male individuals
        who are HIV positive and do not have the intervention already. The intervention is distributed based on the
        distribution data provided in a DataFrame.

        >>> import emod_api
        >>> from emodpy_hiv.campaign.distributor import add_intervention_nchooser_df
        >>> from emodpy_hiv.campaign.individual_intervention import MaleCircumcision
        >>> from emodpy_hiv.campaign.common import CommonInterventionParameters as CIP
        >>> from emodpy_hiv.utils.emod_enum import TargetDiseaseState
        >>> import pandas as pd
        >>>
        >>> campaign_obj = emod_api.campaign
        >>> campaign_obj.schema_path = 'path_to_schema'
        >>> # Initialize a MaleCircumcision intervention with intervention_name: 'MaleCircumcision'
        >>> intervention_name='MaleCircumcision'
        >>> mc = MaleCircumcision(campaign_obj, common_intervention_parameters=CIP(intervention_name=intervention_name)
        >>> # Create a DataFrame with the distribution data: year, min_age, max_age, num_targeted_male
        >>> # The intervention will be distributed to MALE individuals with the following values:
        >>> #    for the year 2010, age ranges: [1, 14.999), [15, 49.999), the number of targeted MALE individuals are: [200, 1300].
        >>> #    for the year 2011, age ranges: [1, 14.999), [15, 49.999), the number of targeted MALE individuals are: [290, 1490].
        >>> data = {'year': [2010, 2010, 2011, 2011],
        >>>         'min_age': [1, 15, 1, 15],
        >>>         'max_age': [14.999, 49.999, 14.999, 49.999],
        >>>         'num_targeted_male': [200, 1300, 290, 1490]}
        >>> distributions_df = pd.DataFrame.from_dict(data)
        >>> # Distribute the MaleCircumcision intervention to the campaign with the distribution data. The targeted
        >>> # individuals should be male, HIV negative and don't have an intervention called 'MaleCircumcision' already.
        >>> add_intervention_nchooser_df(campaign_obj,
        >>>                              intervention_list=[mc],
        >>>                              target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]],
        >>>                              target_disease_state_has_intervention_name=intervention_name,
        >>>                              distribution_df=distributions_df)

        Example 2: This example demonstrates the usage of "And" and "Or" relationship in the target_disease_state parameter.
        With the following target_disease_state parameter, the MaleCircumcision intervention will be distributed to
        individuals who don't have the intervention already and are either HIV positive or tested positive.

        >>> add_intervention_nchooser_df(campaign_obj,
        >>>                              intervention_list=[mc],
        >>>                              target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION],
        >>>                                                   [TargetDiseaseState.TESTED_POSITIVE, TargetDiseaseState.NOT_HAVE_INTERVENTION]],
        >>>                              target_disease_state_has_intervention_name=intervention_name,
        >>>                              distribution_df=distributions_df)

    Raises:

    """
    # These are the columns that are expected in the distribution dataframe
    required_columns = {'year', 'min_age', 'max_age'}
    if not required_columns.issubset(distribution_df.columns):
        raise ValueError(f"Expected these columns: {required_columns} in the distribution_df "
                         f"dataframe. Got distributions.columns: {distribution_df.columns}")

    # Only one of the following names is required.
    optional_columns = {'num_targeted', 'num_targeted_female', 'num_targeted_male'}
    # Check if at least one optional column is present in the distribution dataframe
    if not optional_columns.intersection(distribution_df.columns):
        raise ValueError(f"Expected at least one of these columns: {optional_columns} in the distribution_df "
                         f"dataframe. Got distributions.columns: {distribution_df.columns}")

    # Get the unique value of target years from the distribution dataframe
    target_years = distribution_df.year.unique()
    # Created the distribution objects for each target year
    targeted_distributions = []
    for year in target_years:
        # Filter the distribution dataframe with year
        df_cur_year = distribution_df[distribution_df['year'] == year].sort_values(by=['min_age'])
        # Max and Min age ranges for qualifying individuals.
        age_ranges_years = [df_cur_year['min_age'].tolist(), df_cur_year['max_age'].tolist()]
        num_targeted = None
        num_targeted_female = None
        num_targeted_male = None
        if 'num_targeted' in distribution_df.columns:
            num_targeted = df_cur_year['num_targeted'].tolist()
            if 'num_targeted_female' in distribution_df.columns or 'num_targeted_male' in distribution_df.columns:
                raise ValueError("num_targeted column should not be used with num_targeted_female or num_targeted_male.")
        else:
            if 'num_targeted_female' in distribution_df.columns:
                num_targeted_female = df_cur_year['num_targeted_female'].tolist()
            if 'num_targeted_male' in distribution_df.columns:
                num_targeted_male = df_cur_year['num_targeted_male'].tolist()

            # If one of them is not set, it should contain 0s with the same length as the other one.
            if num_targeted_female is None:
                num_targeted_female = [0] * len(num_targeted_male)
            if num_targeted_male is None:
                num_targeted_male = [0] * len(num_targeted_female)

        targeted_distribution = NChooserTargetedDistributionHIV(age_ranges_years=age_ranges_years,
                                                                start_year=float(year),
                                                                end_year=year + 0.999999,
                                                                num_targeted=num_targeted,
                                                                num_targeted_females=num_targeted_female,
                                                                num_targeted_males=num_targeted_male,
                                                                property_restrictions=property_restrictions,
                                                                target_disease_state=target_disease_state,
                                                                target_disease_state_has_intervention_name=
                                                                target_disease_state_has_intervention_name)
        targeted_distributions.append(targeted_distribution)

    # Call the add_intervention_nchooser function to distribute the intervention_list with target_distributions
    # Set start_year to the minimum year in the target_years
    start_year = float(min(target_years))
    _add_intervention_nchooser(campaign,
                               intervention_list=intervention_list,
                               targeted_distributions=targeted_distributions,
                               start_year=start_year,
                               event_name=event_name,
                               node_ids=node_ids)


def _add_intervention_nchooser(campaign: api_campaign,
                               intervention_list: list[IndividualIntervention],
                               targeted_distributions: list[NChooserTargetedDistributionHIV],
                               start_year: float,
                               event_name: str = None,
                               node_ids: list[int] = None) -> None:
    """
    Distributes a list of individual-level interventions to exactly N people of a targeted demographic in HIV
    simulations. This contrasts with other event coordinators that distribute an intervention to a percentage of the
    population, not to an exact count.

    This function takes in a list of NChooserTargetedDistributionHIV object specifying when, to whom, and how many
    interventions are distributed.

    Please refer to the Emod documentation for NChooserEventCoordinatorHIV at the following link:
    :doc:`emod-hiv:parameter-campaign-event-nchoosereventcoordinatorhiv`

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the event will be added.
            - This should be an instance of the emod_api.campaign class.
        intervention_list (list[IndividualIntervention], required):
            - A list of IndividualIntervention objects. NodeIntervention is not supported in this feature.
            - Refer to the emodpy_hiv.campaign.individual_intervention module for available IndividualIntervention derived classes.
        targeted_distributions (list[NChooserTargetedDistributionHIV], required):
            - A list of NChooserTargetedDistributionHIV object specifying when, to whom, and how many interventions are distributed.
            - Please refer emodpy_hiv.campaign.event_coordinator.NChooserTargetedDistributionHIV for more details.
        start_year (float, requied):
            - The year when the event starts.
        event_name (str, optional):
            - The name of the campaign event.
            - Default value: None.
        node_ids (list[int], optional):
            - A list of node IDs where the event will be applied.
            - If None, the event applies to all nodes.
            - Default value: None.

    Returns:
        None: This function does not return anything. It modifies the campaign object in place.

    Examples:
        >>> from emodpy_hiv.campaign.common import NChooserTargetedDistributionHIV
        >>> from emod_api import campaign as api_campaign
        >>> from emodpy_hiv.campaign.individual_intervention import MaleCircumcision
        >>> from emodpy_hiv.campaign.distributor import _add_intervention_nchooser
        >>>
        >>> api_campaign.set_schema('path_to_schema')
        >>> intervention_config = MaleCircumcision(api_campaign)
        >>> distribution_1 = NChooserTargetedDistributionHIV( ...)
        >>> distribution_2 = NChooserTargetedDistributionHIV( ...)
        >>> _add_intervention_nchooser(api_campaign,
        >>>                           intervention_list=[intervention_config],
        >>>                           targeted_distributions=[distribution_1, distribution_2],
        >>>                           start_year=1990,
        >>>                           node_ids=[1, 2, 3])
    """
    # Create a NChooserEventCoordinatorHIV with the intervention
    coordinator = NChooserEventCoordinatorHIV(campaign, intervention_list=intervention_list,
                                              targeted_distributions=targeted_distributions)
    # Create a CampaignEventByYear object with the coordinator
    event = create_campaign_event(campaign, coordinator=coordinator, event_name=event_name, node_ids=node_ids,
                                  start_day=None, start_year=start_year)

    # Add the event to the campaign
    campaign.add(event.to_schema_dict(campaign))


def add_intervention_reference_tracking(campaign: api_campaign,
                                        intervention_list: list[IndividualIntervention],
                                        time_value_map: ValueMap,
                                        tracking_config: AbstractTargetingConfig,
                                        start_year: float,
                                        end_year: float = 2200,
                                        update_period: float = 365,
                                        target_demographics_config: TargetDemographicsConfig = TargetDemographicsConfig(demographic_coverage=None),
                                        property_restrictions: PropertyRestrictions = None,
                                        targeting_config: AbstractTargetingConfig = None,
                                        event_name: str = None,
                                        node_ids: list[int] = None) -> None:
    """
    Distribute interventions to the population such that a user determined coverage of an attribute is maintained over
    time.

    This function creates a "tracker" that will track the prevalence of a specific attribute in the population and
    distribute interventions to achieve the desired coverage. The tracker will periodically poll the population to
    determine the current prevalence of the attribute and distribute the number of interventions needed to get
    prevalence up to the desired value. If prevalence is higher than the desired value, then no interventions will be
    distributed. Other things outside of this tracker (like expiration timers in the intervention) maybe needed to
    cause the coverage to stay down to the desired coverage.

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the intervention will be added.
        intervention_list (list[IndividualIntervention], required):
            - A list of IndividualIntervention objects. NodeIntervention is not supported in this feature.
            - Refer to the emodpy_hiv.campaign.individual_intervention module for available IndividualIntervention derived classes.
        time_value_map (ValueMap, required):
            - A ValueMap object that defines the target coverage levels over time.
        tracking_config (AbstractTargetingConfig, required):
            - An AbstractTargetingConfig object that defines the attribute to be tracked within the targeted group.
            - The number of individuals with this attribute is used as the numerator for coverage calculations.
            - The number of individual selected via targeting_config, target_demographics, and property_restrictions determine the denominator.
            - Please refer to the emodpy_hiv.utils.targeting_config module for more information.
        start_year (float, required):
            - The year to start distributing the intervention.
            - Defines the start of the time period over which the intervention will be distributed.
            - Minimum value: 1900,
            - Maximum value: 2200.
        end_year (float, optional):
            - The year to stop distributing the intervention.
            - Defines the end of the time period over which the intervention will be distributed.
            - Minimum value: 1900,
            - Maximum value: 2200,
            - Default value: 2200.
        update_period (float, optional):
            - The time period in days between when the tracker polls the population and determines if it should
              distribute more interventions.
            - Minimum value: 1,
            - Maximum value: 3650,
            - Default value: 365.
        target_demographics_config (TargetDemographicsConfig, optional):
            - A TargetDemographicsConfig to define the demographic characteristics of individuals targeted by the intervention.
            - Please refer to the emodpy_hiv.campaign.common.TargetDemographicsConfig module for more information.
            - Please note that the demographic_coverage is not used in this coordinator. Use TargetDemographicsConfig(demographic_coverage=None) to avoid errors.
            - Default value: TargetDemographicsConfig(demographic_coverage=None).
        property_restrictions (PropertyRestrictions, optional):
            - A PropertyRestrictions object that defines individual-level property restrictions for the intervention.
            - Node property restrictions are not supported.
            - Default value: None.
        targeting_config (AbstractTargetingConfig, optional):
            - An AbstractTargetingConfig to define who to target individuals with the intervention besides the
              target_demographics_config and property_restrictions.
            - Please note that when defining the target group, you do NOT want to specify the negative what you want to
              track. because the number of people in the target group is your denominator when calculating coverage.
              For example, if you want the tracker to have 50% of men circumcised, then you need men who are both
              circumcised and not circumcised in the denominator and only the number circumcised men in the numerator.
            - Please refer to the emodpy_hiv.utils.targeting_config module for more information.
            - Default value: None.
        event_name (str, optional):
            - The name of the campaign event.
            - Default value: None.
        node_ids (list[int], optional):
            - A list of node IDs to which the intervention should be applied.
            - If None, the intervention is applied to all nodes.
            - Default value: None.

    Returns:
        None: This function does not return anything. It modifies the campaign object in place.

    Examples:
        Use a reference tracker to ensure that the fraction of medium risk men that are circumcised meets certain
        levels each year from 1960 through 1965 where the tracker is updating who is circumcised every 6 months (182 days)
        If coverage is below the target level at the time of polling, apply the MaleCircumcision
        intervention to uncircumcised men to reach the target coverage.

        Please note that you don't need to specify the negative of what you want to track(~IsCircumcised()) in the
        targeting_config. See more details in the targeting_config argument description.

        >>> import emod_api
        >>> from emodpy_hiv.campaign.distributor import add_intervention_reference_tracking
        >>> from emodpy_hiv.campaign.individual_intervention import MaleCircumcision
        >>> from emodpy_hiv.campaign.common import (ValueMap, TargetGender, CommonInterventionParameters as CIP,
        >>>                                        TargetDemographicsConfig as TDC)
        >>> from emodpy_hiv.utils.targeting_config import IsCircumcised, HasIP
        >>>
        >>> campaign_obj = emod_api.campaign
        >>> campaign_obj.schema_path = 'path_to_schema'
        >>> mc = MaleCircumcision(campaign_obj,
        >>>                       distributed_event_trigger='VMMC_1')
        >>> time_value_map = ValueMap(times=[1960,  1961,   1962,   1963,   1964],
        >>>                          values=[0.25,  0.375,  0.4,    0.4375, 0.46875])
        >>> targeting_config = HasIP(ip_key_value="Risk:MEDIUM")
        >>> tracking_config = IsCircumcised()
        >>> add_intervention_reference_tracking(campaign_obj,
        >>>                                     intervention_list=[mc],
        >>>                                     time_value_map=time_value_map,
        >>>                                     tracking_config=tracking_config,
        >>>                                     targeting_config=targeting_config,
        >>>                                     start_year=1960,
        >>>                                     end_year=1965,
        >>>                                     update_period=182,
        >>>                                     target_demographics_config=TDC(target_gender=TargetGender.MALE))
    """
    if not isinstance(time_value_map, ValueMap):
        raise ValueError("The time_value_map should be an instance of the ValueMap class.")
    # Validate the start_year and end_year
    if end_year <= start_year:
        raise ValueError("The end_year should be greater than the start_year.")
    # All years in ValueMap should be within the start_year and end_year
    if all([year < start_year or year > end_year for year in time_value_map._times]):
        raise ValueError("All years in the time_value_map is not within the start_year and end_year.")
    # At lease one year in the ValueMap is not within the start_year and end_year
    if any([year < start_year or year > end_year for year in time_value_map._times]):
        warnings.warn("At least one year in the time_value_map is not be within the start_year and end_year."
                      "Please make sure that is intended.\n"
                      f"start_year: {start_year}, end_year: {end_year}, years in time_value_map: {time_value_map._times}.",
                      category=UserWarning)

    # Create a ReferenceTrackingEventCoordinatorTrackingConfig with the intervention_list
    coordinator = ReferenceTrackingEventCoordinatorTrackingConfig(campaign,
                                                                  intervention_list=intervention_list,
                                                                  time_value_map=time_value_map,
                                                                  targeting_config=targeting_config,
                                                                  tracking_config=tracking_config,
                                                                  end_year=end_year,
                                                                  update_period=update_period,
                                                                  target_demographics_config=target_demographics_config,
                                                                  property_restrictions=property_restrictions,
                                                                  )
    # Create a CampaignEventByYear object with the coordinator
    event = create_campaign_event(campaign, coordinator=coordinator, event_name=event_name, node_ids=node_ids,
                                  start_day=None, start_year=start_year)

    # Add the event to the campaign
    campaign.add(event.to_schema_dict(campaign))


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [add_intervention_scheduled, add_intervention_triggered, _add_intervention_nchooser,
                 add_intervention_nchooser_df, add_intervention_reference_tracking]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.
# During the documentation build with Sphinx, these classes will be displayed as belonging to the 'emodpy_hiv' package,
# not the 'emodpy' package.
# For example, the 'PropertyRestrictions' class will be documented as 'emodpy_hiv.campaign.common.PropertyRestrictions(...)'.
# This is crucial for accurately representing the source of these classes in the documentation.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
