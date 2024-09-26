from typing import List, Optional
from emod_api import campaign
from emod_api import schema_to_class as s2c
from emod_api.interventions import common
import copy


def new_intervention(camp: campaign,
                     muxer_name: str,
                     delay_complete_event: str,
                     delay_distribution: str,
                     delay_period_exponential: float = None,
                     delay_period_kappa: float = None,
                     delay_period_lambda: float = None,
                     delay_period_constant: float = None,
                     disqualifying_properties: Optional[List[str]] = None,
                     max_entries: float = 1,
                     new_property_value: str = None
                     ):
    """

    Create a HIVMuxer intervention object and return it.
    Please refer to the documentation for HIVMuxer at the following link:
    :doc:`emod/parameter-campaign-individual-hivmuxer`.


    Args:
        camp (emod_api.campaign): The campaign object to which the event will be added. This should be an instance of
            the emod_api.campaign class.
        muxer_name (str): A name used to identify the delay and check whether individuals have entered it multiple
            times. If the same name is used at multiple points in the health care process, then the number of entries
            is combined when Max_Entries is applied.
        delay_complete_event (str): The event that should occur at the end of the delay period.
        delay_distribution (str): The delay distribution type for the event. Possible values are CONSTANT_DISTRIBUTION,
            EXPONENTIAL_DISTRIBUTION and WEIBULL_DISTRIBUTION.
        delay_period_exponential (float, optional): The mean for an exponential distribution. Required for
            delay_distribution = EXPONENTIAL_DISTRIBUTION. Defaults to None.
        delay_period_kappa (float, optional): The shape value in a Weibull distribution. Required for delay_distribution
            = WEIBULL_DISTRIBUTION. Defaults to None.
        delay_period_lambda (float, optional): The scale value in a Weibull distribution. Required for
            delay_distribution = WEIBULL_DISTRIBUTION. Defaults to None.
        delay_period_constant (float, optional): The constant delay period. Required for delay_distribution
            = CONSTANT_DISTRIBUTION. Defaults to None.
        disqualifying_properties (List[str], optional): A list of IndividualProperty key:value pairs that cause an
            intervention to be aborted. Generally used to control the flow of health care access. For example, to
            prevent the same individual from accessing health care via two different routes at the same time.
        max_entries (float, optional): The maximum number of times the individual can be registered with the HIVMuxer
            delay. Determines what should happen if an individual reaches the HIVMuxer stage of health care multiple
            times. Defaults to 1.
        new_property_value (str, optional): An optional IndividualProperty key:value pair that will be assigned when the
            intervention is first updated. Generally used to indicate the broad category of health care cascade to which
            an intervention belongs to prevent individuals from accessing care through multiple pathways.

    Returns:
        intervention

    Raises:
        ValueError: If invalid input is provided.

    """
    intervention = s2c.get_class_with_defaults("HIVMuxer", camp.schema_path)
    intervention.Broadcast_Event = camp.get_send_trigger(delay_complete_event, True)
    intervention.Delay_Period_Distribution = delay_distribution
    if delay_distribution == 'CONSTANT_DISTRIBUTION':
        if not delay_period_constant:
            raise ValueError("delay_period_constant is required for CONSTANT_DISTRIBUTION.")
        intervention.Delay_Period_Constant = delay_period_constant
    elif delay_distribution == 'EXPONENTIAL_DISTRIBUTION':
        if not delay_period_exponential:
            raise ValueError("delay_period_exponential is required for EXPONENTIAL_DISTRIBUTION.")
        intervention.Delay_Period_Exponential = delay_period_exponential
    elif delay_distribution == 'WEIBULL_DISTRIBUTION':
        if not delay_period_kappa or not delay_period_lambda:
            raise ValueError("delay_period_kappa and delay_period_lambda are required for EXPONENTIAL_DISTRIBUTION.")
        intervention.Delay_Period_Kappa = delay_period_kappa
        intervention.Delay_Period_Lambda = delay_period_lambda
    else:
        raise NotImplementedError("delay_distribution supports CONSTANT_DISTRIBUTION, EXPONENTIAL_DISTRIBUTION and "
                                  "WEIBULL_DISTRIBUTION for now, contact us if you want more to use other delay "
                                  "distributions.")
    intervention.Disqualifying_Properties = disqualifying_properties.copy()
    intervention.Max_Entries = max_entries
    intervention.Muxer_Name = muxer_name
    intervention.New_Property_Value = new_property_value
    return intervention


def add_hiv_muxer_event_with_trigger(camp: campaign,
                                     start_day: int,
                                     event_trigger_list: List[str],
                                     muxer_name: str,
                                     delay_complete_event: str,
                                     delay_distribution: str,
                                     delay_period_exponential: float = None,
                                     delay_period_kappa: float = None,
                                     delay_period_lambda: float = None,
                                     delay_period_constant: float = None,
                                     disqualifying_properties: Optional[List[str]] = None,
                                     demographic_coverage: float = 1,
                                     event_name: str = 'HIVMuxer with NLHTI',
                                     new_property_value: str = None,
                                     node_ids: Optional[List[int]] = None
                                     ) -> None:
    """

    Add HIVMuxer intervention with NodeLevelHealthTriggeredIV to campaign object
    Please refer to the documentation for HIVMuxer at the following link:
    :doc:`emod/parameter-campaign-individual-hivmuxer`.

    Args:
        camp (emod_api.campaign): The campaign object to which the event will be added. This should be an instance of
            the emod_api.campaign class.
        start_day (int): The starting day for the event.
        event_trigger_list (list): A list of triggers for the event.
        muxer_name (str): A name used to identify the delay and check whether individuals have entered it multiple
            times. If the same name is used at multiple points in the health care process, then the number of entries
            is combined when Max_Entries is applied.
        delay_complete_event (str): The event that should occur at the end of the delay period.
        delay_distribution (str): The delay distribution type for the event. Possible values are CONSTANT_DISTRIBUTION,
            EXPONENTIAL_DISTRIBUTION and WEIBULL_DISTRIBUTION.
        delay_period_exponential (float, optional): The mean for an exponential distribution. Required for
            delay_distribution = EXPONENTIAL_DISTRIBUTION. Defaults to None.
        delay_period_kappa (float, optional): The shape value in a Weibull distribution. Required for delay_distribution
            = WEIBULL_DISTRIBUTION. Defaults to None.
        delay_period_lambda (float, optional): The scale value in a Weibull distribution. Required for
            delay_distribution = WEIBULL_DISTRIBUTION. Defaults to None.
        delay_period_constant (float, optional): The constant delay period. Required for delay_distribution =
            CONSTANT_DISTRIBUTION. Defaults to None.
        disqualifying_properties (List[str], optional): A list of IndividualProperty key:value pairs that cause an
            intervention to be aborted. Generally used to control the flow of health care access. For example, to
            prevent the same individual from accessing health care via two different routes at the same time.
        demographic_coverage (float, optional): The demographic coverage for the event. Defaults to 1.
        event_name (str, optional): The name of the event. Defaults to 'HIVMuxer with NLHTI'.
        new_property_value (str, optional): An optional IndividualProperty key:value pair that will be assigned when the
            intervention is first updated. Generally used to indicate the broad category of health care cascade to which
            an intervention belongs to prevent individuals from accessing care through multiple pathways.
        node_ids (List[int], optional): A list of node IDs. Defaults to None.

    Returns:
        None

    Raises:
        ValueError: If invalid input is provided.

    Example:
        >>> add_hiv_muxer_event_with_trigger(
        >>>     camp,
        >>>     start_day=10,
        >>>     event_trigger_list=['HCTUptakePostDebut1'],
        >>>     muxer_name='HCTUptakePostDebut',
        >>>     new_property_value='CascadeState:HCTUptakePostDebut',
        >>>     delay_complete_event='HCTUptakePostDebut2',
        >>>     delay_distribution='EXPONENTIAL_DISTRIBUTION',
        >>>     delay_period_exponential=0.5,
        >>>     disqualifying_properties=[
        >>>                     "CascadeState:LostForever",
        >>>                     "CascadeState:OnART",
        >>>                     "CascadeState:LinkingToART",
        >>>                     "CascadeState:OnPreART",
        >>>                     "CascadeState:LinkingToPreART",
        >>>                     "CascadeState:ARTStaging",
        >>>                     "CascadeState:HCTTestingLoop"],
        >>>     demographic_coverage=0.5,
        >>>     node_ids=[1, 2, 3]
        >>> )

    """
    intervention = new_intervention(camp,
                                    muxer_name=muxer_name,
                                    delay_complete_event=delay_complete_event,
                                    delay_distribution=delay_distribution,
                                    delay_period_exponential=delay_period_exponential,
                                    delay_period_kappa=delay_period_kappa,
                                    delay_period_lambda=delay_period_lambda,
                                    delay_period_constant=delay_period_constant,
                                    disqualifying_properties=disqualifying_properties,
                                    new_property_value=new_property_value)
    intervention_list = [intervention]

    event = common.TriggeredCampaignEvent(camp,
                                          Start_Day=start_day,
                                          Event_Name=event_name,
                                          Node_Ids=node_ids,
                                          Triggers=event_trigger_list.copy(),
                                          Demographic_Coverage=demographic_coverage,
                                          Intervention_List=copy.deepcopy(intervention_list))
    camp.add(event)
