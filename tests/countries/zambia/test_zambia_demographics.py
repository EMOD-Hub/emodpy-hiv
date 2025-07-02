import unittest
import pytest
from pathlib import Path
import sys
import json
import os

from emodpy_hiv.countries.zambia import Zambia

manifest_directory = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(manifest_directory))

parent = Path(__file__).resolve().parent

import helpers

ROUNDING_DIGITS = 9

@pytest.mark.unit
class TestZambiaDemographics(unittest.TestCase):
    def setUp(self):
        output_path = Path(__file__).parent.joinpath("outputs")
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.zambia = Zambia
        print(f"running test: {self._testMethodName}")

    def tearDown(self):
        pass

    def load_json(self, file_path):
        """Load JSON data from a file."""
        with open(file_path, 'r') as file:
            return json.load(file)

    def test_demographics(self):
        filename_exp = Path(__file__).parent.joinpath('inputs/test_zambia_demographics.json')
        filename_act = Path(__file__).parent.joinpath('outputs', "test_demographics_actual.json")

        demog = self.zambia.build_demographics()
        act_demog_json = demog.to_dict()
        with open(filename_act,"w") as file:
            # This process of writing and reading and writing allows us to write a file where
            # the floating point values are rounded to 9 digits. This helps us not have rounding
            # issues between different platforms.
            tmp = json.dumps(act_demog_json, indent=4, sort_keys=True)
            tmp = json.loads(tmp, parse_float=lambda x: round(float(x), 9))
            json.dump(tmp,file,indent=4,sort_keys=True,)
        exp_demog_json = self.load_json(filename_exp)
        act_demog_json = self.load_json(filename_act)
    
        # erase the date so we don't compare that
        exp_demog_json["Metadata"]["DateCreated"] = ""
        act_demog_json["Metadata"]["DateCreated"] = ""
        exp_demog_json["Metadata"]["Author"     ] = ""
        act_demog_json["Metadata"]["Author"     ] = ""
    
        self.assertDictEqual(exp_demog_json, act_demog_json,
                             "The actual demographics for Zambia are different than expected.")
        helpers.delete_existing_file(filename_act)

    def test_demographics_v2(self):
        demographics = self.zambia.build_demographics()
        # age_simple (default), age_complex (override), fertility_age_year, _set_enable_natural_mortality,
        # mortality_age_gender_year, AddIndividualPropertyAndHINT (one for each node, so 10)
        self.assertEqual(len(demographics.implicits), 15)
        self.assertEqual(len(demographics.migration_files), 0)

        # load the source demographics file for regression checking
        regression_file = Path(parent, 'inputs', 'Demographics--zambia_regression.json')
        with open(regression_file, 'rb') as f:
            expected = json.load(f)

        # --------------------
        # --- SAVE DEBUG CODE
        # --------------------
        # with open("generated_zambia_demog.json","w") as f:
        #     demog_dict = demographics.to_dict()
        #     json.dump( demog_dict, f )

        # ----------------------------------------
        # --- check important per-node information
        # ----------------------------------------
        self.assertEqual(len(demographics.nodes), len(expected['Nodes']))

        expected_nodes_by_id = {node_dict['NodeID']: node_dict for node_dict in expected['Nodes']}
        for node in demographics.nodes:
            expected_node = expected_nodes_by_id[node.id]
            self.assertEqual(node.id, expected_node['NodeID'])
            self.assertEqual(node.name, expected_node['NodeName'])
            self.assertEqual(node.pop, expected_node['NodeAttributes']['InitialPopulation'])

            # -------------------------------------------------------------------------
            # --- ensure the expected IPs are set (for zambia, Risk is on each node
            # --- because they have a different LOW distribution.
            # -------------------------------------------------------------------------
            self.assertEqual(len(node.individual_properties),3)
            self.assertEqual(len(node.individual_properties),len(expected_node['IndividualProperties']))
            expected_ips_by_key = {ip_dict['Property']: ip_dict for ip_dict in expected_node['IndividualProperties']}
            for ip in node.individual_properties:
                expected_ip = expected_ips_by_key[ip.property]
                self.assertEqual(ip.property, expected_ip['Property'])
                self.assertEqual(ip.values, expected_ip['Values'])
                self.assertEqual(len(ip.initial_distribution), len(expected_ip['Initial_Distribution']))
                for i in range(len(expected_ip['Values'])):
                    self.assertAlmostEqual(ip.initial_distribution[i], expected_ip['Initial_Distribution'][i], places=ROUNDING_DIGITS)
                transitions = [] if ip.transitions is None else ip.transitions
                self.assertEqual(transitions, expected_ip.get('Transitions', []))
                transmission_matrix = [] if ip.transmission_matrix is None else ip.transmission_matrix
                self.assertEqual(transmission_matrix, expected_ip.get('TransmissionMatrix', []))

        # -------------------------------------
        # --- verify fertility data is the same
        # -------------------------------------
        expected_fertility = expected['Defaults']['IndividualAttributes']['FertilityDistribution']
        fertility = demographics.default_node.individual_attributes.fertility_distribution
        self.assertEqual(fertility._axis_names(), expected_fertility['AxisNames'])
        self.assertEqual(fertility._axis_scale_factors(), expected_fertility['AxisScaleFactors'])
        self.assertEqual(fertility._rate_scale_units(), expected_fertility['ResultUnits'])
        self.assertAlmostEqual(fertility._rate_scale_factor(), expected_fertility['ResultScaleFactor'],
                               places=ROUNDING_DIGITS)

        self.assertEqual(len(fertility._population_groups), len(expected_fertility['PopulationGroups']))
        self.assertEqual(len(fertility._population_groups[0]), len(expected_fertility['PopulationGroups'][0]))
        self.assertEqual(len(fertility._population_groups[1]), len(expected_fertility['PopulationGroups'][1]))
        for j in range(2):
            for i in range(len(fertility._population_groups[j])):
                act_val = fertility._population_groups[j][i]
                exp_val = expected_fertility['PopulationGroups'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        for j in range(len(fertility._population_groups[0])):
            for i in range(len(fertility._population_groups[1])):
                act_val = fertility.pregnancy_rate_matrix[j][i]
                exp_val = expected_fertility['ResultValues'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        # -----------------------------------
        # --- female mortality data is the same
        # -----------------------------------        
        exp_female_mortality = expected['Defaults']['IndividualAttributes']['MortalityDistributionFemale']
        act_female_mortality = demographics.default_node.individual_attributes.mortality_distribution_female
        self.assertEqual(act_female_mortality._axis_names(), exp_female_mortality['AxisNames'])
        self.assertEqual(act_female_mortality._axis_scale_factors(), exp_female_mortality['AxisScaleFactors'])
        self.assertEqual(act_female_mortality._rate_scale_units(), exp_female_mortality['ResultUnits'])
        self.assertAlmostEqual(act_female_mortality._rate_scale_factor(), exp_female_mortality['ResultScaleFactor'],
                               places=ROUNDING_DIGITS)

        self.assertEqual( 2,                                              len(exp_female_mortality['PopulationGroups']   )) # noqa: E241
        self.assertEqual(len(act_female_mortality._population_groups), len(exp_female_mortality['PopulationGroups']))
        self.assertEqual(len(act_female_mortality._population_groups[0]), len(exp_female_mortality['PopulationGroups'][0]))
        self.assertEqual(len(act_female_mortality._population_groups[1]), len(exp_female_mortality['PopulationGroups'][1]))

        for j in range(2):
            for i in range(len(act_female_mortality._population_groups[j])):
                act_val = act_female_mortality._population_groups[j][i]
                exp_val = exp_female_mortality['PopulationGroups'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        for j in range(len(act_female_mortality._population_groups[0])):
            for i in range(len(act_female_mortality._population_groups[1])):
                act_val = act_female_mortality.mortality_rate_matrix[j][i]
                exp_val = exp_female_mortality['ResultValues'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        # --------------------
        # --- SAVE DEBUG CODE
        # --------------------
        # with open("zambia_old_mortality_female.csv", "w") as file:
        #     file.write("node_id,min_year,min_age,rate\n")
        #     for y in range(len(exp_female_mortality['PopulationGroups'][1])):
        #         for a in range(len(exp_female_mortality['PopulationGroups'][0])):
        #             if (a % 2) != 0: # skip odd ages
        #                 continue
        #             rate = exp_female_mortality['ResultValues'][a][y]
        #             age  = exp_female_mortality['PopulationGroups'][0][a]
        #             year = exp_female_mortality['PopulationGroups'][1][y]
        #             line = f"0,{year},{age},{rate}\n"
        #             file.write( line )

        # -----------------------------------
        # --- Male mortality data is the same
        # -----------------------------------        
        exp_male_mortality = expected['Defaults']['IndividualAttributes']['MortalityDistributionMale']
        act_male_mortality = demographics.default_node.individual_attributes.mortality_distribution_male
        self.assertEqual(act_male_mortality._axis_names(), exp_male_mortality['AxisNames'])
        self.assertEqual(act_male_mortality._axis_scale_factors(), exp_male_mortality['AxisScaleFactors'])
        self.assertEqual(act_male_mortality._rate_scale_units(), exp_male_mortality['ResultUnits'])
        self.assertAlmostEqual(act_male_mortality._rate_scale_factor(), exp_male_mortality['ResultScaleFactor'],
                               places=ROUNDING_DIGITS)

        self.assertEqual( 2,                                            len(exp_male_mortality['PopulationGroups']   )) # noqa: E241
        self.assertEqual(len(act_male_mortality._population_groups), len(exp_male_mortality['PopulationGroups']))
        self.assertEqual(len(act_male_mortality._population_groups[0]), len(exp_male_mortality['PopulationGroups'][0]))
        self.assertEqual(len(act_male_mortality._population_groups[1]), len(exp_male_mortality['PopulationGroups'][1]))

        for j in range(2):
            for i in range(len(act_male_mortality._population_groups[j])):
                act_val = act_male_mortality._population_groups[j][i]
                exp_val = exp_male_mortality['PopulationGroups'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        for j in range(len(act_male_mortality._population_groups[0])):
            for i in range(len(act_male_mortality._population_groups[1])):
                act_val = act_male_mortality.mortality_rate_matrix[j][i]
                exp_val = exp_male_mortality['ResultValues'][j][i]
                self.assertAlmostEqual( exp_val, act_val, delta=0.000001)

        # ---------------------------------------------
        # --- verify the age distributions are the same
        # ---------------------------------------------
        expected_age_distribution = expected['Defaults']['IndividualAttributes']['AgeDistribution']
        age_distribution = demographics.default_node.individual_attributes.age_distribution

        self.assertAlmostEqual(age_distribution._rate_scale_factor(), expected_age_distribution['ResultScaleFactor'],
                               places=ROUNDING_DIGITS)
        self.assertEqual(expected_age_distribution['ResultValues'], age_distribution.ages_years)
        self.assertEqual( len(expected_age_distribution['DistributionValues']),
                          len(age_distribution.cumulative_population_fraction))
        for i in range(len(expected_age_distribution['DistributionValues'])):
            exp_val = expected_age_distribution['DistributionValues'][i]
            act_val = age_distribution.cumulative_population_fraction[i]
            self.assertAlmostEqual(exp_val, act_val, delta=0.000002)


if __name__ == '__main__':
    unittest.main()
