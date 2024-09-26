from typing import List, Any, Dict, Union, Optional

import pandas as pd
from emod_api import campaign
from emod_api import schema_to_class as s2c
from emod_api.interventions import utils
from emodpy_hiv.interventions import malecirc


def new_target_distribution(
        camp: campaign,
        age_ranges_years: List[List[Union[float]]],
        start_year: float,
        end_year: float,
        num_targeted_females: List[int],
        num_targeted_males: List[int],
        num_targeted: List[int] = None,
        property_restrictions_within_node: List[Dict[str, Any]] = None,
        target_disease_state: List[List[str]] = None,
        target_disease_state_has_intervention_name: str = None
) -> Dict:
    """

    Configures a new target distribution for a campaign, specifying when, to whom, and how many interventions are
    distributed.

    Args:
        camp (campaign):                                  The campaign object to which the target distribution will be
                                                          added.
        age_ranges_years (List[List[Union[float]], List[Union[float]]]): A 2D list specifying age ranges for
                                                          qualifying individuals.It should contain 2 lists, the first
                                                          list is 'Max' age and the second list for 'Min' age.
        start_year (float):                               The year to start distributing the intervention.
        end_year (float):                                 The year to stop distributing the intervention.
        num_targeted_females (List[int]):                 The number of female individuals to target.
        num_targeted_males (List[int]):                   The number of male individuals to target.
        num_targeted (List[int], optional):               The number of individuals to target with the intervention.
                                                          Default to None.
        property_restrictions_within_node (List[Dict[str, Any]], optional): A list of property restrictions, each
                                                          represented as a dict with keys as property names and values
                                                          as property values. Default to None.
        target_disease_state (List[List[str]], optional): A 2D list specifying targeted disease states. Default to None.
                                                          To qualify for the intervention, an individual must have only
                                                          one of the targeted disease states. An individual must have
                                                          all the disease states in the inner array. Possible values
                                                          are: HIV_Positive, HIV_Negative, Tested_Positive,
                                                          Tested_Negative, Male_Circumcision_Positive,
                                                          Male_Circumcision_Negative, Has_Intervention,
                                                          Not_Have_Intervention.
        target_disease_state_has_intervention_name (str, optional): The name of the intervention to look for in
                                                          an individual when targeting specific disease states (
                                                          'Has_Intervention' or 'Not_Have_Intervention').
                                                          Default to None.

    Returns:
        A dictionary representing a target distribution configuration for the campaign.

    Example:
        >>> camp = emod_api.campaign
        >>> age_ranges_years = [[0.99999, 14.9999999, 49.9999, 64.9999],   # Max ages
        >>>                     [0,       1,          15,      50]]        # Min ages
        >>> num_targeted_females = [0,    0,          0,       0]
        >>> num_targeted_males = [0, 8064.777513, 25054.39959, 179.0207223]
        >>> distribution = new_target_distribution(camp=camp,
        >>>                                        age_ranges_years=age_ranges_years,
        >>>                                        start_year=2010.0,
        >>>                                        end_year=2010.999,
        >>>                                        num_targeted_females=num_targeted_females,
        >>>                                        num_targeted_males=num_targeted_males,
        >>>                                        target_disease_state=[["Not_Have_Intervention"]],
        >>>                                        target_disease_state_has_intervention_name="DMPA_or_control")

    """
    distribution = s2c.get_class_with_defaults("idmType:TargetedDistributionHIV", camp.schema_path)

    # Check if age_ranges_years is a 2D list contains 2 lists with the same length
    if len(age_ranges_years) != 2:
        raise ValueError("The age_ranges_years must contains exactly 2 lists.")
    else:
        max_ages, min_ages = age_ranges_years
        if not isinstance(max_ages, list) or not isinstance(min_ages, list) or len(max_ages) != len(min_ages):
            raise ValueError("The age_ranges_years must contains 2 lists with the same length.")

        # Get the total number of age ranges
        num_of_age_ranges = len(max_ages)

        # The num_targeted lists in the intervention should have the same length
        if len(num_targeted_males) != len(num_targeted_females) != num_of_age_ranges:
            raise ValueError("num_targeted_males and num_targeted_females should have the same length "
                             "as age ranges.")

        if num_targeted and len(num_targeted) != num_of_age_ranges:
            raise ValueError("num_targeted should have the same length as age ranges.")

        if start_year > end_year:
            raise ValueError(f"start_year: {start_year} should be less than end_year: {end_year}.")
        # Turn the age_ranges_years into a list of dictionaries each has a 'Min' and 'Max' age.
        age_ranges_years_list = list()
        for max_age, min_age in zip(max_ages, min_ages):
            if max_age < min_age:
                raise ValueError(f"Max age: {max_age} should be larger than min age: {min_age}.")
            age_ranges_years_list.append({"Max": float(max_age),
                                          "Min": float(min_age)})

        distribution.Age_Ranges_Years = age_ranges_years_list
        distribution.End_Year = float(end_year)
        distribution.Start_Year = float(start_year)
        distribution.Num_Targeted_Females = num_targeted_females.copy()
        distribution.Num_Targeted_Males = num_targeted_males.copy()
        if num_targeted:
            distribution.Num_Targeted = num_targeted.copy()
        if property_restrictions_within_node:
            distribution.Property_Restrictions_Within_Node = property_restrictions_within_node.copy()
        # Update distribution target disease state:
        if target_disease_state:
            distribution.Target_Disease_State = target_disease_state.copy()
            intervention_states = ['Has_Intervention', 'Not_Have_Intervention']
            # Check for the presence of intervention states: 'Has_Intervention' or 'Not_Have_Intervention'
            contains_intervention = any(state in row for row in target_disease_state for state in intervention_states)
            if contains_intervention and not target_disease_state_has_intervention_name:
                raise ValueError("If using 'Has_Intervention' or 'Not_Have_Intervention' in Target_Disease_State, "
                                 "you must also define 'Target_Disease_State_Has_Intervention_Name' to the name of"
                                 " the intervention.")
            elif not contains_intervention and target_disease_state_has_intervention_name:
                raise ValueError("You are setting 'Target_Disease_State_Has_Intervention_Name' but Target_Disease_State"
                                 " has no 'Has_Intervention' or 'Not_Have_Intervention'.")
            elif contains_intervention:
                distribution.Target_Disease_State_Has_Intervention_Name = target_disease_state_has_intervention_name
        elif target_disease_state_has_intervention_name:
            raise ValueError(
                "You are setting 'Target_Disease_State_Has_Intervention_Name' but Target_Disease_State is empty.")

        return distribution


def add_nchooser_event(
        camp: campaign,
        target_distributions: list,
        intervention_config,
        start_day: Union[int, float] = 1,
        event_name: str = '',
        node_ids: Optional[List[int]] = None
) -> None:
    """

    Creates a new NChooserEventCoordinatorHIV event in the specified EMOD campaign.

    This function adds a new event to an EMOD campaign object. It configures the event with specific
    intervention configurations and distributions, targeting specific nodes from a defined start year.

    Please refer to the documentation for NChooserEventCoordinatorHIV at the following link:
    :doc:`emod/parameter-campaign-event-nchoosereventcoordinatorhiv`.

    Args:
        camp (emod_api.campaign):                             The campaign object to which the event will be added. This
                                                              should be an instance of the emod_api.campaign class.
        target_distributions (list[TargetedDistributionHIV]): A list of distribution configurations for the event. Each
                                                              distribution configuration dictates how the intervention
                                                              is distributed among the population.
        intervention_config (Intervention):                   An Emod Intervention object.
        start_day (int | float, optional):                    The day when the event starts. Defaults to 1.
        event_name (str, optional):                           The name of the campaign event, default to empty string.
        node_ids (list of int, optional):                     A list of node IDs where the event will be applied. If
                                                              None, the event applies to all nodes. Defaults to None.

    Returns:
        None: This function does not return anything. It modifies the campaign object in place.

    Examples:
        >>> import emod_api
        >>> from emodpy_hiv.interventions import malecirc, nchooser
        >>>
        >>> campaign_obj = emod_api.campaign
        >>> intervention_config = malecirc.new_intervention(campaign_obj)
        >>> distribution_1 = nchooser.new_target_distribution(campaign_obj, ...)
        >>> distribution_2 = nchooser.new_target_distribution(campaign_obj, ...)
        >>> distributions = [distribution_1, distribution_2]
        >>> nchooser.add_nchooser_event(campaign_obj, distributions, intervention_config, start_day=365,
        >>>                             node_ids=[1, 2, 3])

    """
    # NChooster Coordinator
    nchooser = s2c.get_class_with_defaults("NChooserEventCoordinatorHIV", camp.schema_path)
    if not target_distributions or not intervention_config:
        raise ValueError("target_distributions and intervention_config should not be empty.")
    nchooser.Distributions = target_distributions
    nchooser.Intervention_Config = intervention_config

    # Event
    event = s2c.get_class_with_defaults("CampaignEvent", camp.schema_path)
    event.Event_Coordinator_Config = nchooser
    event.Start_Day = float(start_day)
    event.Nodeset_Config = utils.do_nodes(camp.schema_path, node_ids)
    if event_name:
        # event.Event_Name = event_name
        event['Event_Name'] = event_name  # Event_Name is not in Schema
    camp.add(event)


def add_nchooser_distributed_circumcision_event(camp: campaign,
                                                target_disease_state: List[List[str]],
                                                has_intervention_name_exclusion: str,
                                                distributions: pd.DataFrame,
                                                property_restrictions: List[Dict[str, Any]] = None,
                                                circumcision_reduced_acquire: float = 0.6,
                                                distributed_event_trigger: str = 'Program_VMMC',
                                                start_day: Union[int, float] = 1,
                                                event_name: str = '',
                                                node_ids: Optional[List[int]] = None
                                                ) -> None:
    """

    Creates a new NChooserEventCoordinatorHIV event in the specified EMOD campaign with a MaleCircumcision intervention and
    Distributions specified in distributions dataframe.

    Args:
        camp (emod_api.campaign):                       The campaign object to which the event will be added. This
                                                        should be an instance of  the emod_api.campaign class.
        target_disease_state (List[List[str]]):         A 2D list specifying targeted disease states.
        has_intervention_name_exclusion (str):          The name of the intervention to look for in an individual when
                                                        targeting specific disease states. It's also the
                                                        Intervention_Name of the MaleCircumcision intervention.
        distributions:                                  A DataFrame contains the data for these columns: year, min_age,
                                                        max_age, n_circumcisions.
        property_restrictions (List[Dict[str, Any]], optional):  A list of property restrictions, each represented as
                                                                 a dict with keys as property names and values as
                                                                 property values. Deafult to None.
        circumcision_reduced_acquire (Float, optional): Circumcision_Reduced_Acquire parameter: The reduction of
                                                        susceptibility to STI by voluntary male medical circumcision
                                                        (VMMC). Default to 0.6.
        distributed_event_trigger(str, optional):       This is the event that is broadcasted when the circumcision is
                                                        distributed to the man. One could add it to a report to say
                                                        count the number of men who were circumcised during the
                                                        reporting period. Default to 'Program_VMMC'.
        start_day(int | float, optional):               The day when the event starts. Defaults to 1.
        event_name(str, optional):                      The name of the campaign event, default to empty string.
        node_ids (list of int, optional):               A list of node IDs where the event will be applied. If None,
                                                        the event applies to all nodes. Defaults to None.

    Returns:
            None: This function does not return anything. It modifies the campaign object in place.

    Examples:
        >>> import emod_api
        >>> from emodpy_hiv.interventions import nchooser
        >>> import pandas as pd
        >>>
        >>> campaign_obj = emod_api.campaign
        >>> target_disease_state = [["HIV_Negative", "Not_Have_Intervention"]]
        >>> has_intervention_name_exclusion = 'MaleCircumcision'
        >>> data = {'year': [2010, 2010, 2011, 2011],
        >>>         'min_age': [1, 15, 1, 15],
        >>>         'max_age': [14.999, 49.999, 14.999, 49.999],
        >>>         'n_circumcisions': [200, 1300, 290, 1490]}
        >>> distributions = pd.DataFrame.from_dict(data)
        >>> nchooser.add_nchooser_distributed_circumcision_event(campaign_obj, target_disease_state,
        >>>                                                      has_intervention_name_exclusion, distributions,
        >>>                                                      start_day=365, node_ids=[1, 2, 3])

    """
    if not {'year', 'min_age', 'max_age', 'n_circumcisions'}.issubset(distributions.columns):
        raise ValueError("Expected these columns: 'year', 'min_age', 'max_age', 'n_circumcisions' in the distributions "
                         f"dataframe. Got distributions.columns: {distributions.columns}")
    target_distributions = []
    # Get the unique value of target years from the distribution dataframe
    target_years = distributions.year.unique()
    # Created the distribution objects for each target year
    for year in target_years:
        # Filter the distribution dataframe with year
        df_cur_year = distributions[distributions['year'] == year].sort_values(by=['min_age'])
        # Max and Min age ranges for qualifying individuals.
        age_ranges_years = [df_cur_year['max_age'].tolist(), df_cur_year['min_age'].tolist()]
        # num_targeted_males is the values in n_circumcisions column,
        # num_targeted_females contains 0s with the same length.
        num_targeted_males = df_cur_year['n_circumcisions'].tolist()
        num_targeted_females = [0] * len(num_targeted_males)

        target_distribution = new_target_distribution(camp,
                                                      age_ranges_years=age_ranges_years,
                                                      start_year=float(year),
                                                      end_year=float(year) + 0.999,
                                                      num_targeted_females=num_targeted_females,
                                                      num_targeted_males=num_targeted_males,
                                                      property_restrictions_within_node=property_restrictions,
                                                      target_disease_state=target_disease_state,
                                                      target_disease_state_has_intervention_name=
                                                      has_intervention_name_exclusion)
        target_distributions.append(target_distribution)
    # Create a MaleCircumcision intervention
    intervention = malecirc.new_intervention(camp)
    intervention.Circumcision_Reduced_Acquire = circumcision_reduced_acquire
    intervention.Distributed_Event_Trigger = camp.get_send_trigger(distributed_event_trigger, True)
    intervention.Intervention_Name = has_intervention_name_exclusion

    # Call the add_nchooser_event function to add the MaleCircumcision with target_distributions
    add_nchooser_event(camp, target_distributions=target_distributions, intervention_config=intervention,
                       start_day=start_day, event_name=event_name, node_ids=node_ids)

