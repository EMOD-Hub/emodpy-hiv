import emod_api.schema_to_class as s2c

from emodpy.utils import validate_key_value_pair
from emodpy.campaign.individual_intervention import BroadcastEvent as BroadcastEvent
from emodpy.campaign.individual_intervention import BroadcastEventToOtherNodes as BroadcastEventToOtherNodes
from emodpy.campaign.individual_intervention import ControlledVaccine as ControlledVaccine
from emodpy.campaign.individual_intervention import DelayedIntervention as DelayedIntervention
from emodpy.campaign.individual_intervention import IndividualImmunityChanger as IndividualImmunityChanger
from emodpy.campaign.individual_intervention import IndividualNonDiseaseDeathRateModifier as IndividualNonDiseaseDeathRateModifier
from emodpy.campaign.individual_intervention import MigrateIndividuals as MigrateIndividuals
from emodpy.campaign.individual_intervention import MultiEffectBoosterVaccine as MultiEffectBoosterVaccine
from emodpy.campaign.individual_intervention import MultiEffectVaccine as MultiEffectVaccine
from emodpy.campaign.individual_intervention import MultiInterventionDistributor as MultiInterventionDistributor
from emodpy.campaign.individual_intervention import OutbreakIndividual as OutbreakIndividual
from emodpy.campaign.individual_intervention import PropertyValueChanger as PropertyValueChanger
from emodpy.campaign.individual_intervention import SimpleBoosterVaccine as SimpleBoosterVaccine
from emodpy.campaign.individual_intervention import SimpleVaccine as SimpleVaccine
from emodpy.campaign.individual_intervention import StandardDiagnostic as StandardDiagnostic
from emodpy.campaign.individual_intervention import IndividualIntervention
from emodpy.campaign.individual_intervention import IVCalendar as IVCalendar
from emodpy.utils import validate_value_range
from emodpy.campaign.utils import set_event
from emodpy_hiv.utils.emod_enum import (SensitivityType, SettingType, RelationshipType, EventOrConfig, PrioritizePartnersBy,
                                        CondomUsageParametersType)
from emodpy_hiv.utils.distributions import BaseDistribution
from emodpy_hiv.campaign.common import ValueMap, CommonInterventionParameters
from emodpy_hiv.campaign.waning_config import AbstractWaningConfig
from emod_api import campaign as api_campaign

from typing import Union

class Sigmoid:
    """
    Defines a sigmoidal curve that can be used to define probabilities versus time.

    Args:
        min(float, optional):
            The left asymptote for the sigmoid trend over time.  The **min** value must be smaller than the **max** value.
            Minimum value: -1
            Maximum value: 1
            Default value: 0

        max(float, optional):
            The right asymptote for the sigmoid trend over time.  The **max** value must be larger than the **min** value.
            Minimum value: -1
            Maximum value: 1
            Default value: 1

        mid(float, optional):
            The time of the infection point in the sigmoid trend over time.
            Minimum value: 1900
            Maximum value: 2200
            Default value: 2000

        rate(float, optional):
            The slope of the inflection point in the sigmoid trend over time. A Rate of 1 sets the slope to a
            25% change in probability per year. Specify a negative Rate (e.g. -1) to achieve a negative sigmoid.
            Minimum value: -100
            Maximum value: 100
            Default value: 1
    """
    def __init__(self,
                 min: float = 0,
                 max: float = 1,
                 mid: float = 2000,
                 rate: float = 1):
        self.min = validate_value_range(min, 'min', -1, 1, float)
        self.max = validate_value_range(max, 'max', -1, 1, float)
        self.mid = validate_value_range(mid, 'mid', 1900, 2200, float)
        self.rate = validate_value_range(rate, 'rate', -100, 100, float)

        if self.min >= self.max:
            raise ValueError(f"The 'min'(={min}) value must be smaller than the 'max'(={max}) value.")

    def check_value_ranges(self,
                           class_name: str,
                           min_low: float = -1,
                           min_high: float = 1,
                           max_low: float = -1,
                           max_high: float = 1,
                           mid_low: float = 0,
                           mid_high: float = 3.40282e+38,
                           rate_low: float = -100,
                           rate_high: float = 100):
        if self.min < min_low or self.min > min_high:
            raise ValueError(f"For the {class_name} the Sigmoid's 'min'(={self.min}) value must be between {min_low} and {min_high}.")
        if self.max < max_low or self.max > max_high:
            raise ValueError(f"For the {class_name} the Sigmoid's 'max'(={self.max}) value must be between {max_low} and {max_high}.")
        if self.mid < mid_low or self.mid > mid_high:
            raise ValueError(f"For the {class_name} the Sigmoid's 'mid'(={self.mid}) value must be between {mid_low} and {mid_high}.")
        if self.rate < rate_low or self.rate > rate_high:
            raise ValueError(f"For the {class_name} the Sigmoid's 'rate'(={self.rate}) value must be between {rate_low} and {rate_high}.")

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        """
        A function that converts the Sigmoid object to a schema dictionary.
        """
        sigmoid = s2c.get_class_with_defaults("idmType:Sigmoid", campaign.schema_path)
        sigmoid.Min = self.min
        sigmoid.Max = self.max
        sigmoid.Mid = self.mid
        sigmoid.Rate = self.rate
        sigmoid.finalize()
        return sigmoid


class RangeThreshold:
    """
    An element of a look-up table where if a value (age in **AgeDiagnostic** or CD4 in **CD4Diagnostic**)
    is greater-than-or-equal-to the 'Low' value and less-than the 'High' value, the 'Event' will be broadcasted.

    Args:
        low(float, optional):
            The low end of the diagnostic level. For this 'Event' to be selected, the value
            must be greater-than-or-equal-to (>=) this threshold.
            Minimum value: 0
            Maximum value: 2000
            Default value: 0

        high(float, optional):
            The high end of the diagnostic level. For this 'Event' to be selected, the value
            must be less-than this threshold.
            Minimum value: 0
            Maximum value: 2000
            Default value: 2000

        event_to_broadcast(str, required):
            If 'low' <= value < 'high, then this event will be broadcast.
            See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
    """
    def __init__(self,
                 event_to_broadcast: str,
                 low: float = 0,
                 high: float = 2000):
        if event_to_broadcast is None or event_to_broadcast == '':
            raise ValueError(f"{event_to_broadcast} must be a string and cannot be None or empty.")
        self.event_to_broadcast = event_to_broadcast
        self.low  = validate_value_range( low,  'low', 0, 2000, float) # Noqa: E241, E201, E221
        self.high = validate_value_range(high, 'high', 0, 2000, float)

    def to_schema_dict(self, campaign) -> s2c.ReadOnlyDict:
        """
        A function that converts the Sigmoid object to a schema dictionary.
        """
        rt = s2c.get_class_with_defaults("idmType:RangeThreshold", campaign.schema_path)
        rt.Low = self.low
        rt.High = self.high
        rt.Event = set_event(self.event_to_broadcast, 'event_to_broadcast', campaign, True)
        rt.finalize()
        return rt


class ARTDropout(IndividualIntervention):
    """
    The **ARTDropout** intervention class removes an individual from antiretroviral therapy (ART) and
    interrupts their progress through the cascade of care. The individual's infectiousness will
    return to a non-suppressed level, and a new prognosis will be assigned.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ARTDropout', common_intervention_parameters)


class ARTMortalityTable(IndividualIntervention):
    """
    The **ARTMortalityTable** intervention class allows the user to modify an individual's life expectancy
    based on different levels of ART adherence; the user defines parameters for age, CD4 count, and time
    on ART in a multidimensional table which is then used to determine mortality rate. Note: If you
    have different adherence levels for each gender, then you will need to configure your campaign to
    distribute an ARTMortalityTable for each gender and adherence level.

    Additional considerations when using this intervention:
        - The model will not allow someone who is HIV negative to be put on ART.
        - A person who has not previously been on ART is considered to be 'starting ART' at the time
          this intervention is applied; the model will track this start time/duration.
        - If a person is already on ART from another intervention, receiving a second ART intervention
          will have no effect.
        - If a person is on already ART and receives the **ARTMortalityTable** intervention, the original ART
          start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration
          since starting ART will not change; it will continue to increase.
        - If a person is on ART and receives the **ARTDropout** intervention, the person will go off ART and
          the duration will be reset; if receiving a new ART intervention, this new start time/duration
          will be used in any calculations.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        mortality_table(list[list[list[float]]], required):
            Three-dimensional array of mortality rates used to determine the number of days until AIDS death.
            Dimensioned by the values specified in **art_duration_days_bins**, **age_years_bins**, and
            **cd4_count_bins**.

        art_duration_days_bins(list[float], required):
            An array of bins representing the person's duration on ART, in days (greater than or equal to the
            value of the bin, but less than the value of the next bin). Each value represents the outer
            dimension of the **mortality_table**. Must be in ascending order.

        age_years_bins(list[float], required):
            An array of bins representing the age of the person, in years, at the time they received the
            intervention (greater than or equal to the value of the bin, but less than the value of the next
            bin). If they are new to ART, then it is the age that they started ART. If they are changing their
            adherence, then it is the age at that time. This bin is used to select the second dimension of the
            **mortality_table**. Must be in ascending order.

        cd4_count_bins(list[float], required):
            An array of bins representing a person's CD4 count at the time they received the intervention
            (started ART or changed adherence). For each value in the array, there will be one value in the
            associated row in the **mortality_table**.  A mortality rate will be selected from the table as
            follows:
            * Person's CD4 is less than first value in array: Use first mortality rate
            * Person's CD4 is greater than the last value in the array: Use the last mortality rate
            * Person's CD4 is between two values: Use linear interpolation to find the mortality rate
            associated with the person's CD4
            Must be in ascending order.

        days_to_achieve_viral_suppression(float, optional):
            The number of days after ART initiation over which infectiousness declines linearly until the
            **art_multiplier_on_transmission_prob_per_act** takes full effect.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 183

        art_multiplier_on_transmission_prob_per_act(float, optional):
            Multiplier acting on Base_Infectivity to determine the per-act transmission probability of a
            virally suppressed HIV+ individual.
            Minimum value: 0
            Maximum value: 1
            Default value: 0.08

        art_is_active_against_mortality_and_transmission(bool, optional):
            If set to true (1), ART will suppress viral load and extend prognosis.
            Default value: True

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None

    Example:
        Creating an ARTMortalityTable intervention with comprehensive mortality data:
            - 5 ART duration bins (0-6mo, 6-12mo, 12-24mo, 24-36mo, 36+mo)
            - 2 age groups (under 40, 40 and over)
            - 7 CD4 count bins reflecting different immune system states
            - Higher mortality rates for early ART duration and lower CD4 counts
            - Reduced mortality over time as patients stabilize on treatment

            >>> from emodpy_hiv.campaign.individual_intervention import ARTMortalityTable
            >>> from emodpy_hiv.campaign.common import CommonInterventionParameters
            >>> import emodpy_hiv.campaign as api_campaign
            >>>
            >>> art_duration_days_bins=[0, 183, 365, 730, 1095]                    # 0, 6mo, 1yr, 2yr, 3yr in days
            >>> age_years_bins=[0, 40]                                             # Under 40, 40+
            >>> cd4_count_bins=[0, 25, 74.5, 149.5, 274.5, 424.5, 624.5]           # CD4 count thresholds
            >>> # Define mortality table: 5 duration bins x 2 age bins x 7 CD4 bins
            >>> mortality_table = [
            >>>     [  # Duration bin 0 (0-6 months)
            >>>         [0.2015, 0.2015, 0.1128, 0.0625, 0.0312, 0.0206, 0.0162],  # Age 0-40
            >>>         [0.0875, 0.0875, 0.0490, 0.0271, 0.0136, 0.0062, 0.0041]   # Age 40+
            >>>     ],
            >>>     [  # Duration bin 1 (6-12 months)
            >>>         [0.0271, 0.0271, 0.0184, 0.0149, 0.0074, 0.0048, 0.0048],
            >>>         [0.0171, 0.0171, 0.0116, 0.0094, 0.0047, 0.0030, 0.0030]
            >>>     ],
            >>>     [  # Duration bin 2 (12-24 months)
            >>>         [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026],
            >>>         [0.0095, 0.0095, 0.0065, 0.0052, 0.0026, 0.0026, 0.0026]
            >>>     ],
            >>>     [  # Duration bin 3 (24-36 months)
            >>>         [0.0075, 0.0075, 0.0051, 0.0041, 0.0021, 0.0021, 0.0021],
            >>>         [0.0075, 0.0075, 0.0051, 0.0041, 0.0021, 0.0021, 0.0021]
            >>>     ],
            >>>     [  # Duration bin 4 (36+ months)
            >>>         [0.0060, 0.0060, 0.0041, 0.0033, 0.0017, 0.0017, 0.0017],
            >>>         [0.0060, 0.0060, 0.0041, 0.0033, 0.0017, 0.0017, 0.0017]
            >>>     ]
            >>>   ]
            >>>
            >>> # Create the intervention
            >>> art_intervention = ARTMortalityTable(campaign=api_campaign,
            >>>                                      mortality_table=mortality_table,
            >>>                                      art_duration_days_bins=art_duration_days_bins,
            >>>                                      age_years_bins=age_years_bins,
            >>>                                      cd4_count_bins=cd4_count_bins,
            >>>                                      days_to_achieve_viral_suppression=183.0,
            >>>                                      art_multiplier_on_transmission_prob_per_act=0.08,
            >>>                                      art_is_active_against_mortality_and_transmission=True,
            >>>                                      common_intervention_parameters=CommonInterventionParameters(cost=1)
            >>> )
    """

    def __init__(self,
                 campaign: api_campaign,
                 mortality_table: list[list[list[float]]],
                 art_duration_days_bins: list[float],
                 age_years_bins: list[float],
                 cd4_count_bins: list[float],
                 days_to_achieve_viral_suppression: float = 183,
                 art_multiplier_on_transmission_prob_per_act: float = 0.08,
                 art_is_active_against_mortality_and_transmission: bool = True,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'ARTMortalityTable', common_intervention_parameters)

        self._validate_mortality_table_inputs(mortality_table, art_duration_days_bins, age_years_bins, cd4_count_bins)
        
        self._intervention.MortalityTable = mortality_table
        self._intervention.Days_To_Achieve_Viral_Suppression = validate_value_range(days_to_achieve_viral_suppression, 'days_to_achieve_viral_suppression', 0, 3.40282e+38, float)
        self._intervention.CD4_Count_Bins = cd4_count_bins
        self._intervention.Age_Years_Bins = age_years_bins
        self._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act = validate_value_range(art_multiplier_on_transmission_prob_per_act, 'art_multiplier_on_transmission_prob_per_act', 0, 1, float)
        self._intervention.ART_Is_Active_Against_Mortality_And_Transmission = art_is_active_against_mortality_and_transmission
        self._intervention.ART_Duration_Days_Bins = art_duration_days_bins

    def _validate_mortality_table_inputs(self, mortality_table, art_duration_days_bins, age_years_bins, cd4_count_bins):
        """
        Validate that mortality table and associated bins are consistent and properly formatted.
        
        Args:
            mortality_table: 3D list of mortality rates (required)
            art_duration_days_bins: List of ART duration bins (required)
            age_years_bins: List of age bins (required)
            cd4_count_bins: List of CD4 count bins (required)
        """
        self._validate_bin_parameters(art_duration_days_bins, age_years_bins, cd4_count_bins)
        self._validate_mortality_table_structure_and_dimensions(mortality_table, art_duration_days_bins, age_years_bins, cd4_count_bins)

    def _validate_mortality_table_structure_and_dimensions(self, mortality_table, art_duration_days_bins, age_years_bins, cd4_count_bins):
        """
        Validate the 3D structure, values, and dimensions of the mortality table in a single pass.
        
        Args:
            mortality_table: 3D list of mortality rates
            art_duration_days_bins: List of ART duration bins
            age_years_bins: List of age bins
            cd4_count_bins: List of CD4 count bins
        """
        if not isinstance(mortality_table, list):
            raise TypeError("mortality_table must be a list")
        
        # Check first dimension (duration bins)
        if len(mortality_table) != len(art_duration_days_bins):
            raise ValueError(f"mortality_table first dimension ({len(mortality_table)}) must match art_duration_days_bins length ({len(art_duration_days_bins)})")
        
        # Validate each dimension and check dimensional consistency
        expected_age_bins = len(age_years_bins)
        expected_cd4_bins = len(cd4_count_bins)
        
        for i, outer_list in enumerate(mortality_table):
            if not isinstance(outer_list, list):
                raise TypeError(f"mortality_table[{i}] must be a list")
            
            # Check second dimension (age bins)
            if len(outer_list) != expected_age_bins:
                raise ValueError(f"mortality_table[{i}] length ({len(outer_list)}) must match age_years_bins length ({expected_age_bins})")
            
            for j, inner_list in enumerate(outer_list):
                if not isinstance(inner_list, list):
                    raise TypeError(f"mortality_table[{i}][{j}] must be a list")
                
                # Check third dimension (CD4 bins)
                if len(inner_list) != expected_cd4_bins:
                    raise ValueError(f"mortality_table[{i}][{j}] length ({len(inner_list)}) must match cd4_count_bins length ({expected_cd4_bins})")
                
                # Validate all values are numeric and within valid range
                for k, value in enumerate(inner_list):
                    if not isinstance(value, (int, float)):
                        raise TypeError(f"mortality_table[{i}][{j}][{k}] must be a number, got {type(value)}")
                    if value < 0 or value > 1:
                        raise ValueError(f"mortality_table[{i}][{j}][{k}] must between 0 and 1, got {value}")

    def _validate_bin_parameters(self, art_duration_days_bins, age_years_bins, cd4_count_bins):
        """
        Validate the bin parameter arrays.
        
        Args:
            art_duration_days_bins: List of ART duration bins
            age_years_bins: List of age bins
            cd4_count_bins: List of CD4 count bins
        """
        for bin_name, bin_values, max_value in [('art_duration_days_bins', art_duration_days_bins, None),
                                                ('age_years_bins', age_years_bins, 125),
                                                ('cd4_count_bins', cd4_count_bins, 1000)]:
            if not isinstance(bin_values, list):
                raise TypeError(f"{bin_name} must be a list")
            if len(bin_values) == 0:
                raise ValueError(f"{bin_name} cannot be empty")
            
            # Validate all values are numeric and non-negative
            for i, value in enumerate(bin_values):
                if not isinstance(value, (int, float)):
                    raise TypeError(f"{bin_name}[{i}] must be a number, got {type(value)}")
                if value < 0:
                    raise ValueError(f"{bin_name}[{i}] must be non-negative, got {value}")
                if max_value and value > max_value:
                    raise ValueError(f"{bin_name}[{i}] must be less than or equal to {max_value}, got {value}")
            
            # Validate bins are in ascending order
            for i in range(1, len(bin_values)):
                if bin_values[i] <= bin_values[i-1]:
                    raise ValueError(f"{bin_name} must be in ascending order: {bin_values[i-1]} >= {bin_values[i]} at positions {i-1}, {i}")



class AgeDiagnostic(IndividualIntervention):
    """
    The **AgeDiagnostic** allows you to broadcast different events based on the individual's age.  For example,
    you could distribute this intervention to people who are high risk and use the intervention to have
    different things happen (because of the broadcasted events) based on their age.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        age_thresholds(list[RangeThreshold], optional):
            Used to associate age ranges for individuals.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 age_thresholds: list[RangeThreshold] = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AgeDiagnostic', common_intervention_parameters)

        for at in age_thresholds:
            self._intervention.Age_Thresholds.append(at.to_schema_dict(campaign))


class AntiretroviralTherapy(IndividualIntervention):
    """
    The **AntiretroviralTherapy** intervention class begins antiretroviral therapy (ART) for specified individuals.
    To remove an individual from ART, use **ARTDropout**. Please refer to the documentation for
    **AntiretroviralTherapy** at the following link:
    :doc:`emod-hiv:emod/hiv-model-healthcare-systems`.

    Additional considerations when using this intervention:
        - The model will not allow someone who is HIV negative to be put on ART.
        - A person who has not previously been on ART is considered to be 'starting ART' at the time this
          intervention is applied; the model will track this start time/duration.
        - If a person is already on ART from another intervention, receiving a second ART intervention will
          have no effect.
        - If a person is on already ART and receives the ARTMortalityTable intervention, the original ART
          start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration
          since starting ART will not change; it will continue to increase.
        - If a person is on ART and receives the **ARTDropout** intervention, the person will go off ART and
          the duration will be reset; if receiving a new ART intervention, this new start time/duration will
          be used in any calculations.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        days_to_achieve_viral_suppression(float, optional):
            The number of days after ART initiation over which infectiousness declines linearly until the
            **art_multiplier_on_transmission_prob_per_act** takes full effect.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 183

        art_survival_who_stage_threshold_for_cox(float, optional):
            If the person receiving ART has a WHO Stage greater than or equal to this threshold, then use the
            hazard ratio determined by the parameter **art_survival_hazard_ratio_who_stage_3plus**.
            Minimum value: 0
            Maximum value: 5
            Default value: 3

        art_survival_hazard_ratio_who_stage_3plus(float, optional):
            The hazard ratio comparing those starting ART in WHO stage >= 3 to those in WHO stage < 3.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 2.7142

        art_survival_hazard_ratio_female(float, optional):
            The hazard ratio comparing survival female to male survival for those starting ART.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 0.6775

        art_survival_hazard_ratio_cd4_slope(float, optional):
            The slope value to sue when calculating the hazard for for the person based on their CD4 count.
            multiplier = exp(cd4_slope * cd4 + cd4_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: -0.00758256

        art_survival_hazard_ratio_cd4_intercept(float, optional):
            The Y-intercept to use when calculating the hazard ratio for the person based on their CD4 count.
            multiplier = exp(cd4_slope * cd4 + cd4_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: 0.282852

        art_survival_hazard_ratio_body_weight_kg_slope(float, optional):
            The slope to use when calculating the hazard ratio for the person's body weight.
            The body weight is determined by WHO stage:
            * WHO Stage 0 = 65.0 kg
            * WHO Stage 1-2 = 62.1 kg
            * WHO Stage 2-3 = 57.0 kg
            * WHO Stage 3-4 = 50.0 kg
            * WHO Stage 4+ = 40.1 kg
            multiplier = exp(weight_slope * weight + weight_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: -0.073153

        art_survival_hazard_ratio_body_weight_kg_intercept(float, optional):
            The Y-intercept to use when calculating the hazard ratio for the person's body weight.

            The body weight is determined by WHO stage:

            * WHO Stage 0 = 65.0 kg
            * WHO Stage 1-2 = 62.1 kg
            * WHO Stage 2-3 = 57.0 kg
            * WHO Stage 3-4 = 50.0 kg
            * WHO Stage 4+ = 40.1 kg

            multiplier = exp(weight_slope * weight + weight_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: 3.05043

        art_survival_hazard_ratio_age_over_40yr(float, optional):
            The hazard ratio comparing the survival time of those starting ART over 40 years of age compared to
            those starting ART <40 years.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 1.4309

        art_survival_baseline_hazard_weibull_shape(float, optional):
            Shape parameter for a Weibull distribution of survival time in years for a male < 40 with WHO stage
            of 1 or 2 starting ART (base case).
            Minimum value: 0
            Maximum value: 10
            Default value: 0.34

        art_survival_baseline_hazard_weibull_scale(float, optional):
            Scale parameter for a Weibull distribution of survival time in years for a male < 40 with WHO stage
            of 1 or 2 starting ART (base case).
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 123.83

        art_multiplier_on_transmission_prob_per_act(float, optional):
            Multiplier acting on Base_Infectivity to determine the per-act transmission probability of a
            virally suppressed HIV+ individual.
            Minimum value: 0
            Maximum value: 1
            Default value: 0.08

        art_is_active_against_mortality_and_transmission(bool, optional):
            If set to true (1), ART will suppress viral load and extend prognosis.
            Default value: True

        art_cd4_at_initiation_saturating_reduction_in_mortality(float, optional):
            The duration from ART enrollment to on-ART HIV-cause death increases with CD4 at ART initiation up
            to a threshold determined by this parameter value. This is the maximum value that CD4 is allowed to
            have in the hazard ratio calculation for CD4.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 350

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 days_to_achieve_viral_suppression: float = 183,
                 art_survival_who_stage_threshold_for_cox: float = 3,
                 art_survival_hazard_ratio_who_stage_3plus: float = 2.7142,
                 art_survival_hazard_ratio_female: float = 0.6775,
                 art_survival_hazard_ratio_cd4_slope: float = -0.00758256,
                 art_survival_hazard_ratio_cd4_intercept: float = 0.282852,
                 art_survival_hazard_ratio_body_weight_kg_slope: float = -0.073153,
                 art_survival_hazard_ratio_body_weight_kg_intercept: float = 3.05043,
                 art_survival_hazard_ratio_age_over_40yr: float = 1.4309,
                 art_survival_baseline_hazard_weibull_shape: float = 0.34,
                 art_survival_baseline_hazard_weibull_scale: float = 123.83,
                 art_multiplier_on_transmission_prob_per_act: float = 0.08,
                 art_is_active_against_mortality_and_transmission: bool = True,
                 art_cd4_at_initiation_saturating_reduction_in_mortality: float = 350,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AntiretroviralTherapy', common_intervention_parameters)

        self._intervention.Days_To_Achieve_Viral_Suppression = validate_value_range(days_to_achieve_viral_suppression, 'days_to_achieve_viral_suppression', 0, 3.40282e+38, float)
        self._intervention.ART_Survival_WHO_Stage_Threshold_For_Cox = validate_value_range(art_survival_who_stage_threshold_for_cox, 'art_survival_who_stage_threshold_for_cox', 0, 5, float)
        self._intervention.ART_Survival_Hazard_Ratio_WHO_Stage_3Plus = validate_value_range(art_survival_hazard_ratio_who_stage_3plus, 'art_survival_hazard_ratio_who_stage_3plus', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Female = validate_value_range(art_survival_hazard_ratio_female, 'art_survival_hazard_ratio_female', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_CD4_Slope = validate_value_range(art_survival_hazard_ratio_cd4_slope, 'art_survival_hazard_ratio_cd4_slope', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_CD4_Intercept = validate_value_range(art_survival_hazard_ratio_cd4_intercept, 'art_survival_hazard_ratio_cd4_intercept', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Slope = validate_value_range(art_survival_hazard_ratio_body_weight_kg_slope, 'art_survival_hazard_ratio_body_weight_kg_slope', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Intercept = validate_value_range(art_survival_hazard_ratio_body_weight_kg_intercept, 'art_survival_hazard_ratio_body_weight_kg_intercept', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Age_Over_40Yr = validate_value_range(art_survival_hazard_ratio_age_over_40yr, 'art_survival_hazard_ratio_age_over_40yr', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Baseline_Hazard_Weibull_Shape = validate_value_range(art_survival_baseline_hazard_weibull_shape, 'art_survival_baseline_hazard_weibull_shape', 0, 10, float)
        self._intervention.ART_Survival_Baseline_Hazard_Weibull_Scale = validate_value_range(art_survival_baseline_hazard_weibull_scale, 'art_survival_baseline_hazard_weibull_scale', 1e-06, 1000000.0, float)
        self._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act = validate_value_range(art_multiplier_on_transmission_prob_per_act, 'art_multiplier_on_transmission_prob_per_act', 0, 1, float)
        self._intervention.ART_Is_Active_Against_Mortality_And_Transmission = 1 if art_is_active_against_mortality_and_transmission else 0
        self._intervention.ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality = validate_value_range(art_cd4_at_initiation_saturating_reduction_in_mortality, 'art_cd4_at_initiation_saturating_reduction_in_mortality', 0, 3.40282e+38, float)


class AntiretroviralTherapyFull(IndividualIntervention):
    """
    The **AntriretroviralTherapyFull** intervention class begins antiretroviral therapy (ART) on the person
    receiving the intervention. This class is similar to the standard AntiretroviralTherapy, but enhances
    it with two key features: 1) a built-in delay timer such that when the delay expires, the person will
    come off of ART (**ARTDropout** should NOT be used with this intervention), and 2) persistence with the
    individual so the user can track this intervention using ReferenceTrackingEventCoordinator.

    Additional considerations when using this intervention:
        - The model will not allow someone who is HIV negative to be put on ART.
        - A person who has not previously been on ART is considered to be 'starting ART' at the time this
          intervention is applied; the model will track this start time/duration.
        - If a person is already on ART from another intervention, receiving a second ART intervention will
          have no effect.
        - If a person is on already ART and receives the ARTMortalityTable intervention, the original ART
          start time will be used to calculate the duration from enrollment to ART AIDS Death. The duration
          since starting ART will not change; it will continue to increase.
        - If a person is on ART and receives the **ARTDropout** intervention, the person will go off ART and
          the duration will be reset; if receiving a new ART intervention, this new start time/duration will
          be used in any calculations.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        time_on_art_distribution(BaseDistribution, required):
            The type of distribution to use when determine how long a person will be on ART.
            Please use the following distribution classes from emodpy_hiv.utils.distributions
            to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        stop_art_event(str, optional):
            This event is broadcast when the person drops off ART. This could happen either via the timer
            running out or the intervention detected a disqualifying property.  See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        days_to_achieve_viral_suppression(float, optional):
            The number of days after ART initiation over which infectiousness declines linearly until the
            **ART_Multiplier_On_Transmission_Prob_Per_Act** takes full effect.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 183

        art_survival_who_stage_threshold_for_cox(float, optional):
            If the person receiving ART has a WHO Stage greater than or equal to this threshold, then use the
            hazard ratio determined by the parameter **ART_Survival_Hazard_Ratio_WHO_Stage_3Plus**.
            Minimum value: 0
            Maximum value: 5
            Default value: 3

        art_survival_hazard_ratio_who_stage_3plus(float, optional):
            The hazard ratio comparing those starting ART in WHO stage >= 3 to those in WHO stage < 3.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 2.7142

        art_survival_hazard_ratio_female(float, optional):
            The hazard ratio comparing survival female to male survival for those starting ART.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 0.6775

        art_survival_hazard_ratio_cd4_slope(float, optional):
            The slope value to sue when calculating the hazard for for the person based on their CD4 count.
            multiplier = exp(cd4_slope * cd4 + cd4_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: -0.00758256

        art_survival_hazard_ratio_cd4_intercept(float, optional):
            The Y-intercept to use when calculating the hazard ratio for the person based on their CD4 count.
            multiplier = exp(cd4_slope * cd4 + cd4_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: 0.282852

        art_survival_hazard_ratio_body_weight_kg_slope(float, optional):
            The slope to use when calculating the hazard ratio for the person's body weight.
            The body weight is determined by WHO stage:
            * WHO Stage 0 = 65.0 kg
            * WHO Stage 1-2 = 62.1 kg
            * WHO Stage 2-3 = 57.0 kg
            * WHO Stage 3-4 = 50.0 kg
            * WHO Stage 4+ = 40.1 kg
            multiplier = exp(weight_slope * weight + weight_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: -0.073153

        art_survival_hazard_ratio_body_weight_kg_intercept(float, optional):
            The Y-intercept to use when calculating the hazard ratio for the person's body weight.

            The body weight is determined by WHO stage:

            * WHO Stage 0 = 65.0 kg
            * WHO Stage 1-2 = 62.1 kg
            * WHO Stage 2-3 = 57.0 kg
            * WHO Stage 3-4 = 50.0 kg
            * WHO Stage 4+ = 40.1 kg

            multiplier = exp(weight_slope * weight + weight_intercept)
            Minimum value: -1000000.0
            Maximum value: 1000000.0
            Default value: 3.05043

        art_survival_hazard_ratio_age_over_40yr(float, optional):
            The hazard ratio comparing the survival time of those starting ART over 40 years of age compared to
            those starting ART <40 years.
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 1.4309

        art_survival_baseline_hazard_weibull_shape(float, optional):
            Shape parameter for a Weibull distribution of survival time in years for a male < 40 with WHO stage
            of 1 or 2 starting ART (base case).
            Minimum value: 0
            Maximum value: 10
            Default value: 0.34

        art_survival_baseline_hazard_weibull_scale(float, optional):
            Scale parameter for a Weibull distribution of survival time in years for a male < 40 with WHO stage
            of 1 or 2 starting ART (base case).
            Minimum value: 1e-06
            Maximum value: 1000000.0
            Default value: 123.83

        art_multiplier_on_transmission_prob_per_act(float, optional):
            Multiplier acting on Base_Infectivity to determine the per-act transmission probability of a
            virally suppressed HIV+ individual.
            Minimum value: 0
            Maximum value: 1
            Default value: 0.08

        art_is_active_against_mortality_and_transmission(bool, optional):
            If set to true (1), ART will suppress viral load and extend prognosis.
            Default value: True

        art_cd4_at_initiation_saturating_reduction_in_mortality(float, optional):
            The duration from ART enrollment to on-ART HIV-cause death increases with CD4 at ART initiation up
            to a threshold determined by this parameter value. This is the maximum value that CD4 is allowed to
            have in the hazard ratio calculation for CD4.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 350

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 time_on_art_distribution: BaseDistribution,
                 stop_art_event: str = None,
                 days_to_achieve_viral_suppression: float = 183,
                 art_survival_who_stage_threshold_for_cox: float = 3,
                 art_survival_hazard_ratio_who_stage_3plus: float = 2.7142,
                 art_survival_hazard_ratio_female: float = 0.6775,
                 art_survival_hazard_ratio_cd4_slope: float = -0.00758256,
                 art_survival_hazard_ratio_cd4_intercept: float = 0.282852,
                 art_survival_hazard_ratio_body_weight_kg_slope: float = -0.073153,
                 art_survival_hazard_ratio_body_weight_kg_intercept: float = 3.05043,
                 art_survival_hazard_ratio_age_over_40yr: float = 1.4309,
                 art_survival_baseline_hazard_weibull_shape: float = 0.34,
                 art_survival_baseline_hazard_weibull_scale: float = 123.83,
                 art_multiplier_on_transmission_prob_per_act: float = 0.08,
                 art_is_active_against_mortality_and_transmission: bool = True,
                 art_cd4_at_initiation_saturating_reduction_in_mortality: float = 350,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'AntiretroviralTherapyFull', common_intervention_parameters)

        if not isinstance(time_on_art_distribution, BaseDistribution):
            raise ValueError(f"time_on_art_distribution must be an instance of BaseDistribution, not {type(time_on_art_distribution)}.")
        self.set_distribution(time_on_art_distribution, 'Time_On_ART')

        self._intervention.Stop_ART_Event = set_event(stop_art_event, 'stop_art_event', campaign, True)
        self._intervention.Days_To_Achieve_Viral_Suppression = validate_value_range(days_to_achieve_viral_suppression, 'days_to_achieve_viral_suppression', 0, 3.40282e+38, float)
        self._intervention.ART_Survival_WHO_Stage_Threshold_For_Cox = validate_value_range(art_survival_who_stage_threshold_for_cox, 'art_survival_who_stage_threshold_for_cox', 0, 5, float)
        self._intervention.ART_Survival_Hazard_Ratio_WHO_Stage_3Plus = validate_value_range(art_survival_hazard_ratio_who_stage_3plus, 'art_survival_hazard_ratio_who_stage_3plus', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Female = validate_value_range(art_survival_hazard_ratio_female, 'art_survival_hazard_ratio_female', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_CD4_Slope = validate_value_range(art_survival_hazard_ratio_cd4_slope, 'art_survival_hazard_ratio_cd4_slope', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_CD4_Intercept = validate_value_range(art_survival_hazard_ratio_cd4_intercept, 'art_survival_hazard_ratio_cd4_intercept', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Slope = validate_value_range(art_survival_hazard_ratio_body_weight_kg_slope, 'art_survival_hazard_ratio_body_weight_kg_slope', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Body_Weight_Kg_Intercept = validate_value_range(art_survival_hazard_ratio_body_weight_kg_intercept, 'art_survival_hazard_ratio_body_weight_kg_intercept', -1000000.0, 1000000.0, float)
        self._intervention.ART_Survival_Hazard_Ratio_Age_Over_40Yr = validate_value_range(art_survival_hazard_ratio_age_over_40yr, 'art_survival_hazard_ratio_age_over_40yr', 1e-06, 1000000.0, float)
        self._intervention.ART_Survival_Baseline_Hazard_Weibull_Shape = validate_value_range(art_survival_baseline_hazard_weibull_shape, 'art_survival_baseline_hazard_weibull_shape', 0, 10, float)
        self._intervention.ART_Survival_Baseline_Hazard_Weibull_Scale = validate_value_range(art_survival_baseline_hazard_weibull_scale, 'art_survival_baseline_hazard_weibull_scale', 1e-06, 1000000.0, float)
        self._intervention.ART_Multiplier_On_Transmission_Prob_Per_Act = validate_value_range(art_multiplier_on_transmission_prob_per_act, 'art_multiplier_on_transmission_prob_per_act', 0, 1, float)
        self._intervention.ART_Is_Active_Against_Mortality_And_Transmission = 1 if art_is_active_against_mortality_and_transmission else 0
        self._intervention.ART_CD4_at_Initiation_Saturating_Reduction_in_Mortality = validate_value_range(art_cd4_at_initiation_saturating_reduction_in_mortality, 'art_cd4_at_initiation_saturating_reduction_in_mortality', 0, 3.40282e+38, float)


class CD4Diagnostic(IndividualIntervention):
    """
    The **CD4Diagnostic** allows you to have different things happen to a person based on their actual CD4 count.
    For example, if a person was given an HIVRapidDiagnostic and tested positive, you could give that person
    the **CD4Diagnositic**.  The diagnostic would broadcast different events based on their current CD4 count.
    If the CD4 count was high, you could broadcast an event that would give the person a delay that would have
    the person re-test in three months.  If the CD4 count was low, you could broadcast an event that would cause
    them to go on ART immediately.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        cd4_thresholds(list[RangeThreshold], optional):
            This parameter associates ranges of CD4 counts with events that should occur for individuals whose
            CD4 counts fall into those ranges.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 cd4_thresholds: list[RangeThreshold] = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'CD4Diagnostic', common_intervention_parameters)

        for ct in cd4_thresholds:
            self._intervention.CD4_Thresholds.append(ct.to_schema_dict(campaign))


class CoitalActRiskFactors(IndividualIntervention):
    """
    The **CoitalActRiskFactors** intervention class provides a method of modifying an individual's
    risk/probability of acquiring or transmitting an STI. If other risk multipliers are active
    (across other interventions), the values will be multiplied together; the resulting value
    will be multiplied with any active STI co-infection factors. When the intervention expires,
    the individual's risk factor multiplier returns to one. Since this intervention persists,
    it can be used with Distributors.add_intervention_tracker(). NOTE: An individual can have
    multiple of these interventions with each one being multiplied times the other.

    The risk multiplier for a coital act has three contributions:

        1. *Coital Act Risk Factors* - The factors from the use of this intervention.

        2. *Co-Infection* - A person can get a co-infection by using the **ModifyStiCoInfectionStatus**
           intervention.  If the person has a co-infection, then the configuration paameters **STI_Coinfection_Transmission_Multiplier**
           or **STI_Coinfection_Acquisition_Multiplier** depending on whether the person has HIV (transmitter)
           or not (aquirer).  The maximum value of the multiplier between the transmitter and acquirer is used.

        3. *Condom Transmission Blocking* - If condoms were used in this coital act, then the
           configuration parameter **Condom_Transmission_Blocking_Probability** is included.

    The value of the multiplier is calculated as follows:

        >>> co_inf_transmission = infected_individual.STI_Coinfection_Transmission_Multiplier if co-infected else 1
        >>> co_inf_acquisition  = uninfected_individual.STI_Coinfection_Acquisition_Multiplier if co-infected else 1
        >>> risk_multiplier = max( co_inf_transmission, co_inf_acquisition )
        >>>
        >>> risk_factor_transmission = infected_individual.CoitalActsRiskFactors.Transmission_Multiplier
        >>> risk_factor_acquisition = uninfected_individual.CoitalActsRiskFactors.Acquisition_Multiplier
        >>> risk_multiplier *= risk_factor_transmission * risk_factor_acquisition;
        >>>
        >>> risk_multiplier *= (1 - Condom_Transmission_Blocking_Probability) if using_condom else 1

    This risk multiplier is then used to determine if the uninfected person becomes infected:

        >>> probability_infected = risk_multiplier
        >>>                      * transmission_probability
        >>>                      * acquisition_probability

    **Acquisition Probability**

    There are three things that contribute to the probability that an uninfected person can acquire HIV
    from a coital act with an infected person.  They are:

        1. *Male Circumcision* - If the uninfected person is male and has been circumcised, their probability
           of acquisition is reduced.  The male individual will have the **MaleCircumcision** intervention and its
           **Circumcision_Reduced_Acquire** parameter will be used.

        2. *Female Susceptibility By Age* - If the uninfected person is female, then their current age is used
           to determine the a factor from the configuration parameters **Male_To_Female_Relative_Infectivity_Ages**
           and **Male_To_Female_Relative_Infectivity_Multipliers**.  Their age is used with linear interpolation
           to calculate a multiplier.

        3. *PrEP / Vaccine* - If the uninfected person has a vaccine or PrEP, their probability of acquisition
           is also reduced.

        >>> probability_acquire = 1.0
        >>> probability_acquire *= MaleCircumcision.Circumcision_Reduced_Acquire if male and circumcised else 1
        >>> probability_acquire *= get_female_susceptibility( person.age ) if female else 1
        >>> probability_acquire *= vaccine_reduced_acquire if person has vaccine else 1

    **Transmission Probability**

    In EMOD, the probability of a person transmitting HIV comes down to whether nor not the person has been
    vaccinated and how infectious they are.

        1. *Vaccine* - If the infected person has a vaccine that reduces transmission, its probability of
           transmission reduction is used.

        2. *Infectiousness* - The infectiousness of a person depends on the following four factors:

            2a. *Base Infectivity* - The configuration parameter **Base_Infectivity** determines the starting
            amount of infectiousness. It is the starting point of the calculation and is assumed to be
            female-to-male transmission.

            2b. *Heterogeneity* - To represent the heterogeneity in people, the **Base_Infectivity** is
            multiplied by a value from a Log Normal distribution based on the configuration parameter
            **Heterogeneous_Infectiousness_LogNormal_Scale**.

                >>> median = -0.5 * Heterogeneous_Infectiousness_LogNormal_Scale**2
                >>> heterogeneity_factor = median + eGauss() * Heterogeneous_Infectiousness_LogNormal_Scale

            where eGauss() is a gaussian distributed random number between 0 and 1.

            2c. *Stage of Infection* - The mount the infection has progressed also impacts the amount of
            infectiousness.  If the person is in the 'acute' stage, then we multiply the **Base_Infectivity**
            times the configuration parameter **Acute_Stage_Infectivity_Multiplier**.  If the person is in
            the 'AIDS' stage, we multiply by the configuration parameter **AIDS_Stage_Infectivity_Multiplier**.
            If they are in the 'latent' stage, we do not adjust the **Base_Infectivity**.

            2d. *ART Suppression* - If a person has been given an ART intervention (**AntiretroviralTherapy**,
            **AntiretroviralTherapyFull**, or **ARTMortalityTable**) and has not dropped off of art (**ARTDropout**),
            then ART can suppress the person's infectiousness.  This amount of suppression is determined by
            the intervention parameters **ART_Multiplier_On_Transmission_Prob_Per_Act** and
            **Days_To_Achieve_Viral_Suppression**.  If the person has been on ART less than
            **Days_To_Achieve_Viral_Suppression**, the **ART_Multiplier_On_Transmission_Prob_Per_Act**
            will be reduced proportionally.

        These different factors are combined as follows:

            >>> infectiousness = Base_Infectivity
            >>> infectiousness *= heterogeneity_factor
            >>>
            >>> if hiv_stage == ACUTE:
            >>>     infectiousness *= Acute_Stage_Infectivity_Multiplier
            >>> elif hiv_stage == AIDS:
            >>>     infectiousness *= AIDS_Stage_Infectivity_Multiplier
            >>>
            >>> suppression = ART_Multiplier_On_Transmission_Prob_Per_Act
            >>> if Days_To_Achieve_Viral_Suppression > 0:
            >>>     art_mult = ART_Multiplier_On_Transmission_Prob_Per_Act
            >>>     days_to_achieve = Days_To_Achieve_Viral_Suppression
            >>>     suppression = 1 - ((1 - art_mult) / days_to_achieve) * time_since_starting_ART
            >>> infectiousness *= suppression

    The transmission probability is then calculated as:

        >>> probability_transmission = infectiousness * vaccine_reduced_transmission

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        transmission_multiplier(float, optional):
            Multiplier for STI transmission probability per coital act.
            Minimum value: 0
            Maximum value: 100
            Default value: 1

        expiration_period_distribution(BaseDistribution, required):
            The distribution type to use for setting the expiration of the intervention. Each intervention gets
            an expiration duration by doing a random draw from the distribution.  Please use the following
            distribution classes from emodpy_hiv.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        expiration_event_trigger(str, optional):
            When the intervention expires, this individual-level event will be broadcast. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        acquisition_multiplier(float, optional):
            Multiplier for STI acquisition probability per coital act.
            Minimum value: 0
            Maximum value: 100
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 expiration_period_distribution: BaseDistribution,
                 transmission_multiplier: float = 1,
                 expiration_event_trigger: str = None,
                 acquisition_multiplier: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'CoitalActRiskFactors', common_intervention_parameters)

        self._intervention.Transmission_Multiplier = validate_value_range(transmission_multiplier, 'transmission_multiplier', 0, 100, float)
        self._intervention.Expiration_Event_Trigger = set_event(expiration_event_trigger, 'expiration_event_trigger', campaign, True)
        self._intervention.Acquisition_Multiplier = validate_value_range(acquisition_multiplier, 'acquisition_multiplier', 0, 100, float)

        if not isinstance(expiration_period_distribution, BaseDistribution):
            raise ValueError(f"expiration_period_distribution must be an instance of BaseDistribution, not {type(expiration_period_distribution)}.")
        self.set_distribution(expiration_period_distribution, 'Expiration_Period')


class FemaleContraceptive(IndividualIntervention):
    """
    The **FemaleContraceptive** intervention is used to reduce the fertility rate of females of reproductive age
    (14 to 45 years old), based on a distribution set by the user. This intervention can only be distributed to
    females, and ignores the waning condition expiration (as women could still use a contraceptive, even if it
    is ineffective). Note: the Birth_Rate_Dependence configuration parameter must be set to
    INDIVIDUAL_PREGNANCIES or INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR or an error will result.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        waning_config(AbstractWaningConfig, required):
            A WaningConfig object used to control the efficacy of the contraceptive, typically over time.
            Specify how this effect decays over time using one of the Waning Config classes in
            emodpy_hiv.campaign.waning_config.

        usage_expiration_event(str, optional):
            When the woman stops using the contraceptive, this event will be broadcast. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        usage_duration_distribution(BaseDistribution, required):
            For the distribution of each contraceptive, a randomly selected duration from this distribution
            will determine when the woman stops using the contraceptive.  This is independent of how long the
            contraceptive is effective. Please use the following distribution classes
            from emodpy_hiv.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 waning_config: AbstractWaningConfig,
                 usage_expiration_event: str,
                 usage_duration_distribution: BaseDistribution,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'FemaleContraceptive', common_intervention_parameters)
        if not isinstance(waning_config, AbstractWaningConfig):
            raise ValueError(f"waning_config must be an instance of AbstractWaningConfig, not {type(waning_config)}.")
        self._intervention.Waning_Config = waning_config.to_schema_dict(campaign)
        self._intervention.Usage_Expiration_Event = set_event(usage_expiration_event, 'usage_expiration_event', campaign, True)
        if not isinstance(usage_duration_distribution, BaseDistribution):
            raise ValueError(f"usage_duration_distribution must be an instance of BaseDistribution, not {type(usage_duration_distribution)}.")
        self.set_distribution(usage_duration_distribution, 'Usage_Duration')


class HIVARTStagingByCD4Diagnostic(IndividualIntervention):
    """
    The **HIVARTStagingByCD4Diagnostic** intervention class checks for treatment eligibility based on CD4 count.
    It uses the lowest-ever recorded CD4 count for that individual, based on the history of past CD4 counts
    conducted using the **HIVDrawBlood** intervention. To specify the outcome based on age bins instead of CD4
    testing, use **HIVARTStagingCD4AgnosticDiagnostic**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        cd4_threshold(ValueMap, required):
            It is a piecewise table of years to CD4 and the individual's CD4 count must be below this threshold in order
            to get a positive 'diagnosis'.

        if_pregnant(ValueMap, required):
            If the individual does not pass the diagnostic from the **cd4_threshold** or if_active_TB, and the
            individual is pregnant, then the individual's CD4 is compared to the value found in the
            **ValueMap matrix**.

        if_active_tb(ValueMap, required):
            If the individual's CD4 is not below the threshold in the **cd4_threshold** table and the individual
            has TB, then the individual's CD4 will be compared to the CD4 value retrieved from the **ValueMap** matrix
            based on the current year. Whether a person has TB is determined by the value of an Individual Property as
            determined by the parameters individual_property_active_tb_key(typically 'HasActiveTB') and
            individual_property_active_tb_value(typically 'Yes').

        positive_diagnosis_event(str, required):
            If the test is positive, this specifies an event that will be broadcast. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.

        negative_diagnosis_event(str, optional):
            If the test is negative, this specifies an event that will be broadcast.
            See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        individual_property_active_tb_value(str, optional):
            The **IndividualProperty** value ('Yes') used to determine whether the individual has TB. If you want to
            use this feature, you will need to define the property in the demographics
            Default value: None

        individual_property_active_tb_key(str, optional):
            The **IndividualProperty** key ('HasActiveTB') used to determine whether the individual has TB. If you want
            to use this feature, you will need to define the property in the demographics
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 cd4_threshold: ValueMap,
                 if_pregnant: ValueMap,
                 if_active_tb: ValueMap,
                 positive_diagnosis_event: str,
                 negative_diagnosis_event: str = None,
                 individual_property_active_tb_value: str = None,
                 individual_property_active_tb_key: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVARTStagingByCD4Diagnostic', common_intervention_parameters)

        self._intervention.Threshold = cd4_threshold.to_schema_dict(campaign)
        self._intervention.If_Pregnant = if_pregnant.to_schema_dict(campaign)
        self._intervention.If_Active_TB = if_active_tb.to_schema_dict(campaign)
        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)

        # individual_property_active_tb_value and individual_property_active_tb_key are optional, but if one is set, both must be set
        if individual_property_active_tb_value is not None and individual_property_active_tb_key is not None:
            self._intervention.Individual_Property_Active_TB_Value = individual_property_active_tb_value
            self._intervention.Individual_Property_Active_TB_Key = individual_property_active_tb_key
        elif individual_property_active_tb_value is not None or individual_property_active_tb_key is not None:
            raise ValueError("If individual_property_active_tb_value is set, individual_property_active_tb_key must also be set, and vice versa.")


class HIVARTStagingCD4AgnosticDiagnostic(IndividualIntervention):
    """
    The **HIVARTStagingCD4AgnosticDiagnostic** intervention class checks for treatment eligibility based on age.
    It uses the individual's age and the **adult_treatment_age** argument to determine if the person should be
    usin the adult or child requirements. To specify the outcome based on CD4 testing,
    use **HIVARTStagingByCD4Diagnostic**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        child_treat_under_age_in_years_threshold(ValueMap, required):
            Determines the age at which children are eligible for ART regardless of CD4, WHO stage, or other
            factors. This parameter uses **ValueMap** to define **Times** (by year) and **Values**
            for the history and expected treatment guidelines for future years.

        child_by_who_stage(ValueMap, required):
            Determines the WHO stage at or above which children are eligible for ART. This parameter uses
            **ValueMap** to define **Times** (by year) and **Values** for the history and expected
            treatment guidelines for future years.

        child_by_tb(ValueMap, required):
            Determines the WHO stage at or above which children having active TB are eligible for ART.
            This parameter uses **ValueMap** to define **Times** (by year) and **Values** for the history and expected
            treatment guidelines for future years. Whether a child has TB is determined by the value of an Individual Property as
            determined by the parameters individual_property_active_tb_key(typically 'HasActiveTB') and
            individual_property_active_tb_value(typically 'Yes').

        adult_by_who_stage(ValueMap, required):
            Determines the WHO stage at or above which adults are eligible for ART. This parameter uses
            ValueMap to define **Times** (by year) and **Values** for the history and expected
            treatment guidelines for future years.

        adult_by_tb(ValueMap, required):
            Determines the WHO stage at or above which adults having active TB are eligible for ART.
            This parameter uses ValueMap to define **Times**
            (by year) and **Values** for the history and expected treatment guidelines for future years. Whether an
            adult has TB is determined by the value of an Individual Property as
            determined by the parameters individual_property_active_tb_key(typically 'HasActiveTB') and
            individual_property_active_tb_value(typically 'Yes').

        adult_by_pregnant(ValueMap, required):
            Determines the WHO stage at or above which pregnant adults are eligible for ART. This parameter
            uses ValueMap to define **Times** (by year) and **Values** for the history and expected
            treatment guidelines for future years.

        positive_diagnosis_event(str, required):
            If an individual tests positive, this specifies an event that may trigger another intervention when
            the event occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in
            EMOD or use your own custom event.

        negative_diagnosis_event(str, optional):
            If an individual tests negative, this specifies an event that will be broadcast and may trigger another
            intervention. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        individual_property_active_tb_value(str, optional):
            The **IndividualProperty** value ('Yes') used to determine whether the individual has TB.
            Default value: None

        individual_property_active_tb_key(str, optional):
            The **IndividualProperty** key ('HasActiveTB') used to determine whether the individual has TB.
            Default value: None

        adult_treatment_age(float, optional):
            The age (in years) that delineates adult patients from pediatric patients for the purpose of
            treatment eligibility. Patients younger than this age may be eligible on the basis of their
            pediatric patient status.
            Minimum value: -1
            Maximum value: 3.40282e+38
            Default value: 5

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 child_treat_under_age_in_years_threshold: ValueMap,
                 child_by_who_stage: ValueMap,
                 child_by_tb: ValueMap,
                 adult_by_who_stage: ValueMap,
                 adult_by_tb: ValueMap,
                 adult_by_pregnant: ValueMap,
                 positive_diagnosis_event: str,
                 negative_diagnosis_event: str = None,
                 individual_property_active_tb_value: str = None,
                 individual_property_active_tb_key: str = None,
                 adult_treatment_age: float = 5,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVARTStagingCD4AgnosticDiagnostic', common_intervention_parameters)

        self._intervention.Child_Treat_Under_Age_In_Years_Threshold = child_treat_under_age_in_years_threshold.to_schema_dict(campaign)
        self._intervention.Child_By_WHO_Stage = child_by_who_stage.to_schema_dict(campaign)
        self._intervention.Child_By_TB = child_by_tb.to_schema_dict(campaign)
        self._intervention.Adult_By_WHO_Stage = adult_by_who_stage.to_schema_dict(campaign)
        self._intervention.Adult_By_TB = adult_by_tb.to_schema_dict(campaign)
        self._intervention.Adult_By_Pregnant = adult_by_pregnant.to_schema_dict(campaign)
        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)

        # individual_property_active_tb_value and individual_property_active_tb_key are optional, but if one is set, both must be set
        if individual_property_active_tb_value is not None and individual_property_active_tb_key is not None:
            self._intervention.Individual_Property_Active_TB_Value = individual_property_active_tb_value
            self._intervention.Individual_Property_Active_TB_Key = individual_property_active_tb_key
        elif individual_property_active_tb_value is not None or individual_property_active_tb_key is not None:
            raise ValueError(
                "If individual_property_active_tb_value is set, individual_property_active_tb_key must also be set, and vice versa.")
        self._intervention.Adult_Treatment_Age = validate_value_range(adult_treatment_age, 'adult_treatment_age', -1, 3.40282e+38, float)


# DanB - After seaching the campaign files for known country models, I did not find an HIVDelayedIntervention that used
# the special "expiration_period" parameter.  I'm going to leave this private just in case someone needs it, but they
# should be able to use DelayedIntervention instead.

class _HIVDelayedIntervention(IndividualIntervention):  # make this class private until we have time to review and test it.
    """
    **HIVDelayedIntervention** is an intermediate intervention class based on **DelayedIntervention**, but adds
    several features that are specific to the HIV model. This intervention enables event broadcasting after the
    delay period expires.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        broadcast_event(str, required):
            The event that should occur at the end of the delay period.

        expiration_period(float, optional):
            A fixed time period, in days, after which the **Broadcast_On_Expiration_Event** occurs instead of
            the **Broadcast_Event**. Only applied if the **Expiration_Period** occurs earlier than the end of
            the delay period. For example, if loss to follow-up (LTFU) occurs at a high rate for the first 6
            months of care, and then later transitions to a lower rate, then the **Expiration_Period** should
            be set to 183 days and **Broadcast_On_Expiration_Event** can link to another delay intervention
            with a longer average delay time until LTFU. If LTFU does not occur in the first 6 months, then the
            expiration will allow the first rate to give way to the post-6-month rate.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 3.40282e+38

        delay_period_distribution(BaseDistribution, required):
            The distribution type to use for assigning the delay period for distributing interventions. Each
            assigned value is a random draw from the distribution. Please use the following distribution classes
            from emodpy_hiv.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        broadcast_on_expiration_event(str, optional):
            If the delay intervention expires before arriving at the end of the delay period, this specifies
            the event that should occur. For example, if loss to follow-up occurs at a high rate for the first
            6 months of care, and then later transitions to a lower rate, then the **Expiration_Period** should
            be set to 183 days and **Broadcast_On_Expiration_Event** can link to another delay intervention
            with a longer average delay time until loss to follow up (LTFU). If LTFU does not occur in the
            first 6 months, then the expiration will allow the first rate to give way to the post-6-month rate.
            See the list of available events for possible values .See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 broadcast_event: str,
                 delay_period_distribution: BaseDistribution,
                 expiration_period: float = 3.40282e+38,
                 broadcast_on_expiration_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVDelayedIntervention', common_intervention_parameters)

        self._intervention.Broadcast_Event = set_event(broadcast_event, 'broadcast_event', campaign, False)
        self._intervention.Expiration_Period = validate_value_range(expiration_period, 'expiration_period', 0, 3.40282e+38, float)
        self._intervention.Coverage = 1 # do not make option for user
        self._intervention.Broadcast_On_Expiration_Event = set_event(broadcast_on_expiration_event, 'broadcast_on_expiration_event', campaign, True)

        if not isinstance(delay_period_distribution, BaseDistribution):
            raise ValueError(f"delay_period_distribution must be an instance of BaseDistribution, not {type(delay_period_distribution)}.")
        self.set_distribution(delay_period_distribution, 'Delay_Period')

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the HIVDelayedIntervention intervention.')


class HIVDrawBlood(IndividualIntervention):
    """
    The **HIVDrawBlood** intervention class represents a test where blood is drawn and the person's CD4 or
    viral load are determined. It allows for a test result to be recorded and used for future health care
    decisions, but does not intrinsically lead to a health care event. A future health care decision will
    use this recorded CD4 count or viral load, even if the actual CD4/viral load has changed since last
    phlebotomy. The result can be updated by distributing another **HIVDrawBlood** intervention.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        positive_diagnosis_event(str, required):
            If an individual tests positive, this specifies an event that may trigger another intervention when
            the event occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or
            use your own custom event.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_event: str,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVDrawBlood', common_intervention_parameters)

        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)


class HIVMuxer(IndividualIntervention):
    """
    The **HIVMuxer** intervention class is a method of placing groups of individuals into a waiting pattern for the next
    event, and is based on DelayedIntervention. **HIVMuxer** adds the ability to limit the number of times an individual
    can be registered with the delay, which ensures that an individual is only provided with the delay one time. For
    example, without **HIVMuxer**, an individual could be given an exponential delay twice, effectively doubling the rate
    of leaving the delay.

    Please refer to the documentation for **HIVMuxer** at the following link:
    :doc:`emod-hiv:emod/parameter-campaign-individual-hivmuxer`

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        muxer_name(str, required):
            A name used to identify the delay and check whether individuals have entered it multiple times. If
            the same name is used at multiple points in the health care process, then the number of entries is
            combined when **max_entries** is applied.

        delay_period_distribution(BaseDistribution, required):
            The distribution type to use for assigning the delay period for distributing interventions. Each
            assigned value is a random draw from the distribution. Please use the following distribution classes
            from emodpy_hiv.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        max_entries(int, optional):
            The maximum number of times the individual can be registered with the HIVMuxer delay. Determines
            what should happen if an individual reaches the HIVMuxer stage of health care multiple times. For
            example, registering for an exponential delay two times effectively doubles the rate of leaving the
            delay. Setting **max_entries** to 1 prevents the rate from doubling.
            Minimum value: 0
            Maximum value: 2147480000.0
            Default value: 1

        expiration_period(float, optional):
            A fixed time period, in days, after which the **broadcast_on_expiration_event** occurs instead of
            the **broadcast_delay_complete_event**. Only applied if the **expiration_period** occurs earlier than the end of
            the delay period. For example, if loss to follow-up (LTFU) occurs at a high rate for the first 6
            months of care, and then later transitions to a lower rate, then the **Expiration_Period** should
            be set to 183 days and **Broadcast_On_Expiration_Event** can link to another delay intervention
            with a longer average delay time until LTFU. If LTFU does not occur in the first 6 months, then the
            expiration will allow the first rate to give way to the post-6-month rate.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 3.40282e+38

        broadcast_on_expiration_event(str, optional):
            If the delay intervention expires before arriving at the end of the delay period, this specifies
            the event that should occur. For example, if loss to follow-up occurs at a high rate for the first
            6 months of care, and then later transitions to a lower rate, then the **Expiration_Period** should
            be set to 183 days and **Broadcast_On_Expiration_Event** can link to another delay intervention
            with a longer average delay time until loss to follow up (LTFU). If LTFU does not occur in the
            first 6 months, then the expiration will allow the first rate to give way to the post-6-month rate.
            See the list of available events for possible values. See :doc:`emod-hiv:emod/parameter-campaign-event-list`
            for events already used in EMOD or use your own custom event.
            Default value: None

        broadcast_delay_complete_event(str, optional):
            The event that should occur at the end of the delay period. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your own custom
            event.
            custom event.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 muxer_name: str,
                 delay_period_distribution: BaseDistribution,
                 max_entries: int = 1,
                 expiration_period: float = 3.40282e+38,
                 broadcast_on_expiration_event: str = None,
                 broadcast_delay_complete_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVMuxer', common_intervention_parameters)

        self._intervention.Muxer_Name = muxer_name
        if not isinstance(delay_period_distribution, BaseDistribution):
            raise ValueError(f"delay_period_distribution must be an instance of BaseDistribution, not {type(delay_period_distribution)}.")
        self.set_distribution(delay_period_distribution, 'Delay_Period')

        self._intervention.Max_Entries = validate_value_range(max_entries, 'max_entries', 0, 2147480000.0, int)
        self._intervention.Expiration_Period = validate_value_range(expiration_period, 'expiration_period', 0, 3.40282e+38, float)
        self._intervention.Broadcast_On_Expiration_Event = set_event(broadcast_on_expiration_event, 'broadcast_on_expiration_event', campaign, True)
        self._intervention.Broadcast_Event = set_event(broadcast_delay_complete_event, 'broadcast_event', campaign, True)

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the HIVMuxer intervention.')


class HIVPiecewiseByYearAndSexDiagnostic(IndividualIntervention):
    """
    The **HIVPiecewiseByYearAndSexDiagnostic** intervention class is used to model the roll-out of an
    intervention over time. Unlike **HIVSigmoidByYearAndSexDiagnostic**, which requires the time trend
    to have a sigmoid shape, this intervention allows for any trend of time to be configured using
    piecewise or linear interpolation. The trends over time can be configured differently for males and
    females. Note that the term "diagnosis" is used, but this intervention is typically used more like a
    trend in behavior or coverage over time.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        time_value_map(ValueMap, required):
            Please use the ValueMap class from emodpy_hiv.campaign.common to define the **time_value_map**.
            The years (times) and matching probabilities for test results. This parameter uses
            ValueMap to define **Times** (by year) and **Values** for the history and expected
            treatment guidelines for future years. This creates a JSON structure containing one array of
            **Times** and one for **Values**, which allows for a time-variable probability that can take on any
            shape over time. When queried at a simulation year corresponding to one of the listed **Times**, it
            returns the corresponding **Value**. When queried earlier than the first listed **Time**, it
            returns the default **Value**. When queried in between listed **Times**, it either returns the
            **Value** for the most recent past time (when **linear_interpolation** is False) or linearly interpolates
            Values between **Times** (when **linear_interpolation** is True). When queried after the last **Time** in
            the list, it returns the last **Value**. The **Times** and **Values** must be of equal length, and
            can consist of a single value. **Times** must monotonically increase.

        positive_diagnosis_event(str, required):
            If an individual tests positive, this specifies an event that may trigger another intervention when
            the event occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or
            use your own custom event.

        negative_diagnosis_event(str, optional):
            If an individual tests negative, this specifies an event that may trigger another intervention when
            the event occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or
            use your own custom event.
            Default value: None

        linear_interpolation(bool, optional):
            When set to False, interpolation between values in the **time_value_map** is zero-order
            ('staircase'). When set to True, interpolation between values in the **time_value_map** is linear. The
            final value is held constant for all times after the last time specified in the **time_value_map**.
            Default value: False

        female_multiplier(float, optional):
            Allows for the probabilities in the **time_value_map** to be different for males and females, by
            multiplying the female probabilities by a constant value.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 1

        default_value(float, optional):
            The probability of positive diagnosis if the intervention is used before the earliest specified
            time in the **time_value_map**.
            Minimum value: 0
            Maximum value: 1
            Default value: 0

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 time_value_map: ValueMap,
                 positive_diagnosis_event: str,
                 negative_diagnosis_event: str = None,
                 linear_interpolation: bool = False,
                 female_multiplier: float = 1,
                 default_value: float = 0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVPiecewiseByYearAndSexDiagnostic', common_intervention_parameters)

        self._intervention.Time_Value_Map = time_value_map.to_schema_dict(campaign)
        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)
        self._intervention.Interpolation_Order = 1 if linear_interpolation else 0
        self._intervention.Female_Multiplier = validate_value_range(female_multiplier, 'female_multiplier', 0, 3.40282e+38, float)
        self._intervention.Default_Value = validate_value_range(default_value, 'default_value', 0, 1, float)


class HIVRandomChoice(IndividualIntervention):
    """
    The **HIVRandomChoice** intervention class is used to change the logic in how and where treatment is applied
    to individuals based on specified probabilities.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        choice_probabilities(list[float], required):
            An array of probabilities that the event will be selected, used with **choice_names**. Values in
            map must be normalized to sum to one.

        choice_names(list[str], required):
            An array of event names to be broadcast if randomly selected, used with **choice_probabilities**.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 choice_probabilities: list[float] = None,
                 choice_names: list[str] = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVRandomChoice', common_intervention_parameters)

        # check if the choice_probabilities and choice_names are the same length
        if len(choice_probabilities) != len(choice_names):
            raise ValueError('The length of choice_probabilities and choice_names must be the same.')

        # check if the sum of the choice_probabilities is equal to 1
        if sum(choice_probabilities) != 1:
            raise ValueError('The sum of choice_probabilities must be equal to 1.')

        choice_names = [set_event(choice_name, 'choice_name', campaign, False) for choice_name in choice_names]

        self._intervention.Choice_Probabilities = choice_probabilities
        self._intervention.Choice_Names = choice_names


class HIVRapidHIVDiagnostic(IndividualIntervention):
    """
    The **HIVRapidHIVDiagnostic** intervention class builds on **StandardDiagnostic** by also updating the
    individual's knowledge of their HIV status. This can affect their access to ART in the future as well as
    other behaviors. This intervention should be used only if the individual's knowledge of their status should
    impact a voluntary male circumcision campaign.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        positive_diagnosis_event(str, required):
            If the test is positive, this specifies an event that will be broadcast.
            See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or
            use your own custom event.

        base_sensitivity(float, optional):
            Use this parameter to set a constant value for sensitivity of the diagnostic. If you want to set
            the sensitivity over time, use the **sensitivity_versus_time** parameter instead. You need to set either
            **base_sensitivity** or **sensitivity_versus_time**.
            This sets the proportion of the time that individuals with the condition being tested receive a positive
            diagnostic test. When set to 1, the diagnostic always accurately reflects the condition. When set to zero,
            then individuals who have the condition always receive a false-negative diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: None

        sensitivity_versus_time(ValueMap, Optional):
            Use this parameter to set the sensitivity of the diagnostic test over time. If you want to set a constant
            value for sensitivity, use the **base_sensitivity** parameter instead. You need to set either
            **base_sensitivity** or **sensitivity_versus_time**.
            This expects a ValueMap object (from emodpy_hiv.campaign.common) that contains two arrays:
            The 'Times' values are the duration from when the person became infected. 'Values' is the
            sensitivity of the diagnostic for the given age of the infection.
            Default value: None


        base_specificity(float, optional):
            The specificity of the diagnostic. This sets the proportion of the time that individuals without
            the condition being tested receive a negative diagnostic test. When set to 1, the diagnostic always
            accurately reflects the lack of having the condition. When set to zero, then individuals who do not
            have the condition always receive a false-positive diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        probability_received_result(float, optional):
            The probability that an individual received the results of a diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        negative_diagnosis_event(str, optional):
            If the test is negative, this event will be broadcast. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your own
            custom event.
            Default value: None

        enable_is_symptomatic(bool, optional):
            If true, requires an infection to be symptomatic to return a positive test.
            Default value: True

        days_to_diagnosis(float, optional):
            The number of days from diagnosis (which is done when the intervention is distributed) until a
            positive response is performed. The response to a negative diagnosis is done immediately when the
            diagnosis is made (at distribution of the intervention).
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_event: str,
                 base_sensitivity: float = None,
                 base_specificity: float = 1,
                 sensitivity_versus_time: ValueMap = None,
                 probability_received_result: float = 1,
                 negative_diagnosis_event: str = None,
                 enable_is_symptomatic: bool = False,
                 days_to_diagnosis: float = 0,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVRapidHIVDiagnostic', common_intervention_parameters)

        if base_sensitivity is None and sensitivity_versus_time is None:
            raise ValueError('Either base_sensitivity or sensitivity_versus_time must be provided.')
        elif base_sensitivity is not None and sensitivity_versus_time is not None:
            raise ValueError('Only one of base_sensitivity or sensitivity_versus_time can be provided.')
        elif base_sensitivity is not None:
            self._intervention.Base_Sensitivity = validate_value_range(base_sensitivity, 'base_sensitivity', 0, 1, float)
            self._intervention.Sensitivity_Type = SensitivityType.SINGLE_VALUE
        else:
            self._intervention.Sensitivity_Versus_Time = sensitivity_versus_time.to_schema_dict(campaign)
            self._intervention.Sensitivity_Type = SensitivityType.VERSUS_TIME

        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Probability_Received_Result = validate_value_range(probability_received_result, 'probability_received_result', 0, 1, float)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)
        self._intervention.Enable_Is_Symptomatic = enable_is_symptomatic
        self._intervention.Days_To_Diagnosis = validate_value_range(days_to_diagnosis, 'days_to_diagnosis', 0, 3.40282e+38, float)
        self._intervention.Base_Specificity = validate_value_range(base_specificity, 'base_specificity', 0, 1, float)


class HIVSigmoidByYearAndSexDiagnostic(IndividualIntervention):
    """
    The **HIVSigmoidByYearAndSexDiagnostic** intervention class broadcasts a positive 'diagnosis' event by
    selecting a probability of that event from a sigmoidal curve versus time. For a linear approach, use
    **HIVPiecewiseByYearandSexDiagnostic**.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        positive_diagnosis_event(str, required):
            If an individual tests positive, this specifies an event that may trigger another intervention when
            the event occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or
            use your own custom event.

        year_sigmoid(Sigmoid, required):
            Defines a sigmoidal curve for the probability of a positive diagnosis versus time (year).

        female_multiplier(float, optional):
            Allows for the sigmoid time-varying probability to be different for males and females, by
            multiplying the female probability by a constant value.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 1

        negative_diagnosis_event(str, optional):
            If an individual tests negative, this specifies an event that may trigger another intervention when
            the event occurs. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_event: str,
                 year_sigmoid: Sigmoid,
                 female_multiplier: float = 1,
                 negative_diagnosis_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVSigmoidByYearAndSexDiagnostic', common_intervention_parameters)

        if year_sigmoid is None:
            raise ValueError("'year_sigmoid' must be defined.")

        # Don't need to check values because these values are the same as the ranges in the Sigmoid class.
        self._intervention.Ramp_Min     = year_sigmoid.min
        self._intervention.Ramp_Max     = year_sigmoid.max
        self._intervention.Ramp_MidYear = year_sigmoid.mid
        self._intervention.Ramp_Rate    = year_sigmoid.rate
        self._intervention.Female_Multiplier = validate_value_range(female_multiplier, 'female_multiplier', 0, 3.40282e+38, float)
        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)


# DanB - After searching the campaign files for known country models, I did not see any one using HIVSimpleDiagnostic.
# People pretty much use HIVRapidHIVDiagnostic instead.  I'm going to leave this private just in case someone needs it.

class _HIVSimpleDiagnostic(IndividualIntervention):  # make this class private until we have time to review and test it.
    """
    The **HIVSimpleDiagnostic** intervention class is based on the **SimpleDiagnostic** intervention, but adds the
    ability to specify outcomes upon both positive and negative diagnosis (whereas **SimpleDiagnostic** only allows
    for an outcome resulting from a positive diagnosis). **HIVSimpleDiagnostic** tests for HIV status without
    logging the HIV test to the individual's medical history. To log the HIV test to the medical history,
    use **HIVRapidHIVDiagnostic** instead.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        positive_diagnosis_event(str, required):
            If the test is positive, this specifies an event that can trigger another intervention when the
            event occurs. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.

        negative_diagnosis_event(str, optional):
            This parameter defines the event to be broadcasted on a
            negative test result. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        enable_is_symptomatic(bool, optional):
            If true, requires an infection to be symptomatic to return a positive test.
            Default value: True

        days_to_diagnosis(float, optional):
            The number of days from diagnosis (which is done when the intervention is distributed) until a
            positive response is performed. The response to a negative diagnosis is done immediately when the
            diagnosis is made (at distribution of the intervention).
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0

        base_specificity(float, optional):
            The specificity of the diagnostic. This sets the proportion of the time that individuals without
            the condition being tested receive a negative diagnostic test. When set to 1, the diagnostic always
            accurately reflects the lack of having the condition. When set to zero, then individuals who do not
            have the condition always receive a false-positive diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        base_sensitivity(float, optional):
            The sensitivity of the diagnostic. This sets the proportion of the time that individuals with the
            condition being tested receive a positive diagnostic test. When set to 1, the diagnostic always
            accurately reflects the condition. When set to zero, then individuals who have the condition always
            receive a false-negative diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_event: str,
                 negative_diagnosis_event: str = None,
                 enable_is_symptomatic: bool = False,
                 days_to_diagnosis: float = 0,
                 base_specificity: float = 1,
                 base_sensitivity: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'HIVSimpleDiagnostic', common_intervention_parameters)

        self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event, 'positive_diagnosis_event', campaign, False)
        self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event, 'negative_diagnosis_event', campaign, True)
        self._intervention.Enable_Is_Symptomatic = enable_is_symptomatic
        self._intervention.Days_To_Diagnosis = validate_value_range(days_to_diagnosis, 'days_to_diagnosis', 0, 3.40282e+38, float)
        self._intervention.Base_Specificity = validate_value_range(base_specificity, 'base_specificity', 0, 1, float)
        self._intervention.Base_Sensitivity = validate_value_range(base_sensitivity, 'base_sensitivity', 0, 1, float)


class InterventionForCurrentPartners(IndividualIntervention):
    """
    The **InterventionForCurrentPartners** intervention class provides a mechanism for the partners of
    individuals in the care system to also seek care. Partners do not need to seek testing at the same time;
    a delay may occur between the initial test and the partner's test. If a relationship has been paused,
    such as when a partner migrates to a different node, the partner will not be contacted.

    Either the **intervention_config** or **broadcast_event** parameter must be set, but not both.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        intervention_config(IndividualIntervention, optional):
            The intervention definition that is immediately distributed to the partner. This parameter
            is required if **broadcast_event** is not set.
            Default value: None

        broadcast_event(str, optional):
            The event that is immediately broadcast to the partner.
            See :doc:`emod-hiv:emod/parameter-campaign-event-list` for possible built-in values, or use your own
            custom event. This parameter is required if **intervention_config** is not set.
            Default value: None

        prioritize_partners_by(PrioritizePartnersBy, optional):
            How to prioritize partners for the intervention, as long as they have been in a relationship longer
            than **minimum_duration_years**. Expect PrioritizePartnersBy enum from emodpy_hiv.utils.emod_enum.
            Possible values are:
            * NO_PRIORTIZATION - All partners are contacted.
            * CHOSEN_AT_RANDOM - Partners are randomly selected until **maximum_partners** have received the
            intervention.
            * LONGER_TIME_IN_RELATIONSHIP - Partners are sorted in descending order of the duration of the
            relationship. Partners are contacted from the beginning of this list until **maximum_partners**
            have received the intervention.
            * SHORTER_TIME_IN RELATIONSHIP - Partners are sorted in ascending order of the duration of the
            relationship. Partners are contacted from the beginning of the list until **maximum_partners** have
            received the intervention.
            * OLDER_AGE - Partners are sorted in descending order of their age. Partners are contacted from the
            beginning of this list until **maximum_partners** have received the intervention.
            * YOUNGER_AGE - Partners sorted in ascending order of the duration of the relationship.
            Partners are contacted from the beginning of this list until **maximum_partners** have received the
            intervention.
            * RELATIONSHIP_TYPE - Partners are sorted based on the order of relationship types defined in the
            **relationship_types** array. For example, 'relationship_types' : ['MARITAL', 'INFORMAL',
            'TRANSITORY', 'COMMERCIAL'], will prioritize marital first, then informal, then transitory, then
            commercial, with random selection between mulitple partners of the same type.
            Default value: PrioritizePartnersBy.NO_PRIORITIZATION

        relationship_types(list[RelationshipTypes], optional):
            An array listing all possible relationship types for which partners can qualify for the
            intervention. Expect RelationshipTypes enum emodpy_hiv.utils.emod_enum. Possible values are:
            TRANSITORY, INFORMAL, MARITAL, and COMMERCIAL.
            If **prioritize_partners_by** is set to PrioritizePartnersBy.RELATIONSHIP_TYPE, then the order of these types is used. The
            array may not contain duplicates, and cannot be empty.
            Default value: None

        minimum_duration_years(float, optional):
            The minimum amount of time, in years, between relationship formation and the current time for the
            partner to qualify for the intervention.
            Minimum value: 0
            Maximum value: 200
            Default value: 0

        maximum_partners(float, optional):
            The maximum number of partners that will receive the intervention. Required when
            **Prioritize_Partners_By** is not set to NO_PRIORITIZATION.
            Minimum value: 0
            Maximum value: 100
            Default value: 100

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 intervention_config: IndividualIntervention = None,
                 broadcast_event: str = None,
                 prioritize_partners_by: 'PrioritizePartnersBy' = PrioritizePartnersBy.NO_PRIORITIZATION,
                 relationship_types: list[str] = None,
                 minimum_duration_years: float = 0,
                 maximum_partners: float = 100,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'InterventionForCurrentPartners', common_intervention_parameters)

        self._intervention.Prioritize_Partners_By = prioritize_partners_by
        if prioritize_partners_by == PrioritizePartnersBy.RELATIONSHIP_TYPE:
            if relationship_types is None or len(relationship_types) == 0:
                raise ValueError('The relationship_types parameter must be set when prioritize_partners_by is set to RELATIONSHIP_TYPE.')
            self._intervention.Relationship_Types = relationship_types

        if prioritize_partners_by != PrioritizePartnersBy.NO_PRIORITIZATION:
            self._intervention.Maximum_Partners = validate_value_range(maximum_partners, 'maximum_partners', 0, 100,
                                                                       float)

        self._intervention.Minimum_Duration_Years = validate_value_range(minimum_duration_years, 'minimum_duration_years', 0, 200, float)

        if intervention_config is not None and broadcast_event is not None:
            raise ValueError('You can only set either intervention_config or broadcast_event, but not both.')
        elif intervention_config is not None:
            self._intervention.Intervention_Config = intervention_config.to_schema_dict()
            self._intervention.Event_Or_Config = EventOrConfig.Config
        elif broadcast_event is not None:
            self._intervention.Broadcast_Event = set_event(broadcast_event, 'broadcast_event', campaign, False)
            self._intervention.Event_Or_Config = EventOrConfig.Event
        else:
            raise ValueError('You must set either intervention_config or broadcast_event.')

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the InterventionForCurrentPartners intervention.')


class MaleCircumcision(IndividualIntervention):
    """
    The **MaleCircumcision** intervention class introduces male circumcision as a method to control
    HIV transmission. Voluntary medical male circumcision (VMMC) permanently reduces a male's likelihood
    of acquiring HIV; successful distribution results in a reduction in the probability of transmission.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        distributed_event_trigger(str, optional):
            The name of the event to be broadcast when the intervention is distributed to an individual. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        circumcision_reduced_acquire(float, optional):
            The reduction of susceptibility to STI by voluntary male medical circumcision (VMMC).
            Minimum value: 0
            Maximum value: 1
            Default value: 0.6

        apply_if_higher_reduced_acquire(bool, optional):
            If set to False, the **MaleCircumcision** intervention can never be applied to someone who
            already has a **MaleCircumcision** intervention. If set to True, a male who already has a
            **MaleCircumcision** intervention, but whose pre-existing **MaleCircumcision** intervention has a
            lower efficacy parameter (**circumcision_reduced_acquire**) than the one about to be applied, will
            receive the higher-efficacy **MaleCircumcision**.
            Default value: False

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 distributed_event_trigger: str = None,
                 circumcision_reduced_acquire: float = 0.6,
                 apply_if_higher_reduced_acquire: bool = False,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'MaleCircumcision', common_intervention_parameters)

        self._intervention.Distributed_Event_Trigger = set_event(distributed_event_trigger, 'distributed_event_trigger', campaign, True)
        self._intervention.Circumcision_Reduced_Acquire = validate_value_range(circumcision_reduced_acquire, 'circumcision_reduced_acquire', 0, 1, float)
        self._intervention.Apply_If_Higher_Reduced_Acquire = 1 if apply_if_higher_reduced_acquire else 0


class ModifyStiCoInfectionStatus(IndividualIntervention):
    """
    The **ModifyStiCoInfectionStatus** intervention class creates or removes STI co-infections
    (which influence the rate of HIV transmission). This intervention can be used to represent
    things like STI treatment programs or STI outbreaks.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        new_sti_coinfection_status(bool, required):
            Determines whether to apply STI co-infection, or cure/remove STI co-infection. Set to True to
            include co-infection; set to False to remove co-infection.

    """

    def __init__(self,
                 campaign: api_campaign,
                 new_sti_coinfection_status: bool):
        super().__init__(campaign, 'ModifyStiCoInfectionStatus')

        self._intervention.New_STI_CoInfection_Status = 1 if new_sti_coinfection_status else 0

    def _set_intervention_name(self, intervention_name: str) -> None:
        raise ValueError('Intervention_Name is not a valid parameter for the ModifyStiCoInfectionStatus intervention.')

    def _set_dont_allow_duplicates(self, dont_allow_duplicates: bool) -> None:
        raise ValueError('Dont_Allow_Duplicates is not a valid parameter for the ModifyStiCoInfectionStatus intervention.')

    def _set_new_property_value(self, new_property_value: str) -> None:
        raise ValueError('New_Property_Value is not a valid parameter for the ModifyStiCoInfectionStatus intervention.')

    def _set_disqualifying_properties(self, disqualifying_properties: Union[dict[str, str], list[str]]) -> None:
        raise ValueError('Disqualifying_Properties is not a valid parameter for the ModifyStiCoInfectionStatus intervention.')

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the ModifyStiCoInfectionStatus intervention.')


class PMTCT(IndividualIntervention):
    """
    The **PMTCT** (Prevention of Mother-to-Child Transmission) intervention class is used to define the efficacy
    of PMTCT treatment at time of birth. This can only be used for mothers who are not on suppressive ART and
    will automatically expire 40 weeks after distribution. Efficacy will be reset to 0 once it expires.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        efficacy(float, optional):
            Represents the efficacy of a Prevention of Mother to Child Transmission (PMTCT) intervention,
            defined as the rate ratio of mother to child transmission (MTCT) between women receiving the
            intervention and women not receiving the intervention. A setting of 1 is equivalent to 100%
            blocking efficacy, and 0 reverts to the default probability of transmission, configured through the
            config.json parameter **Maternal_Transmission_Probability**.
            Minimum value: 0
            Maximum value: 1
            Default value: 0.5

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 efficacy: float = 0.5,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'PMTCT', common_intervention_parameters)

        self._intervention.Efficacy = validate_value_range(efficacy, 'efficacy', 0, 1, float)

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the PMTCT intervention.')


class STIBarrier(IndividualIntervention):
    """
    The **STIBarrier** intervention is used to reduce the probability of STI or HIV transmission by applying
    a time-variable probability of condom usage. Each **STIBarrier** intervention is directed at a specific
    relationship type, and must be configured as a sigmoid trend over time.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        usage_expiration_event(str, optional):
            When the person stops using the STIBarrier, this event will be broadcasted.  See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        usage_duration_distribution(BaseDistribution, required):
            For the distribution of each **STIBarrier**, a randomly selected duration from this distribution
            will determine when the man stops using the intervention and revert back to condom usage based on
            the relationship type. Please use the following distribution classes
            from emodpy_hiv.utils.distributions to define the distribution:
            * ConstantDistribution
            * UniformDistribution
            * GaussianDistribution
            * ExponentialDistribution
            * PoissonDistribution
            * LogNormalDistribution
            * DualConstantDistribution
            * WeibullDistribution
            * DualExponentialDistribution

        relationship_type('RelationshipType', optional):
            The relationship type to which the condom usage probability is applied. Possible values are:
            * TRANSITORY
            * INFORMAL
            * MARITAL
            * COMMERCIAL
            Default value: TRANSITORY

        condom_usage_sigmoid(Sigmoid, required):
            The new sigmoid to use when determining the probability that a condom is used during a coital act
            within the specified relationship. This overrides the **Condom_Usage_Probablility** for the
            relationship type as defined in the Demographics file.  If None (default), the **Condom_Usage_Probablility**
            is not overridden.
            - **WARNING:** For **STIBarrier**, the 'min' and 'max' values of the sigmoid must be between 0 and 1.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 usage_expiration_event: str,
                 usage_duration_distribution: BaseDistribution,
                 relationship_type: 'RelationshipType' = RelationshipType.TRANSITORY,
                 condom_usage_sigmoid: Sigmoid = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'STIBarrier', common_intervention_parameters)

        if condom_usage_sigmoid is None:
            raise ValueError("'condom_usage_sigmoid' must be defined.")
        else:
            condom_usage_sigmoid.check_value_ranges( class_name="STIBarrier",
                                                     min_low= 0, min_high=1,
                                                     max_low= 0, max_high=1,
                                                     mid_low=1900, mid_high=2200,
                                                     rate_low=-100, rate_high=100)

        if not isinstance(usage_duration_distribution, BaseDistribution):
            raise ValueError(f"usage_duration_distribution must be an instance of BaseDistribution, not {type(usage_duration_distribution)}.")
        self.set_distribution(usage_duration_distribution, 'Usage_Duration')

        self._intervention.Usage_Expiration_Event = set_event(usage_expiration_event, 'usage_expiration_event', campaign, True)
        self._intervention.Relationship_Type = relationship_type
        self._intervention.Rate    = condom_usage_sigmoid.rate
        self._intervention.MidYear = condom_usage_sigmoid.mid
        self._intervention.Late    = condom_usage_sigmoid.max
        self._intervention.Early   = condom_usage_sigmoid.min


class STIIsPostDebut(IndividualIntervention):
    """
    The **STIIsPostDebut** intervention class checks to see if the individual is post-STI debut.
    Note that this is not connected to IndividualProperties in the demographics file.

    User can either set the diagnosis_config parameters:
    - `positive_diagnosis_config` (required)
    - `negative_diagnosis_config` (optional)

    or set the diagnosis_event parameters:
    - `positive_diagnosis_event` (required)
    - `negative_diagnosis_event` (optional)

    but not both.

    Args:
        campaign (api_campaign, optional):
            An instance of the emod_api.campaign module.

        positive_diagnosis_config(IndividualIntervention, optional):
            The intervention distributed to individuals if they test positive.
            Default value: None

        negative_diagnosis_config(IndividualIntervention, optional):
            The intervention distributed to individuals if they test negative.
            Default value: None

        positive_diagnosis_event(str, optional):
            The event to be broadcast on a positive test result. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        negative_diagnosis_event(str, optional):
            The event to be broadcast on a negative test result. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_config: IndividualIntervention = None,
                 negative_diagnosis_config: IndividualIntervention = None,
                 positive_diagnosis_event: str = None,
                 negative_diagnosis_event: str = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'STIIsPostDebut', common_intervention_parameters)

        # Make sure that user only set either config or event, but not both
        if any([positive_diagnosis_config, negative_diagnosis_config]) and any([positive_diagnosis_event, negative_diagnosis_event]):
            raise ValueError('You can only set either diagnosis_config(s) or diagnosis_event(s), but not both.')
        # Make sure that user set either config or event
        if not any([positive_diagnosis_config, negative_diagnosis_config, positive_diagnosis_event,
                    negative_diagnosis_event]):
            raise ValueError('You must set either diagnosis_config(s) or diagnosis_event(s).')

        # Set the intervention based on the provided config
        if positive_diagnosis_config or negative_diagnosis_config:
            if not positive_diagnosis_config:
                raise ValueError('positive_diagnosis_config must be set if you set negative_diagnosis_config.')
            self._intervention.Positive_Diagnosis_Config = positive_diagnosis_config.to_schema_dict()
            if negative_diagnosis_config:
                self._intervention.Negative_Diagnosis_Config = negative_diagnosis_config.to_schema_dict()
            self._intervention.Event_Or_Config = EventOrConfig.Config
            self._intervention.pop("Positive_Diagnosis_Event")
            self._intervention.pop("Negative_Diagnosis_Event")

        # Set the event based on the provided event
        if positive_diagnosis_event or negative_diagnosis_event:
            if not positive_diagnosis_event:
                raise ValueError('positive_diagnosis_event must be set if you set negative_diagnosis_event.')
            self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event,
                                                                    'positive_diagnosis_event', campaign, False)
            self._intervention.Negative_Diagnosis_Event = set_event(negative_diagnosis_event,
                                                                    'negative_diagnosis_event', campaign, True)
            self._intervention.Event_Or_Config = EventOrConfig.Event
            self._intervention.pop("Positive_Diagnosis_Config")
            self._intervention.pop("Negative_Diagnosis_Config")


class SetSexualDebutAge(IndividualIntervention):
    """
    The **SetSexualDebutAge** intervention class is used to set the age of the individual when they start
    seeking sexual relationships.  If the individual's current age is greater than the age being set, they
    will immediately debut.

    This intervention is typically used when setting the configuration parameter **Sexual_Debut_Age_Setting_Type**
    to **FROM_INTERVENTION**.  This setting causes all individuals to be initialized with a very large sexual debut
    age (max float) so that they never debut.  The intervention is used to target specific individuals and set their
    debut age.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        setting_type('SettingType', optional):
            Use Weibull distribution to initialize sexual debut age or an intervention.
            Default value: CURRENT_AGE

        distributed_event_trigger(str, optional):
            The name of the event to be broadcast when the intervention is distributed to an individual. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        age_years(float, optional):
            The age (in years) at which the person receiving the intervention will start seeking sexual
            relationships.  If the person is already order than this age, they will start seeking relationships
            immediately. You must set **Setting_Type** to **USER_SPECIFIED** for the parameter to become
            activated.
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 125

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 setting_type: 'SettingType' = SettingType.CURRENT_AGE,
                 distributed_event_trigger: str = None,
                 age_years: float = 125,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'SetSexualDebutAge', common_intervention_parameters)

        self._intervention.Setting_Type = setting_type
        self._intervention.Distributed_Event_Trigger = set_event(distributed_event_trigger, 'distributed_event_trigger', campaign, True)
        if setting_type == SettingType.USER_SPECIFIED:
            self._intervention.Age_Years = validate_value_range(age_years, 'age_years', 0, 3.40282e+38, float)

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the SetSexualDebutAge intervention.')


class StartNewRelationship(IndividualIntervention):
    """
    The **StartNewRelationship** intervention class provides a method of triggering the formation of a relationship
    following a user-specified event. The parameters of the relationship that is formed can also be customized by
    the user, such as individual properties required of the partner, or modified condom usage probability within
    the relationship. Note: These new relationships can be made by people of any age (the intervention disregards
    **IsPostDebut** and **Sexual_Debut_Age_Min**). Additionally, these relationships are considered outside of the
    Pair Formation Algorithm (PFA), and do not impact/are not impacted by concurrency or pair formation parameters.
    Coital act and condom usage rate are as per the corresponding relationship type, unless modified by the user.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        relationship_type('RelationshipType', optional):
            The type of the relationship to start for this person. Possible values are:
            * TRANSITORY
            * INFORMAL
            * MARITAL
            * COMMERCIAL
            Default value: TRANSITORY

        partner_has_ip(str, optional):
            The **IndividualProperty** key:value pair that the potential partner must have. Empty string
            implies no filtering. See :ref:`demo-properties` parameters for more information.
            Default value: None

        relationship_created_event(str, optional):
            The event trigger to broadcast when a new relationship is created due to the intervention. See
            :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        condom_usage_sigmoid(Sigmoid, required):
            The new sigmoid to use when determining the probability that a condom is used during a coital act
            within the specified relationship. This overrides the **Condom_Usage_Probablility** for the
            relationship type as defined in the Demographics file.  If None (default), the **Condom_Usage_Probablility**
            is not overridden.
            - **WARNING:** For **StartNewRelationship**, the 'min' and 'max' values of the sigmoid must be between 0 and 1.

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 4 common
            parameters: intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            The following parameters are not valid for this intervention:
            cost
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 relationship_type: 'RelationshipType' = RelationshipType.TRANSITORY,
                 partner_has_ip: str = "",
                 relationship_created_event: str = "",
                 condom_usage_sigmoid: Sigmoid = None,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'StartNewRelationship', common_intervention_parameters)

        self._intervention.Relationship_Type = relationship_type
        self._intervention.Relationship_Created_Event = set_event(relationship_created_event, 'relationship_created_event', campaign, True)

        if partner_has_ip:
            self._intervention.Partner_Has_IP = validate_key_value_pair(partner_has_ip)

        if condom_usage_sigmoid is not None:
            condom_usage_sigmoid.check_value_ranges( class_name="StartNewRelationship",
                                                     min_low= 0, min_high=1,
                                                     max_low= 0, max_high=1,
                                                     mid_low=1900, mid_high=2200,
                                                     rate_low=-100, rate_high=100)
            self._intervention.Condom_Usage_Parameters_Type = CondomUsageParametersType.SPECIFY_USAGE
            self._intervention.Condom_Usage_Sigmoid = condom_usage_sigmoid.to_schema_dict(campaign)
        else:
            self._intervention.Condom_Usage_Parameters_Type = CondomUsageParametersType.USE_DEFAULT

    def _set_cost(self, cost: float) -> None:
        raise ValueError('Cost_To_Consumer is not a valid parameter for the StartNewRelationship intervention.')


class _StiCoInfectionDiagnostic(IndividualIntervention): # make this class private until we have time to review and test it.
    """
    The **StiCoInfectionDiagnostic** intervention class is based on **SimpleDiagnostic** and allows for diagnosis
    of STI co-infection. It includes **SimpleDiagnostic** features and works in conjunction with the
    **ModifyCoInfectionStatus** flag.

    Args:
        campaign (api_campaign, required):
            An instance of the emod_api.campaign module.

        positive_diagnosis_config(IndividualIntervention, required):
            The intervention distributed to individuals if they test positive.

        treatment_fraction(float, optional):
            The fraction of positive diagnoses that are given the positive_diagnosis_config or
            positive_diagnosis_event, whichever is defined.
            diagnosis.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        positive_diagnosis_event(str, optional):
            If the test is positive, this specifies an event that can trigger another intervention when the event
            occurs. See :doc:`emod-hiv:emod/parameter-campaign-event-list` for events already used in EMOD or use your
            own custom event.
            Default value: None

        enable_is_symptomatic(bool, optional):
            If true, requires an infection to be symptomatic to return a positive test.
            Default value: True

        days_to_diagnosis(float, optional):
            The number of days from diagnosis (which is done when the intervention is distributed) until a
            positive response is performed. The response to a negative diagnosis is done immediately when the
            diagnosis is made (at distribution of the intervention).
            Minimum value: 0
            Maximum value: 3.40282e+38
            Default value: 0

        base_specificity(float, optional):
            The specificity of the diagnostic. This sets the proportion of the time that individuals without
            the condition being tested receive a negative diagnostic test. When set to 1, the diagnostic always
            accurately reflects the lack of having the condition. When set to zero, then individuals who do not
            have the condition always receive a false-positive diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        base_sensitivity(float, optional):
            The sensitivity of the diagnostic. This sets the proportion of the time that individuals with the
            condition being tested receive a positive diagnostic test. When set to 1, the diagnostic always
            accurately reflects the condition. When set to zero, then individuals who have the condition always
            receive a false-negative diagnostic test.
            Minimum value: 0
            Maximum value: 1
            Default value: 1

        common_intervention_parameters (CommonInterventionParameters, optional):
            The CommonInterventionParameters object that contains the 5 common
            parameters: cost, intervention_name, new_property_value, disqualifying_properties, dont_allow_duplicates.
            Default value: None
    """

    def __init__(self,
                 campaign: api_campaign,
                 positive_diagnosis_config: IndividualIntervention,
                 treatment_fraction: float = 1,
                 positive_diagnosis_event: str = None,
                 enable_is_symptomatic: bool = False,
                 days_to_diagnosis: float = 0,
                 base_specificity: float = 1,
                 base_sensitivity: float = 1,
                 common_intervention_parameters: CommonInterventionParameters = None):
        super().__init__(campaign, 'StiCoInfectionDiagnostic', common_intervention_parameters)
        if bool(positive_diagnosis_event) == bool(positive_diagnosis_config):
            raise ValueError("Either 'positive_diagnosis_config' or 'positive_diagnosis_event' must be defined, "
                             "but not both.")
        if positive_diagnosis_config:
            if not isinstance(positive_diagnosis_config, IndividualIntervention):
                raise ValueError('positive_diagnosis_config must be a Intervention instance.')
            self._intervention.Positive_Diagnosis_Config = positive_diagnosis_config.to_schema_dict()
            self._intervention.Event_Or_Config = EventOrConfig.Config
            self._intervention.pop("Positive_Diagnosis_Event")
        else:
            self._intervention.Positive_Diagnosis_Event = set_event(positive_diagnosis_event,
                                                                    'positive_diagnosis_event', campaign, False)
            self._intervention.pop("Positive_Diagnosis_Config")
            self._intervention.Event_Or_Config = EventOrConfig.Event

        self._intervention.Treatment_Fraction = validate_value_range(treatment_fraction, 'treatment_fraction', 0, 1, float)
        self._intervention.Enable_Is_Symptomatic = enable_is_symptomatic
        self._intervention.Days_To_Diagnosis = validate_value_range(days_to_diagnosis, 'days_to_diagnosis', 0, 3.40282e+38, float)
        self._intervention.Base_Specificity = validate_value_range(base_specificity, 'base_specificity', 0, 1, float)
        self._intervention.Base_Sensitivity = validate_value_range(base_sensitivity, 'base_sensitivity', 0, 1, float)


# __all_exports: A list of classes that are intended to be exported from this module.
# the private classes are commented out until we have time to review and test them.
__all_exports = [
    ARTDropout,
    # _ARTMortalityTable,
    AgeDiagnostic,
    AntiretroviralTherapy,
    AntiretroviralTherapyFull,
    CD4Diagnostic,
    CoitalActRiskFactors,
    FemaleContraceptive,
    HIVARTStagingByCD4Diagnostic,
    HIVARTStagingCD4AgnosticDiagnostic,
    # _HIVDelayedIntervention,
    HIVDrawBlood,
    HIVMuxer,
    HIVPiecewiseByYearAndSexDiagnostic,
    HIVRandomChoice,
    HIVRapidHIVDiagnostic,
    HIVSigmoidByYearAndSexDiagnostic,
    # _HIVSimpleDiagnostic,
    IVCalendar,
    # _ImmunityBloodTest,
    InterventionForCurrentPartners,
    MaleCircumcision,
    ModifyStiCoInfectionStatus,
    PMTCT,
    RangeThreshold,
    STIBarrier,
    STIIsPostDebut,
    SetSexualDebutAge,
    Sigmoid,
    StartNewRelationship,
    # _StiCoInfectionDiagnostic,
    BroadcastEvent,
    BroadcastEventToOtherNodes,
    ControlledVaccine,
    DelayedIntervention,
    IndividualImmunityChanger,
    IndividualNonDiseaseDeathRateModifier,
    MigrateIndividuals,
    MultiEffectBoosterVaccine,
    MultiEffectVaccine,
    MultiInterventionDistributor,
    OutbreakIndividual,
    PropertyValueChanger,
    SimpleBoosterVaccine,
    SimpleVaccine,
    StandardDiagnostic,
]

# The following loop sets the __module__ attribute of each class in __all_exports to the name of the current module.
# This is done to ensure that when these classes are imported from this module, their __module__ attribute correctly
# reflects their source module.

for _ in __all_exports:
    _.__module__ = __name__

# __all__: A list that defines the public interface of this module.
# This is essential to ensure that Sphinx builds documentation for these classes, including those that are imported
# from emodpy.
# It contains the names of all the classes that should be accessible when this module is imported using the syntax
# 'from module import *'.
# Here, it is set to the names of all classes in __all_exports.

__all__ = [_.__name__ for _ in __all_exports]
