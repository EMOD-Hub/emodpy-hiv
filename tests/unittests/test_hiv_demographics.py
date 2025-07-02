import unittest
import pytest
import sys
import pandas as pd
from pathlib import Path
from typing import List, Callable

from emod_api.demographics.Node import Node
from emod_api.demographics.fertility_distribution import FertilityDistribution
from emod_api.demographics.Updateable import Updateable

from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.demographics.relationship_types import RelationshipTypes

parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

ROUNDING_DIGITS = 9


@pytest.mark.unit
class TestHIVDemographics(unittest.TestCase):

    def setUp(self):
        self.ages_years = [15.0, 24.999, 25.0, 34.999, 35.0, 44.999]  # M ages
        self.calendar_years = [2010.0, 2014.999, 2015.0, 2019.999]  # N times
        self.pregnancy_rate_matrix = [[103.3, 103.3, 77.5, 77.5],  # fertility rates at age 15.0, the six timepoints above
                                      [103.3, 103.3, 77.5, 77.5],  # fertility rates at age 24.999
                                      [265.0, 265.0, 278.7, 278.7],  # fertility rates at age 25.0
                                      [265.0, 265.0, 278.7, 278.7],  # fertility rates at age 34.999
                                      [152.4, 152.4, 129.2, 129.2],  # fertility rates at age 35.0
                                      [152.4, 152.4, 129.2, 129.2]]  # fertility rates at age 44.999
        self.fertility_distribution = FertilityDistribution(ages_years=self.ages_years,
                                                            calendar_years=self.calendar_years,
                                                            pregnancy_rate_matrix=self.pregnancy_rate_matrix)
        self.nodes = []
        self.demographics = HIVDemographics(nodes=self.nodes, default_society_template="PFA-Southern-Africa")

        self.fertility_distribution2 = FertilityDistribution(ages_years=[15, 20],
                                                             calendar_years=[2000, 2020, 2040],
                                                             pregnancy_rate_matrix=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

    def tearDown(self):
        pass

        #
        # a few of reusable testing functions for any distribution use case copied in from emodpy tests.
        #

    def _verify_complex_distribution_values(self, use_case: str, node: Node, expected: Updateable):
        self.assertIsInstance(getattr(node.individual_attributes, f"{use_case}_distribution"), Updateable)

        # Value-checking complex distribution, not memory address checking as Updateable will not change addresses
        attributes = vars(getattr(node.individual_attributes, f"{use_case}_distribution"))
        expected_attributes = vars(expected)
        self.assertEqual(sorted(attributes.keys()), sorted((expected_attributes.keys())))
        for attribute, value in attributes.items():
            self.assertEqual(value, expected_attributes[attribute])

        flag_attribute = f"{use_case}_distribution_flag"
        if hasattr(node.individual_attributes, flag_attribute):
            self.assertEqual(getattr(node.individual_attributes, flag_attribute), None)
            self.assertEqual(getattr(node.individual_attributes, f"{use_case}_distribution1"), None)
            self.assertEqual(getattr(node.individual_attributes, f"{use_case}_distribution2"), None)

    def _test_set_complex_distribution_works(self,
                                             use_case: str,
                                             distribution,
                                             implicit_functions: List[Callable] = None):
        """
        Some common code to allow slight test variations/test naming sugar
        Args:
            explicit: True/False: explicitly or implicitly specify the default node

        Returns:
            Nothing
        """
        selected_node_ids = [0]  # one way to specify the default node

        initial_n_implicits = len(self.demographics.implicits)
        setting_function = getattr(self.demographics, f"set_{use_case}_distribution")
        setting_function(distribution=distribution, node_ids=selected_node_ids)

        final_n_implicits = len(self.demographics.implicits)

        # check right values on modified demographics object
        nodes = self.demographics.get_nodes_by_id(node_ids=selected_node_ids)
        for _, node in nodes.items():
            self._verify_complex_distribution_values(node=node, expected=distribution, use_case=use_case)

        # ensuring implicit config call/update(s) are set up properly
        if implicit_functions is not None:
            self.assertEqual(final_n_implicits - initial_n_implicits, len(implicit_functions))
            implicits_set = self.demographics.implicits[-1 * len(implicit_functions):]
            for i in range(len(implicits_set)):
                self.assertEqual(implicits_set[i], implicit_functions[i])
        else:
            self.assertEqual(final_n_implicits, initial_n_implicits)

    def _test_set_complex_distribution_works_twice(self, use_case: str,
                                                   distribution1, distribution2,
                                                   implicit_functions: List[Callable] = None):
        """
        Ensure that setting a complex distribution more than once updates properly (last updated values win)

        Returns:
            Nothing
        """
        selected_node_ids = [0]  # one way to specify the default node

        initial_n_implicits = len(self.demographics.implicits)

        setting_function = getattr(self.demographics, f"set_{use_case}_distribution")
        setting_function(distribution=distribution1, node_ids=selected_node_ids)
        setting_function(distribution=distribution2, node_ids=selected_node_ids)

        final_n_implicits = len(self.demographics.implicits)

        # check right values on modified demographics object
        nodes = self.demographics.get_nodes_by_id(node_ids=selected_node_ids)
        for _, node in nodes.items():
            self._verify_complex_distribution_values(node=node, expected=distribution2, use_case=use_case)

        # ensuring implicit config call/update(s) are set up properly
        if implicit_functions is not None:
            self.assertEqual(final_n_implicits - initial_n_implicits, 2 * len(implicit_functions))
            implicits_set = self.demographics.implicits[-2 * len(implicit_functions):]  # They've been set twice
            implicit_functions = implicit_functions + implicit_functions  # They've been set twice
            for i in range(len(implicits_set)):
                self.assertEqual(implicits_set[i], implicit_functions[i])
        else:
            self.assertEqual(final_n_implicits, initial_n_implicits)

    #
    # Fertility distribution tests using the same format as emodpy age/mortality/etc distribution tests
    #

    def test_set_complex_fertility_distribution_works(self):
        from emod_api.demographics.DemographicsTemplates import _set_fertility_age_year
        self._test_set_complex_distribution_works(use_case='fertility', implicit_functions=[_set_fertility_age_year],
                                                  distribution=self.fertility_distribution)

    def test_set_complex_fertility_distribution_works_twice(self):
        from emod_api.demographics.DemographicsTemplates import _set_fertility_age_year
        self._test_set_complex_distribution_works_twice(use_case='fertility', implicit_functions=[_set_fertility_age_year],
                                                        distribution1=self.fertility_distribution,
                                                        distribution2=self.fertility_distribution2)

    def test_from_template_node(self):
        lat = 11
        lon = 22
        pop = 999
        name = "test_name"
        forced_id = 101
        demog = HIVDemographics.from_template_node(lat=lat, lon=lon, pop=pop, name=name, forced_id=forced_id,
                                                   default_society_template='PFA-Southern-Africa')

        self.assertTrue(isinstance(demog, HIVDemographics))
        self.assertEqual(len(demog.nodes), 1)

        self._default_test(demog)

        nodes = demog.nodes
        node_attributes = nodes[0].to_dict()['NodeAttributes']
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].forced_id, forced_id)
        self.assertEqual(nodes[0].name, name)
        self.assertEqual(node_attributes['InitialPopulation'], pop)
        self.assertEqual(node_attributes["Latitude"], lat)
        self.assertEqual(node_attributes["Longitude"], lon)

    def _default_test(self, demog):
        defaults = demog.default_node.to_dict()  # ['Defaults']
        self.assertIn('NodeAttributes', defaults)
        self.assertIn('IndividualAttributes', defaults)
        self.assertIn('Society', defaults)

    def test_assortivity(self):
        # using the default node (specifying no node(s) means the default node)
        rel_type = RelationshipTypes.transitory.value
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        matrix = [[0.3, 0.1, 0.5], [0.4, 0.2, 0.25], [0.2, 0.7, 0.8]]

        demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.transitory.value, assortivity_matrix=matrix)

        output = demog.get_node_by_id(node_id=None).to_dict()
        assortivity_area = output["Society"][rel_type]["Pair_Formation_Parameters"]["Assortivity"]

        self.assertEqual(["LOW", "MEDIUM", "HIGH"], assortivity_area["Axes"])
        self.assertEqual("INDIVIDUAL_PROPERTY", assortivity_area["Group"])
        self.assertEqual("Risk", assortivity_area["Property_Name"])
        self.assertEqual(matrix, assortivity_area["Weighting_Matrix_RowMale_ColumnFemale"])

        for row in assortivity_area["Weighting_Matrix_RowMale_ColumnFemale"]:
            for number in row:
                self.assertTrue(isinstance(number, float), msg=f"Value {number} in matrix is Not a number")

    def test_assortivity_columns_exception(self):
        node_id = 0
        rel_type = RelationshipTypes.transitory.value
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        big_matrix = [[0.3, 0.1, 0.5, 0.6], [0.4, 0.2, 0.25, 0.7], [0.2, 0.7, 0.8, 0.8]]

        with self.assertRaises(ValueError):
            demog.set_pair_formation_parameters(relationship_type=rel_type, assortivity_matrix=big_matrix, node_ids=[node_id])

    def test_assortivity_rows_exception(self):
        node_id = 0
        rel_type = RelationshipTypes.transitory.value
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        too_many_lists = [[0.3, 0.1, 0.4], [0.3, 0.2, 0.4], [0.5, 0.1, 0.4], [0.6, 0.1, 0.4]]

        with self.assertRaises(ValueError):
            demog.set_pair_formation_parameters(relationship_type=rel_type, assortivity_matrix=too_many_lists, node_ids=[node_id])

    def test_set_concurrency_params_by_type_and_risk(self):
        node_id = 0
        rel_type = RelationshipTypes.commercial.value
        risk = "HIGH"
        max_simul_rels_male = 100
        max_simul_rels_female = 10
        prob_xtra_rel_male = 0.1
        prob_xtra_rel_female = 0.9
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        demog.set_concurrency_params_by_type_and_risk(relationship_type=rel_type,
                                                      risk_group=risk,
                                                      max_simul_rels_male=max_simul_rels_male,
                                                      max_simul_rels_female=max_simul_rels_female,
                                                      prob_xtra_rel_male=prob_xtra_rel_male,
                                                      prob_xtra_rel_female=prob_xtra_rel_female,
                                                      node_ids=[node_id])

        output = demog.get_node_by_id(node_id=node_id).to_dict()
        concurrency_params = output["Society"][rel_type]['Concurrency_Parameters'][risk]

        self.assertEqual(concurrency_params['Max_Simultaneous_Relationships_Male'], max_simul_rels_male)
        self.assertEqual(concurrency_params['Max_Simultaneous_Relationships_Female'], max_simul_rels_female)
        self.assertEqual(concurrency_params['Prob_Extra_Relationship_Male'], prob_xtra_rel_male)
        self.assertEqual(concurrency_params['Prob_Extra_Relationship_Female'], prob_xtra_rel_female)

        # should not change the default values of other relationship type
        for other_rel_type in RelationshipTypes:
            if other_rel_type.value != rel_type:
                concurrency_params = output["Society"][other_rel_type.value]['Concurrency_Parameters']
                # self.assertNotIn(ip_value, concurrency_params.keys())
                concurrency_params = concurrency_params[risk]
                self.assertNotEqual(concurrency_params['Max_Simultaneous_Relationships_Male'], max_simul_rels_male)
                self.assertNotEqual(concurrency_params['Max_Simultaneous_Relationships_Female'], max_simul_rels_female)
                self.assertNotEqual(concurrency_params['Prob_Extra_Relationship_Male'], prob_xtra_rel_male)
                self.assertNotEqual(concurrency_params['Prob_Extra_Relationship_Female'], prob_xtra_rel_female)

    def test_set_pair_form_params(self):
        node_id = 0
        rel_type = RelationshipTypes.marital.value
        new_constant_rate = 0.05
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        demog.set_pair_formation_parameters(relationship_type=rel_type, formation_rate=new_constant_rate,
                                            node_ids=[node_id])

        output = demog.get_node_by_id(node_id=node_id).to_dict()
        pair_form_params = output["Society"][rel_type]['Pair_Formation_Parameters']
        self.assertEqual(pair_form_params['Formation_Rate_Type'], 'CONSTANT')
        self.assertEqual(pair_form_params['Formation_Rate_Constant'], new_constant_rate)

        # should not change the default values of other relationship type
        for other_rel_type in RelationshipTypes:
            if other_rel_type.value != rel_type:
                pair_form_params = output["Society"][other_rel_type.value]['Pair_Formation_Parameters']
                self.assertNotEqual(pair_form_params['Formation_Rate_Constant'], new_constant_rate)

    def test_set_coital_act_rate(self):
        node_id = 0
        rel_type = RelationshipTypes.informal.value
        rate = 0.9
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        demog.set_relationship_parameters(relationship_type=rel_type, coital_act_rate=rate, node_ids=[node_id])
        output = demog.get_node_by_id(node_id=node_id).to_dict()
        relationship_params = output["Society"][rel_type]['Relationship_Parameters']
        self.assertEqual(relationship_params['Coital_Act_Rate'], rate)

        # should not change the default values of other relationship type
        for other_rel_type in RelationshipTypes:
            if other_rel_type.value != rel_type:
                relationship_params = output["Society"][other_rel_type.value]['Relationship_Parameters']
                self.assertNotEqual(relationship_params['Coital_Act_Rate'], rate)

    def test_set_condom_usage_probs(self):
        node_id = 0
        rel_type = RelationshipTypes.transitory.value
        min_value = 0.2
        mid_value = 2005
        max_value = 0.8
        new_rate = 0.5
        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        demog.set_relationship_parameters(relationship_type=rel_type, condom_usage_min=min_value,
                                          condom_usage_mid=mid_value, condom_usage_max=max_value,
                                          condom_usage_rate=new_rate, node_ids=[node_id])
        output = demog.get_node_by_id(node_id=node_id).to_dict()
        condom_usage_probs = output["Society"][rel_type]['Relationship_Parameters']['Condom_Usage_Probability']
        self.assertEqual(condom_usage_probs['Min'], min_value)
        self.assertEqual(condom_usage_probs['Max'], max_value)
        self.assertEqual(condom_usage_probs['Mid'], mid_value)
        self.assertEqual(condom_usage_probs['Rate'], new_rate)

        # should not change the default values of other relationship type
        for other_rel_type in RelationshipTypes:
            if other_rel_type.value != rel_type:
                condom_usage_probs = output["Society"][other_rel_type.value]['Relationship_Parameters'][
                    'Condom_Usage_Probability']
                self.assertNotEqual(condom_usage_probs['Min'], min_value)
                self.assertNotEqual(condom_usage_probs['Max'], max_value)
                self.assertNotEqual(condom_usage_probs['Mid'], mid_value)
                self.assertNotEqual(condom_usage_probs['Rate'], new_rate)

    def test_relationship_duration(self):
        # NOTE: lambda and kappa are really relationship_scale and relationship_duration**-1, respectively.
        #   Keeping lambda/kappa names here since we are directly comparing the distribution values and their names come
        #   from emod-api .
        node_id = 1
        duration_scale = 0.1234
        duration_heterogeneity = 0.5678
        relationship_type = RelationshipTypes.informal.value

        demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name='some_name', forced_id=1,
                                                   default_society_template='PFA-Southern-Africa')
        # we will use this later to ensure default node is unaltered
        default_relationship_parameters = demog.get_node_by_id(node_id=0).society.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
        default_lambda = default_relationship_parameters.duration.weibull_lambda
        default_kappa = default_relationship_parameters.duration.weibull_kappa

        demog.set_relationship_parameters(relationship_type=relationship_type,
                                          duration_scale=duration_scale,
                                          duration_heterogeneity=duration_heterogeneity,
                                          node_ids=[node_id])
        node = demog.get_node_by_id(node_id=node_id)
        relationship_parameters = node.society.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
        self.assertEqual(relationship_parameters.duration.weibull_lambda, duration_scale)
        self.assertEqual(relationship_parameters.duration.weibull_kappa, duration_heterogeneity ** -1)

        # ensure default node was not modified
        default_relationship_parameters = demog.get_node_by_id(node_id=0).society.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
        self.assertEqual(default_relationship_parameters.duration.weibull_lambda, default_lambda)
        self.assertEqual(default_relationship_parameters.duration.weibull_kappa, default_kappa)

    def test_ensure_default_and_regular_nodes_are_updated_independently(self):
        # checks to ensure that when the default node is altered, nodes 1+ are not and vice versa (one test per
        # society data chunk)

        #
        # pair formation parameters test
        #

        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        relationship_type = RelationshipTypes.transitory.value
        matricies_by_node = {0: [[0.31, 0.1, 0.5], [0.41, 0.2, 0.25], [0.21, 0.7, 0.8]],
                             1: [[0.25, 0.1, 0.5], [0.45, 0.2, 0.25], [0.5, 0.7, 0.8]]}

        # This is crazy, but doing the setting TWICE, forward and backward, to ensure neither node-setting overrides
        # the other (both are given a chance to erroneously override the other
        items = list(matricies_by_node.items())
        # forward
        for node_id, matrix in items:
            demographics.set_pair_formation_parameters(relationship_type=relationship_type, assortivity_matrix=matrix,
                                                       node_ids=[node_id])
        # verify each node is still right
        for node_id, matrix in items:
            node = demographics.get_node_by_id(node_id=node_id)
            pfp = node.society.get_pair_formation_parameters_by_relationship_type(relationship_type=relationship_type)
            self.assertEqual(pfp.Assortivity.matrix, matrix)

        # backward
        for node_id, matrix in list(reversed(items)):
            demographics.set_pair_formation_parameters(relationship_type=relationship_type, assortivity_matrix=matrix,
                                                       node_ids=[node_id])
        # verify each node is still right
        for node_id, matrix in list(reversed(items)):
            node = demographics.get_node_by_id(node_id=node_id)
            pfp = node.society.get_pair_formation_parameters_by_relationship_type(relationship_type=relationship_type)
            self.assertEqual(pfp.Assortivity.matrix, matrix)

        #
        # concurrency parameters
        #

        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        relationship_type = RelationshipTypes.informal.value
        risk = 'MEDIUM'
        values_by_node = {0: {'max_simul_rels_male': 1000, 'max_simul_rels_female': 1001,
                              'prob_xtra_rel_male': 1002.0, 'prob_xtra_rel_female': 1003.0},
                          1: {'max_simul_rels_male': 1004, 'max_simul_rels_female': 1005,
                              'prob_xtra_rel_male': 1006.0, 'prob_xtra_rel_female': 1007.0}}
        renaming_dict = {
            'max_simul_rels_male': 'max_simultaneous_relationships_male',
            'max_simul_rels_female': 'max_simultaneous_relationships_female',
            'prob_xtra_rel_male': 'probability_extra_relationship_male',
            'prob_xtra_rel_female': 'probability_extra_relationship_female'
        }
        # This is crazy, but doing the setting TWICE, forward and backward, to ensure neither node-setting overrides
        # the other (both are given a chance to erroneously override the other
        items = list(values_by_node.items())
        # forward
        for node_id, value_dict in items:
            demographics.set_concurrency_params_by_type_and_risk(relationship_type=relationship_type, risk_group=risk,
                                                                 node_ids=[node_id], **value_dict)
        # verify each node is still right
        for node_id, value_dict in items:
            node = demographics.get_node_by_id(node_id=node_id)
            cp = node.society.get_concurrency_parameters_by_relationship_type_and_risk(relationship_type=relationship_type,
                                                                                       risk=risk)
            for attribute, value in value_dict.items():
                self.assertEqual(getattr(cp, renaming_dict[attribute]), value)

        # backward
        for node_id, value_dict in list(reversed(items)):
            demographics.set_concurrency_params_by_type_and_risk(relationship_type=relationship_type, risk_group=risk,
                                                                 node_ids=[node_id], **value_dict)
        # verify each node is still right
        for node_id, value_dict in list(reversed(items)):
            node = demographics.get_node_by_id(node_id=node_id)
            cp = node.society.get_concurrency_parameters_by_relationship_type_and_risk(relationship_type=relationship_type,
                                                                                       risk=risk)
            for attribute, value in value_dict.items():
                self.assertEqual(getattr(cp, renaming_dict[attribute]), value)

        #
        # relationship parameters
        #

        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        relationship_type = RelationshipTypes.marital.value
        values_by_node = {0: {'coital_act_rate': 500, 'condom_usage_min': 501, 'condom_usage_mid': 502,
                              'condom_usage_max': 503, 'condom_usage_rate': 504, 'duration_scale': 505,
                              'duration_heterogeneity': 506},
                          1: {'coital_act_rate': 507, 'condom_usage_min': 508, 'condom_usage_mid': 509,
                              'condom_usage_max': 510, 'condom_usage_rate': 511, 'duration_scale': 512,
                              'duration_heterogeneity': 513}
                          }
        # This is crazy, but doing the setting TWICE, forward and backward, to ensure neither node-setting overrides
        # the other (both are given a chance to erroneously override the other
        items = list(values_by_node.items())
        # forward
        for node_id, value_dict in items:
            demographics.set_relationship_parameters(relationship_type=relationship_type, node_ids=[node_id],
                                                     **value_dict)
        # verify each node is still right
        for node_id, value_dict in items:
            node = demographics.get_node_by_id(node_id=node_id)
            rp = node.society.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
            comparable = {
                'coital_act_rate': getattr(rp, 'coital_act_rate'),
                'condom_usage_min': rp.condom_usage.min,
                'condom_usage_mid': rp.condom_usage.mid,
                'condom_usage_max': rp.condom_usage.max,
                'condom_usage_rate': rp.condom_usage.rate,
                'duration_scale': rp.duration.weibull_lambda,
                'duration_heterogeneity': rp.duration.weibull_kappa ** -1
            }
            for attribute, value in value_dict.items():
                # self.assertEqual(comparable[attribute], value)
                self.assertEqual(round(comparable[attribute], ROUNDING_DIGITS), round(value, ROUNDING_DIGITS))

        # backward
        for node_id, value_dict in list(reversed(items)):
            demographics.set_relationship_parameters(relationship_type=relationship_type, node_ids=[node_id],
                                                     **value_dict)
        # verify each node is still right
        for node_id, value_dict in list(reversed(items)):
            node = demographics.get_node_by_id(node_id=node_id)
            rp = node.society.get_relationship_parameters_by_relationship_type(relationship_type=relationship_type)
            comparable = {
                'coital_act_rate': getattr(rp, 'coital_act_rate'),
                'condom_usage_min': rp.condom_usage.min,
                'condom_usage_mid': rp.condom_usage.mid,
                'condom_usage_max': rp.condom_usage.max,
                'condom_usage_rate': rp.condom_usage.rate,
                'duration_scale': rp.duration.weibull_lambda,
                'duration_heterogeneity': rp.duration.weibull_kappa ** -1
            }
            for attribute, value in value_dict.items():
                # self.assertEqual(comparable[attribute], value)
                self.assertEqual(round(comparable[attribute], ROUNDING_DIGITS), round(value, ROUNDING_DIGITS))

    def test_adding_an_IP_distribution(self):
        # testing the core function called by adding risk/HCA/cascade distributions
        node_id = 0
        property_name = "Washington State"
        values = ["West of Cascades", "East of Cascades"]
        distribution = [0.7, 0.3]
        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        demographics._add_or_update_individual_property_distribution(property_name=property_name,
                                                                     values=values,
                                                                     distribution=distribution,
                                                                     node_ids=[0])
        node = demographics.get_node_by_id(node_id=node_id)
        self.assertTrue(node.has_individual_property(property_key=property_name))
        ip = node.get_individual_property(property_key=property_name)
        self.assertEqual(ip.property, property_name)
        self.assertEqual(ip.values, ip.values)
        self.assertEqual(ip.initial_distribution, distribution)

        # ensure adding again causes no problems; just overwrites the existing one
        values = ["San Juan Islands", "Everything else"]
        distribution = [0.01, 0.99]
        demographics._add_or_update_individual_property_distribution(property_name=property_name,
                                                                     values=values,
                                                                     distribution=distribution,
                                                                     node_ids=[0])
        node = demographics.get_node_by_id(node_id=node_id)
        self.assertTrue(node.has_individual_property(property_key=property_name))
        ip = node.get_individual_property(property_key=property_name)
        self.assertEqual(ip.property, property_name)
        self.assertEqual(ip.values, ip.values)
        self.assertEqual(ip.initial_distribution, distribution)

    def test_nonexistant_node_access_throws_exception(self):
        node_id = 99
        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)
        self.assertRaises(HIVDemographics.UnknownNodeException, demographics.get_node_by_id, node_id=node_id)

    def test_from_population_dataframe(self):
        csv_file = Path(parent, 'inputs', 'initial_population.csv')
        df = pd.read_csv(csv_file)
        demographics = HIVDemographics.from_population_dataframe(df=df, default_society_template='PFA-Southern-Africa')

        self.assertEqual(len(demographics.implicits), 1)  # enable births
        self.assertEqual(len(demographics.migration_files), 0)
        self.assertEqual(len(demographics.nodes), 10)

        # Expected node populations & names
        expected = {
            1: {'population': 304498, 'name': 'Central'},
            2: {'population': 459461, 'name': 'Copperbelt'},
            3: {'population': 371018, 'name': 'Eastern'},
            4: {'population': 231074, 'name': 'Luapula'},
            5: {'population': 510456, 'name': 'Lusaka'},
            6: {'population': 165784, 'name': 'Muchinga'},
            7: {'population': 169368, 'name': 'Northwestern'},
            8: {'population': 257607, 'name': 'Northern'},
            9: {'population': 370381, 'name': 'Southern'},
            10: {'population': 210352, 'name': 'Western'},
        }
        for node_id, expected_dict in expected.items():
            node = demographics.get_node_by_id(node_id=node_id)
            self.assertEqual(node.id, node_id)
            self.assertEqual(node.name, expected_dict['name'])
            self.assertEqual(node.pop, expected_dict['population'])

        # todo: what should the default node values be in this test, if any?
        # TODO: add check of individual attributes on the nodes
        # TODO: add check of individual properties on the nodes
        # TODO: maybe just these on test_load_zambia_country_model_alpha?

    def test_ensure_raw_use_is_prevented(self):
        # testing the core function called by adding risk/HCA/cascade distributions
        demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name="some_name", forced_id=1)

        # This attribute of emod-api Demographics is forcefully deprecated to prevent data loss in HIV
        def access_raw_attribute():
            return demographics.raw

        self.assertRaises(AttributeError, access_raw_attribute)


if __name__ == '__main__':
    unittest.main()
