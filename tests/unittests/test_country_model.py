import unittest
from typing import List

from emodpy_hiv.country_model import Country
from emodpy_hiv.demographics.hiv_demographics import HIVDemographics
from emodpy_hiv.parameterized_call import ParameterizedCall


class MockDemographics(HIVDemographics):
    def __init__(self):
        # defaults
        self.test_parameter1 = 1
        self.test_parameter2 = 2
        self.test_parameter3 = 3
        self.test_parameter4 = 4
        self.test_parameter5 = 5
        self.test_parameter6 = 6


class MockCountry(Country):
    # TODO: we currently do not instantiate country model objects. However, we MAY support this pattern in the furture
    #  so we're adding a test that indicates that ParameterizedCall usage currently supports it.
    def __init__(self):
        pass

    @classmethod
    def initialize_demographics(cls) -> MockDemographics:
        demographics = MockDemographics()
        return demographics

    def set_test_parameter1_via_instance_method(self, demographics, test_parameter1: int = None):
        if test_parameter1 is not None:
            demographics.test_parameter1 = test_parameter1

    @classmethod
    def set_test_parameter2_via_class_method(cls, demographics, test_parameter2: int = None):
        if test_parameter2 is not None:
            demographics.test_parameter2 = test_parameter2

    @staticmethod
    def set_test_parameter3_via_static_method(demographics, test_parameter3: int = None):
        if test_parameter3 is not None:
            demographics.test_parameter3 = test_parameter3

    def set_test_parameter4_via_instance_method(self, demographics, test_parameter4: int = None):
        if test_parameter4 is not None:
            demographics.test_parameter4 = test_parameter4

    @classmethod
    def set_test_parameter5_via_class_method(cls, demographics, test_parameter5: int = None):
        if test_parameter5 is not None:
            demographics.test_parameter5 = test_parameter5

    @staticmethod
    def set_test_parameter6_via_static_method(demographics, test_parameter6: int = None):
        if test_parameter6 is not None:
            demographics.test_parameter6 = test_parameter6


    @classmethod
    def get_demographics_parameterized_calls(cls, demographics: MockDemographics) -> List[ParameterizedCall]:
        parameterized_calls = []
        country_model = MockCountry()  # for instance method testing

        #
        # Three PCs with a hyperparamteter that does NOT override the existing default value
        #

        pc = ParameterizedCall(func=country_model.set_test_parameter1_via_instance_method,
                               hyperparameters={'test_parameter1': None})
        parameterized_calls.append(pc)
        pc = ParameterizedCall(func=cls.set_test_parameter2_via_class_method,
                               hyperparameters={'test_parameter2': None})
        parameterized_calls.append(pc)
        pc = ParameterizedCall(func=cls.set_test_parameter3_via_static_method,
                               hyperparameters={'test_parameter3': None})
        parameterized_calls.append(pc)

        #
        # Three PCs with a hyperparamteter that DO override the existing default value
        #

        pc = ParameterizedCall(func=country_model.set_test_parameter4_via_instance_method,
                               hyperparameters={'test_parameter4': 44})
        parameterized_calls.append(pc)
        pc = ParameterizedCall(func=cls.set_test_parameter5_via_class_method,
                               hyperparameters={'test_parameter5': 55})
        parameterized_calls.append(pc)
        pc = ParameterizedCall(func=cls.set_test_parameter6_via_static_method,
                               hyperparameters={'test_parameter6': 66})
        parameterized_calls.append(pc)

        return parameterized_calls


class TestParameterizedCall(unittest.TestCase):

    def test_instance_and_functional_parameterized_call_functions_work(self):
        demographics = MockCountry.build_demographics()

        # PC func default values expected from these
        self.assertEqual(1, demographics.test_parameter1)
        self.assertEqual(2, demographics.test_parameter2)
        self.assertEqual(3, demographics.test_parameter3)

        # PC default override values expected from these
        self.assertEqual(44, demographics.test_parameter4)
        self.assertEqual(55, demographics.test_parameter5)
        self.assertEqual(66, demographics.test_parameter6)


if __name__ == '__main__':
    unittest.main()
