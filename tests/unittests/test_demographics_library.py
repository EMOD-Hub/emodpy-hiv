import unittest
import pytest
from emodpy_hiv.countries.zambia import Zambia
from emodpy_hiv.demographics import library
from emodpy_hiv.demographics.relationship_types import RelationshipTypes
from emodpy_hiv.demographics.risk_groups import RiskGroups


@pytest.mark.unit
class TestDemographicsLibrary(unittest.TestCase):
    def setUp(self):
        print(f"running test: {self._testMethodName}")
        self.country_model = Zambia
        self.demographics = self.country_model.build_demographics()
        self.relationship_type = RelationshipTypes.marital.value
        self.risk_group = RiskGroups.medium.value

    def tearDown(self):
        pass

    def test_set_concurrency_parameters(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80*'-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)
            society = node.society
            original_all = society.to_dict()

            new_values = {
                'max_simul_rels_male': 17,
                'max_simul_rels_female': 18,
                'prob_xtra_rel_male': 2.345,
                'prob_xtra_rel_female': 3.456
            }
            result_mapping = {
                'max_simul_rels_male': 'Max_Simultaneous_Relationships_Male',
                'max_simul_rels_female': 'Max_Simultaneous_Relationships_Female',
                'prob_xtra_rel_male': 'Prob_Extra_Relationship_Male',
                'prob_xtra_rel_female': 'Prob_Extra_Relationship_Female'
            }
            library.set_concurrency_parameters(demographics=self.demographics,
                                               relationship_type=self.relationship_type,
                                               risk_group=self.risk_group,
                                               node_ids=[node_id],
                                               **new_values)
            result = society.get_concurrency_parameters_by_relationship_type_and_risk(relationship_type=self.relationship_type,
                                                                                      risk=self.risk_group).to_dict()

            # Ensure the specified relationship-risk combination of concurrency parameters have been changed
            for parameter, expected_value in new_values.items():
                mapped_parameter = result_mapping[parameter]
                self.assertEqual(expected_value, result[mapped_parameter])

            # Ensure that only the specified relationship-risk combination of concurrency parameters have been changed
            print("Verifying no unintentional changes occurred to other relationship/risk groups")
            result_all = society.to_dict()
            for relationship_type, result_by_rel_type in result_all.items():
                if relationship_type == 'Concurrency_Configuration':
                    continue  # This isn't a relationship type ...
                print(f"--- relationship_type: {relationship_type}")
                result_by_risk_group = result_by_rel_type.get('Concurrency_Parameters', None)
                if result_by_risk_group is not None:  # Non Default nodes may not have everything set by default.
                    for risk_group, result_concurrency_parameters in result_by_risk_group.items():
                        print(f"--- ---  risk_group: {risk_group}")
                        if relationship_type == self.relationship_type and risk_group == self.risk_group:
                            continue  # This is supposed to be different ...
                        # ensure all the ORIGINAL entries are unmodified in the new data
                        for parameter, expected_value in original_all[relationship_type]['Concurrency_Parameters'][risk_group].items():
                            print(f"--- --- --- parameter: {expected_value} vs {result_concurrency_parameters[parameter]}")
                            self.assertEqual(expected_value, result_concurrency_parameters[parameter])

    def test_set_pair_formation_parameters(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80*'-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)
            society = node.society
            original_all = society.to_dict()

            new_values = {
                'formation_rate': 0.12345,
                'risk_assortivity': 0.23456
            }
            result_mapping = {
                'formation_rate': 'Formation_Rate_Constant',
                'risk_assortivity': 'Assortivity'
            }
            library.set_pair_formation_parameters(demographics=self.demographics,
                                                  relationship_type=self.relationship_type,
                                                  node_ids=[node_id],
                                                  **new_values)
            result = society.get_pair_formation_parameters_by_relationship_type(relationship_type=self.relationship_type).to_dict()

            # Ensure the specified relationship-type pair formation parameters have been changed
            for parameter, expected_value in new_values.items():
                print(f"Parameter: {parameter}")
                mapped_parameter = result_mapping[parameter]
                if parameter == 'risk_assortivity':
                    expected_value = [[expected_value, 1 - expected_value, 0],
                                      [1 - expected_value, expected_value, expected_value],
                                      [0, expected_value, 1 - expected_value]]
                    res = result[mapped_parameter]['Weighting_Matrix_RowMale_ColumnFemale']
                else:
                    res = result[mapped_parameter]

                print(f"parameter: {expected_value} vs {res}")
                self.assertEqual(expected_value, res)

            # Ensure that only the specified relationship-type pair formation parameters have been changed
            print("Verifying no unintentional changes occurred to other relationship/risk groups")
            result_all = society.to_dict()
            for relationship_type, result_by_rel_type in result_all.items():
                if relationship_type == 'Concurrency_Configuration':
                    continue  # This isn't a relationship type ...
                print(f"--- relationship_type: {relationship_type}")
                pfp = result_by_rel_type.get('Pair_Formation_Parameters', None)
                if pfp is not None:  # Non Default nodes may not have everything set by default.
                    if relationship_type == self.relationship_type:
                        continue  # This is supposed to be different ...
                    # ensure all the ORIGINAL entries are unmodified in the new data
                    for parameter, expected_value in original_all[relationship_type]['Pair_Formation_Parameters'].items():
                        print(f"--- --- --- parameter: {expected_value} vs {pfp[parameter]}")
                        self.assertEqual(expected_value, pfp[parameter])

    def test_set_relationship_parameters(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80*'-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)
            society = node.society
            original_all = society.to_dict()

            new_values = {
                'coital_act_rate': 0.123,
                'condom_usage_min': 0.234,
                'condom_usage_mid': 0.345,
                'condom_usage_max': 0.456,
                'condom_usage_rate': 0.567,
                'duration_scale': 0.678,
                'duration_heterogeneity': 0.789
            }
            result_mapping = {
                'coital_act_rate': 'Coital_Act_Rate',
                'condom_usage_min': 'Min',
                'condom_usage_mid': 'Mid',
                'condom_usage_max': 'Max',
                'condom_usage_rate': 'Rate',
                'duration_scale': 'Duration_Weibull_Scale',
                'duration_heterogeneity': 'Duration_Weibull_Heterogeneity'
            }
            library.set_relationship_parameters(demographics=self.demographics,
                                                relationship_type=self.relationship_type,
                                                node_ids=[node_id],
                                                **new_values)
            result = society.get_relationship_parameters_by_relationship_type(relationship_type=self.relationship_type).to_dict()

            # Ensure the specified relationship-type relationship parameters have been changed
            for parameter, expected_value in new_values.items():
                print(f"Parameter: {parameter}")
                mapped_parameter = result_mapping[parameter]
                if parameter in ['condom_usage_min', 'condom_usage_mid', 'condom_usage_max', 'condom_usage_rate']:
                    res = result['Condom_Usage_Probability'][mapped_parameter]
                else:
                    res = result[mapped_parameter]

                print(f"parameter: {expected_value} vs {res}")
                self.assertEqual(expected_value, res)

            # Ensure that only the specified relationship-type relationship parameters have been changed
            print("Verifying no unintentional changes occurred to other relationship/risk groups")
            result_all = society.to_dict()
            for relationship_type, result_by_rel_type in result_all.items():
                if relationship_type == 'Concurrency_Configuration':
                    continue  # This isn't a relationship type ...
                print(f"--- relationship_type: {relationship_type}")
                rp = result_by_rel_type.get('Relationship_Parameters', None)
                if rp is not None:  # Non Default nodes may not have everything set by default.
                    if relationship_type == self.relationship_type:
                        continue  # This is supposed to be different ...
                    # ensure all the ORIGINAL entries are unmodified in the new data
                    for parameter, expected_value in original_all[relationship_type]['Relationship_Parameters'].items():
                        print(f"--- --- --- parameter: {expected_value} vs {rp[parameter]}")
                        self.assertEqual(expected_value, rp[parameter])

    def test_set_initial_risk_distribution(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80*'-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)

            new_values = {
                'initial_risk_distribution_low': 0.123
            }
            result_mapping = {
                'initial_risk_distribution_low': 'Initial_Distribution'
            }
            library.set_initial_risk_distribution(demographics=self.demographics,
                                                  node_ids=[node_id],
                                                  **new_values)
            result = node.get_individual_property(property_key='Risk').to_dict()

            # Ensure the specified distribution has been changed
            for parameter, expected_value in new_values.items():
                print(f"Parameter: {parameter}")
                mapped_parameter = result_mapping[parameter]
                if parameter == 'initial_risk_distribution_low':
                    expected_value = [expected_value, (1 - expected_value), 0]
                res = result[mapped_parameter]

                print(f"parameter: {expected_value} vs {res}")
                self.assertEqual(expected_value, res)

    def test_set_initial_cascade_state_distribution(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80 * '-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)

            new_values = {
                'cascade_state_distribution': [0.1, 0.2, 0.3, 0.4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            }
            result_mapping = {
                'cascade_state_distribution': 'Initial_Distribution'
            }
            library.set_initial_cascade_state_distribution(demographics=self.demographics,
                                                           node_ids=[node_id],
                                                           **new_values)
            result = node.get_individual_property(property_key='CascadeState').to_dict()

            # Ensure the specified distribution has been changed
            for parameter, expected_value in new_values.items():
                print(f"Parameter: {parameter}")
                mapped_parameter = result_mapping[parameter]
                res = result[mapped_parameter]

                print(f"parameter: {expected_value} vs {res}")
                self.assertEqual(expected_value, res)

    def test_set_initial_health_care_accessibility_distribution(self):
        # Testing on the Default node and an arbitrary other node
        for node_id in [None, 1]:
            print(f"{80 * '-'}\nNODE ID: {node_id}")
            node = self.demographics.get_node_by_id(node_id=node_id)

            new_values = {
                'initial_accessibility': 0.123456789
            }
            result_mapping = {
                'initial_accessibility': 'Initial_Distribution'
            }
            library.set_initial_health_care_accessibility_distribution(demographics=self.demographics,
                                                                       node_ids=[node_id],
                                                                       **new_values)
            result = node.get_individual_property(property_key='Accessibility').to_dict()

            # Ensure the specified distribution has been changed
            for parameter, expected_value in new_values.items():
                print(f"Parameter: {parameter}")
                mapped_parameter = result_mapping[parameter]
                if parameter == 'initial_accessibility':
                    expected_value = [expected_value, (1 - expected_value)]
                res = result[mapped_parameter]

                print(f"parameter: {expected_value} vs {res}")
                self.assertEqual(expected_value, res)

    @pytest.mark.skip(reason='Waiting for new data file format')
    def test_set_fertility(self):
        # TODO: need a test to cover setting fertility data
        raise NotImplementedError('')

    @pytest.mark.skip(reason='Waiting for new data file format')
    def test_set_mortality(self):
        # TODO: need a test to cover setting mortality data
        raise NotImplementedError('')

    @pytest.mark.skip(reason='Waiting for new data file format')
    def test_set_age_distribution(self):
        # TODO: need a test to cover setting age distribution data
        raise NotImplementedError('')


if __name__ == '__main__':
    unittest.main()
