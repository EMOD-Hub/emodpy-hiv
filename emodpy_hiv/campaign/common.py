from emod_api import campaign as api_campaign
from emod_api import schema_to_class as s2c
from emodpy_hiv.utils.emod_enum import TargetDiseaseState

from typing import Union

# Importing necessary classes from the emodpy.campaign.common module so user can import them from the current
# module: emodpy_hiv.campaign.common module
# These classes are essential for defining campaign configurations and properties in the EMOD model.

# CommonInterventionParameters: A class used to define common parameters for interventions.
from emodpy.campaign.common import CommonInterventionParameters as CommonInterventionParameters

# MAX_AGE_YEARS: A constant representing the maximum age in years considered in the model.
from emodpy.campaign.common import MAX_AGE_YEARS as EMODPY_MAX_AGE_YEARS

# TargetGender: A class used to specify the gender of individuals targeted by an intervention.
from emodpy.campaign.common import TargetGender as TargetGender

# TargetDemographicsConfig: A class used to define the demographic characteristics of individuals targeted by an
# intervention.
from emodpy.campaign.common import TargetDemographicsConfig as TargetDemographicsConfig

# RepetitionConfig: A class used to configure the number of times an intervention event will occur.
from emodpy.campaign.common import RepetitionConfig as RepetitionConfig

# PropertyRestrictions: A class used to specify property restrictions for an intervention.
from emodpy.campaign.common import PropertyRestrictions as PropertyRestrictions

# ValueMap: A class used to map values over a defined range of time.
from emodpy.campaign.common import ValueMap as ValueMap

# Assigning the imported MAX_AGE_YEARS constant from emodpy to a local constant for use within this module.
MAX_AGE_YEARS = EMODPY_MAX_AGE_YEARS


class NChooserTargetedDistributionHIV:
    """
    **NChooserTargetedDistributionHIV** class to create an object specifying when, to whom,
    and how many interventions are distributed. This class is used in the **NChooserEventCoordinatorHIV** class.

    The number of individuals to distribute interventions to during this time period must be specified by either
    **num_targeted**
    or
    **num_targeted_males** and **num_targeted_female**. These values will be adjusted by x_Base_Population and spread
    evenly over the time period. Please refer to the emodpy_hiv.campaign.distributor.add_intervention_nchooser_df
    function for more information in 'Population Scaling' and 'Distribution Over Time' sections.

    Args:
        age_ranges_years (list[list[float]], required):
            - A 2D list specifying age ranges in years for qualifying individuals.
            - It should contain 2 lists, the first list is 'Min' age and the second list for 'Max' age.
            - An individual is considered in range if their age is greater than or equal to the minimum age and less than the maximum age.
            - In each age range (minimum age, maximum age), maxinum age must be greater or equal to minimum age.
            - There should not be overlapping age ranges.
            - It must have the same number of objects as num_targeted_xxx has elements.
            - For example, age_ranges_years = [[0, 1, 15, 50], [0.9999999, 14.9999999, 49.9999999, 64.9999999]] means that the
              intervention will be distributed to individuals with the following age ranges: [0, 0.9999999),
              [1, 14.9999999), [15, 49.9999999), [50, 64.9999999).
        num_targeted_females (list[int], optional):
            - The number of female individuals to distribute interventions to during this time period.
            - Note that this value will be scaled up by the population scaling factor equal to x_Base_Population.
            - If using this parameter, the length of the list should be the same length as each of the
              age_ranges_years and num_targeted_males. Cannot be used with num_targeted, leave num_targeted at None.
            - Minimum value: 0,
            - Maximum value: 2147480000.
            - Default value: None.
        num_targeted_males (list[int], optional):
            - The number of male individuals to distribute interventions to during this time period.
            - Note that this value will be scaled up by the population scaling factor equal to x_Base_Population.
            - If using this parameter, the length of the list should be the same length as each of the
              age_ranges_years and num_targeted_females. Cannot be used with num_targeted, leave num_targeted at None.
              - Minimum value: 0,
            - Maximum value: 2147480000.
            - Default value: None.
        num_targeted (list[int], optional):
            - The number of individuals to target with the intervention.
            - Note that this value will be scaled up by the population scaling factor equal to x_Base_Population.
            - If using this parameter, the length of the list should be the same length as each of the age_ranges_years.
              Cannot be used with num_targeted_males and num_targeted_female, leave them at None.
            - Minimum value: 0,
            - Maximum value: 2147480000,
            - Default value: None.
        start_year (float, optional):
            - The year to start distributing the intervention.
            - Defines the time period to distribute the intervention along with end_year. The intervention is evenly distributed between each time step in the time period.
            - To have the intervention applied other than at the beginning of the year, you must enter a decimal value after the year. For example, 2010.5 would have the intervention applied halfway through the year 2010.
            - Minimum value: 1900,
            - Maximum value: 2200,
            - Default value: 1900.
        end_year (float, optional):
            - The year to stop distributing the intervention.
            - Defines the time period to distribute the intervention along with start_year. The intervention is evenly distributed between each time step in the time period.
            - Minimum value: 1900,
            - Maximum value: 2200,
            - Default value: 2200.
        property_restrictions (PropertyRestrictions, optional):
            - A PropertyRestrictions to define the individual-level property restrictions in the coordinator.
            - Please note that node property restrictions are not supported in this feature.
            - Default value: None.
        target_disease_state (list[list[TargetDiseaseState]], optional):
            - A two-dimensional list of disease states using the TargetDiseaseState enum.
            - To qualify for the intervention, an individual must match at least one of the inner lists of disease states.
            - Each entry in the inner array is an "and" requirement, meaning an individual must match all states in one
              inner list to qualify.
            - Each inner list is combined with an "or" relationship with other inner list, meaning an individual needs
              to match at least one of the inner list to qualify.
            - Please refer to the Example section for more information about the "and", "or" relationship in this argument.
            - Possible values: Refer to the TargetDiseaseState enum for the possible values.
            - Default value: None.
        target_disease_state_has_intervention_name (str, optional):
            - The name of the intervention to look for in an individual, it's required when using TargetDiseaseState.HAS_INTERVENTION or TargetDiseaseState.NOT_HAS_INTERVENTION in target_disease_state.
            - Default value: None.

    Examples:
        Example 1: This example demonstrates how to create a target distribution for Nchooser coordinator to distribute
        intervention(s) to individuals with specific age ranges. The intervention will be distributed from year 2010 to
        2010.999 to MALE individuals with the following age ranges:
        [0, 0.9999999), [1, 14.9999999), [15, 49.9999999), [50, 64.9999999) and the number of targeted MALE individuals are:
        [0, 8064, 25054, 179]. While no FEMALE individuals are targeted. The targeted individuals should not have the
        intervention 'DMPA_or_control'.

        >>> from emodpy_hiv.campaign.common import NChooserTargetedDistributionHIV
        >>> age_ranges_years = [[0,         1,          15,         50],                # Min ages
        >>>                     [0.9999999, 14.9999999, 49.9999999, 64.9999999]]        # Max ages
        >>> num_targeted_females = [0,    0,          0,       0]
        >>> num_targeted_males   = [0,    8064,       25054,   179]
        >>> target_distribution = NChooserTargetedDistributionHIV(
        >>>                                           age_ranges_years=age_ranges_years,
        >>>                                           start_year=2010.0,
        >>>                                           end_year=2010.999,
        >>>                                           num_targeted_females=num_targeted_females,
        >>>                                           num_targeted_males=num_targeted_males,
        >>>                                           target_disease_state=[[TargetDiseaseState.NOT_HAVE_INTERVENTION]],
        >>>                                           target_disease_state_has_intervention_name="DMPA_or_control")

        Example 2: Simular to example 1, this example also demonstrates how to create a target distribution to target
        individuals with specific disease states. In this case, the intervention will be distributed to individuals with
        the following disease states:  (is HIV positive AND on ART) OR (has tested positive AND on ART), meaning that
        they are on ART and have either tested positive or are HIV positive.

        >>> from emodpy_hiv.campaign.common import NChooserTargetedDistributionHIV
        >>> age_ranges_years = [[0,         1,          15,         50],                # Min ages
        >>>                     [0.9999999, 14.9999999, 49.9999999, 64.9999999]]        # Max ages
        >>> num_targeted_females = [0,    0,          0,       0]
        >>> num_targeted_males   = [0,    8064,       25054,   179]
        >>> target_distribution = NChooserTargetedDistributionHIV(
        >>>                                           age_ranges_years=age_ranges_years,
        >>>                                           start_year=2010.0,
        >>>                                           end_year=2010.999,
        >>>                                           num_targeted_females=num_targeted_females,
        >>>                                           num_targeted_males=num_targeted_males,
        >>>                                           target_disease_state=[[TargetDiseaseState.HIV_POSITIVE, TargetDiseaseState.HAS_INTERVENTION],
        >>>                                                                 [TargetDiseaseState.TESTED_POSITIVE, TargetDiseaseState.HAS_INTERVENTION]],
        >>>                                           target_disease_state_has_intervention_name="ART")

        You can use property_restrictions to target **individuals** with specific properties that are not disease state
        specifc. Node property restriction is not supported in this feature. Please see examples in the PropertyRestrictions class.

    """
    def __init__(self,
                 age_ranges_years: list[list[Union[float]]],
                 num_targeted_females: list[int] = None,
                 num_targeted_males: list[int] = None,
                 num_targeted: list[int] = None,
                 start_year: float = 1900.0,
                 end_year: float = 2200.0,
                 property_restrictions: PropertyRestrictions = None,
                 target_disease_state: list[list[TargetDiseaseState]] = None,
                 target_disease_state_has_intervention_name: str = None):
        self.age_ranges_years = age_ranges_years
        self.num_targeted_females = num_targeted_females
        self.num_targeted_males = num_targeted_males
        self.num_targeted = num_targeted
        self.start_year = start_year
        self.end_year = end_year
        self.property_restrictions = property_restrictions
        self.target_disease_state = target_disease_state
        self.target_disease_state_has_intervention_name = target_disease_state_has_intervention_name
        self._targeted_distribution = None

        self.num_of_age_ranges, self.age_ranges_years_list = self._validate_age_range_years()

        self._validate_num_targeted_parameters()

        self._validate_start_end_years()

        self._validate_property_restriction()

        self.contains_intervention = self._validate_target_disease_state()

    def to_schema_dict(self, campaign: api_campaign):
        """
        Returns the TargetedDistributionHIV object as a dictionary that match the schema and can be used in the campaign.
        """
        self._targeted_distribution = s2c.get_class_with_defaults("idmType:TargetedDistributionHIV", campaign.schema_path)
        self._targeted_distribution.Age_Ranges_Years = self.age_ranges_years_list
        if self.num_targeted:
            self._targeted_distribution.Num_Targeted = self.num_targeted
        else:
            self._targeted_distribution.Num_Targeted_Females = self.num_targeted_females
            self._targeted_distribution.Num_Targeted_Males = self.num_targeted_males
        self._targeted_distribution.End_Year = self.end_year
        self._targeted_distribution.Start_Year = self.start_year
        if self.property_restrictions:
            self.property_restrictions._set_property_restrictions(self._targeted_distribution)
        if self.target_disease_state:
            self._targeted_distribution.Target_Disease_State = self.target_disease_state
            if self.contains_intervention:
                self._targeted_distribution.Target_Disease_State_Has_Intervention_Name = (
                    self.target_disease_state_has_intervention_name)
        self._targeted_distribution.finalize()
        return self._targeted_distribution

    def _validate_age_range_years(self):
        # Check if age_ranges_years is a 2D list contains 2 lists with the same length
        if len(self.age_ranges_years) != 2:
            raise ValueError("The age_ranges_years must contains exactly 2 lists.")
        # Check if max_ages and min_ages are lists and have the same length
        min_ages, max_ages  = self.age_ranges_years
        if not isinstance(max_ages, list) or not isinstance(min_ages, list) or len(max_ages) != len(min_ages):
            raise ValueError("The age_ranges_years must contains 2 lists with the same length.")

        # Check if each max_age is > min_age and the age ranges are not overlapping
        previous_max_age = -1
        for max_age, min_age in zip(max_ages, min_ages):
            if max_age < min_age:
                raise ValueError(f"Max age: {max_age} should be larger than min age: {min_age}.")
            # Check if the age ranges are overlapping
            if min_age < previous_max_age:
                raise ValueError(f"Min age: {min_age} should be larger than the previous max age: {previous_max_age}."
                                 f"Your age ranges are overlapping.")
            previous_max_age = max_age

        # Get the total number of age ranges
        num_of_age_ranges = len(max_ages)
        # Turn the age_ranges_years into a list of dictionaries each has a 'Min' and 'Max' age.
        age_ranges_years_list = list()
        for max_age, min_age in zip(max_ages, min_ages):
            age_ranges_years_list.append({"Max": float(max_age),
                                          "Min": float(min_age)})
        return num_of_age_ranges, age_ranges_years_list

    def _validate_num_targeted_parameters(self):
        # Make sure that either num_target or num_targeted_males and num_targeted_females are provided
        if not self.num_targeted and not (self.num_targeted_males and self.num_targeted_females):
            raise ValueError("Either num_targeted or num_targeted_male and num_targeted_females should be provided.")
        if self.num_targeted:
            if self.num_targeted_males or self.num_targeted_females:
                raise ValueError(
                    "num_targeted_males and num_targeted_females must be None if num_targeted is provided.")
            if len(self.num_targeted) != self.num_of_age_ranges:
                raise ValueError("num_targeted should have the same length as age ranges.")
        else:
            if not self.num_targeted_males or not self.num_targeted_females:
                raise ValueError(
                    "num_targeted_males and num_targeted_females should be provided if num_targeted is None.")
            # The num_targeted lists in the intervention should have the same length
            if (len(self.num_targeted_males) != len(self.num_targeted_females)
                    or len(self.num_targeted_females) != self.num_of_age_ranges
                    or len(self.num_targeted_males) != self.num_of_age_ranges):
                raise ValueError("num_targeted_males and num_targeted_females should have the same length "
                                 "as age ranges.")

    def _validate_start_end_years(self):
        # Check if start_year is less than end_year
        if self.start_year > self.end_year:
            raise ValueError(f"start_year: {self.start_year} should be less than end_year: {self.end_year}.")

    def _validate_property_restriction(self):
        # Set the property restrictions in the coordinator
        if self.property_restrictions:
            if isinstance(self.property_restrictions, PropertyRestrictions):
                if self.property_restrictions.node_property_restrictions:
                    raise ValueError(
                        "property_restrictions should have only individual property restrictions.")
            else:
                raise ValueError("property_restrictions should be an instance of PropertyRestrictions.")

    def _validate_target_disease_state(self):
        contains_intervention = False
        # Update distribution target disease state:
        if self.target_disease_state:
            if not isinstance(self.target_disease_state, list) or not all(
                    isinstance(row, list) for row in self.target_disease_state):
                raise ValueError("target_disease_state should be a 2D list.")
            # Check if all the elements in the inner lists are TargetDiseaseState enums
            for row in self.target_disease_state:
                for state in row:
                    if not isinstance(state, TargetDiseaseState):
                        raise ValueError(f"Invalid target_disease_state: {state}. It should contain only "
                                         f"TargetDiseaseState enums. Possible values are: "
                                         f"{TargetDiseaseState.__members__}.")

            intervention_states = [TargetDiseaseState.HAS_INTERVENTION, TargetDiseaseState.NOT_HAVE_INTERVENTION]
            # Check for the presence of intervention states: 'Has_Intervention' or 'Not_Have_Intervention'
            contains_intervention = any(
                state in row for row in self.target_disease_state for state in intervention_states)
            if contains_intervention and not self.target_disease_state_has_intervention_name:
                raise ValueError(f"If using '{TargetDiseaseState.HAS_INTERVENTION}' or "
                                 f"'{TargetDiseaseState.NOT_HAVE_INTERVENTION}' in target_disease_state, "
                                 "you must also define 'target_disease_state_has_intervention_name' to the name of"
                                 " the intervention.")
            elif not contains_intervention and self.target_disease_state_has_intervention_name:
                raise ValueError(
                    "You are setting 'target_disease_state_has_intervention_name' but target_disease_state"
                    " has no 'TargetDiseaseState.HAS_INTERVENTION' or 'TargetDiseaseState.NOT_HAVE_INTERVENTION'.")
        elif self.target_disease_state_has_intervention_name:
            raise ValueError(
                "You are setting 'target_disease_state_has_intervention_name' but target_disease_state is empty.")
        return contains_intervention


# __all_exports: A list of classes that are intended to be exported from this module.
__all_exports = [CommonInterventionParameters, PropertyRestrictions, TargetGender, TargetDemographicsConfig,
                 RepetitionConfig, ValueMap, NChooserTargetedDistributionHIV]

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
