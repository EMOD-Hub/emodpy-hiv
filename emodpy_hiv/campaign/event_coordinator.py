from emod_api import campaign as api_campaign, schema_to_class as s2c

from emodpy.campaign.base_intervention import IndividualIntervention, NodeIntervention
from emodpy.campaign.event_coordinator import InterventionDistributorEventCoordinator
from emodpy_hiv.campaign.common import TargetDemographicsConfig, ValueMap, PropertyRestrictions, NChooserTargetedDistributionHIV
from emodpy_hiv.utils.targeting_config import AbstractTargetingConfig

from typing import Union

# ported from emodpy/campaign/event_coordinator.py
# The StandardEventCoordinator coordinator class distributes an individual-level or node-level intervention to
# a specified fraction of individuals or nodes within a node set.
from emodpy.campaign.event_coordinator import StandardEventCoordinator


class NChooserEventCoordinatorHIV(InterventionDistributorEventCoordinator):
    """
    The NChooserEventCoordinatorHIV coordinator class distributes individual-level interventions to
    exactly N people of a targeted demographic in HIV simulations. This contrasts with other event coordinators that
    distribute an intervention to a percentage of the population, not to an exact count. This event coordinator is
    similar to the NChooserEventCoordinator for other simulation types, but replaces start and end days in
    TargetedDistribution with start and end years in TargetedDistributionHIV and includes HIV-specific restrictions that
    individuals must have in order to qualify for the intervention.

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the event will be added.
        intervention_list (list[IndividualIntervention], required):
            - A list of individual-level interventions to be distributed.
        targeted_distributions (list[TargetedDistributionHIV], required):
            - A list of TargetedDistributionHIV objects specifying when, to whom, and how many interventions are distributed.
    """
    def __init__(self,
                 campaign: api_campaign,
                 intervention_list: list[IndividualIntervention],
                 targeted_distributions: list[NChooserTargetedDistributionHIV]):
        """
        NChooserEventCoordinatorHIV class to create a
        """
        super().__init__(campaign, "NChooserEventCoordinatorHIV", intervention_list)

        self._coordinator.Distributions = [targeted_distribution.to_schema_dict(campaign)
                                           for targeted_distribution in targeted_distributions]


class ReferenceTrackingEventCoordinatorTrackingConfig(InterventionDistributorEventCoordinator):
    """
    The ReferenceTrackingEventCoordinatorTrackingConfig coordinator class defines a particular prevalence of an
    individual-level attribute that should be present in a population over time, and a corresponding intervention that
    will cause individuals to acquire that attribute. The coordinator tracks the actual prevalence of that attribute
    against the desired prevalence; it will poll the population of nodes it has been assigned to determine how many
    people have the attribute. When coverage is less than the desired prevalence, it will distribute enough of the
    designated intervention to reach the desired prevalence. This coordinator is similar to the
    ReferenceTrackingEventCoordinator, but allows an attribute in the population to be polled, not only the intervention
    itself having been received. This allows for tracking overall coverage when, potentially, multiple routes exist for
    individuals to have acquired the same target attribute.

    Args:
        campaign (api_campaign, required):
            - The campaign object to which the event will be added.
        intervention_list (list[IndividualIntervention], required):
            - A list of individual-level interventions to be distributed.
        time_value_map (ValueMap, required):
            - A ValueMap object to map coverages over a defined range of time.
        tracking_config (AbstractTargetingConfig, required):
            - An AbstractTargetingConfig to define the attribute to be tracked within the targeted group.
            - The number of people that have this attribute is the numerator while the other targeting parameters define the denominator of the coverage.
            - The intervention will be distributed to people without the attribute, if coverage is below the target level the time of polling.
        end_year (float, optional):
            - The year to stop distributing the intervention.
            - Defines the time period to distribute the intervention along with start_year. The intervention is evenly distributed between each time step in the time period.
            - Minimum value: 1900,
            - Maximum value: 2200,
            - Default value: 2200.
        update_period (float, optional):
            - The time period in days between updates to the intervention distribution.
            - Minimum value: 1,
            - Maximum value: 3650,
            - Default value: 365.
        target_demographics_config (TargetDemographicsConfig, optional):
            - A TargetDemographicsConfig to define the demographic characteristics of individuals targeted by the intervention.
            - Please refer to the emodpy_hiv.campaign.common.TargetDemographicsConfig module for more information.
            - Please note that the demographic_coverage is not used in this coordinator. Use TargetDemographicsConfig(demographic_coverage=None) to avoid errors.
            - Default value: TargetDemographicsConfig(demographic_coverage=None).
        property_restrictions (PropertyRestrictions, optional):
            - A PropertyRestrictions to define the individual-level or node-level property restrictions in the coordinator.
            - Default value: None.
        targeting_config (AbstractTargetingConfig, optional):
            - An AbstractTargetingConfig to define who to target individuals with the intervention besides the target_demographics_config and property_restrictions.
            - Please refer to the emodpy_hiv.utils.targeting_config module for more information.
            - Default value: None.
    """
    def __init__(self,
                 campaign: api_campaign,
                 intervention_list: list[IndividualIntervention],
                 time_value_map: ValueMap,
                 targeting_config: AbstractTargetingConfig,
                 tracking_config: AbstractTargetingConfig,
                 end_year: float = 2200,
                 update_period: float = 365,
                 target_demographics_config: TargetDemographicsConfig = TargetDemographicsConfig(demographic_coverage=None),
                 property_restrictions: PropertyRestrictions = None):

        super().__init__(campaign, "ReferenceTrackingEventCoordinatorTrackingConfig", intervention_list)

        if not all(isinstance(intervention, IndividualIntervention) for intervention in intervention_list):
            raise ValueError("intervention_list should contain only IndividualIntervention objects.")

        if target_demographics_config is not None:
            if target_demographics_config.demographic_coverage is not None:
                raise ValueError("The demographic_coverage parameter is not used in this coordinator. "
                                 "Use TargetDemographicsConfig(demographic_coverage=None) to avoid errors.")
            target_demographics_config._set_target_demographics(self._coordinator)
        if property_restrictions is not None:
            property_restrictions._set_property_restrictions(self._coordinator)
        if targeting_config is not None:
            self._coordinator.Targeting_Config = targeting_config.to_schema_dict(campaign)


        self._coordinator.End_Year = end_year
        self._coordinator.Update_Period = update_period
        self._coordinator.Time_Value_Map = time_value_map.to_schema_dict(campaign)
        self._coordinator.Tracking_Config = tracking_config.to_simple_dict(campaign)


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [StandardEventCoordinator, NChooserEventCoordinatorHIV,
                 ReferenceTrackingEventCoordinatorTrackingConfig]

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
