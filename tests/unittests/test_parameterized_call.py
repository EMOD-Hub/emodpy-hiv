import unittest
import pytest
from emodpy_hiv.parameterized_call import ParameterizedCall


def dummy_function(a=1, b=2, c=3, d=4):
    return {'a': a, 'b': b, 'c': c, 'd': d}


@pytest.mark.unit
class TestParameterizedCall(unittest.TestCase):

    def setUp(self):
        self.label = 'dummy_label'
        pass

    def tearDown(self):
        pass

    def test_properly_distributes_nhp_and_hp(self):
        # no hp or nhp
        pc = ParameterizedCall(func=dummy_function)
        self.assertEqual({}, pc.hyperparameters)
        self.assertEqual({}, pc._non_hyperparameters)

        # setting some of both
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 0, 'b': 0}, non_hyperparameters={'c': 0})
        self.assertEqual(['a', 'b'], list(pc.hyperparameters.keys()))
        self.assertEqual(['c'], list(pc._non_hyperparameters.keys()))

    def test_ensure_label_hyperparameter_works_properly(self):
        # ensure no label is used if not specified
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 0})
        self.assertEqual(None, pc.label)
        self.assertEqual("", pc._label_str)

        # ensure proper labeling occurs for hyperparameters if a label is given
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 0}, label=self.label)
        self.assertEqual(self.label, pc.label)
        self.assertEqual(f"--{self.label}", pc._label_str)

    def test_ensure_labeled_hyperparameters_works_properly(self):
        # ensure no label is used if not specified
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 0})
        self.assertEqual(1, len(pc.labeled_hyperparameters))
        self.assertEqual('a', list(pc.labeled_hyperparameters.keys())[0])

        # ensure proper labeling occurs for hyperparameters if a label is given
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 0}, label=self.label)
        self.assertEqual(1, len(pc.labeled_hyperparameters))
        self.assertEqual(f'a--{self.label}', list(pc.labeled_hyperparameters.keys())[0])

    def test_set_labeled_hyperparameter_works(self):
        # no labels testing
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 10, 'b': 20})
        pc.set_labeled_hyperparameter(labeled_hyperparameter='a', value=100)
        self.assertEqual({'a': 100, 'b': 20}, pc.labeled_hyperparameters)
        # verify error raised if invalid hyperparameter is specified
        self.assertRaises(ValueError, pc.set_labeled_hyperparameter, labeled_hyperparameter=f'a--{self.label}', value=0)
        self.assertRaises(ValueError, pc.set_labeled_hyperparameter, labeled_hyperparameter='xyz', value=0)

        # with labels
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 10, 'b': 20}, label=self.label)
        pc.set_labeled_hyperparameter(labeled_hyperparameter=f'a--{self.label}', value=100)
        self.assertEqual({f'a--{self.label}': 100, f'b--{self.label}': 20}, pc.labeled_hyperparameters)
        # verify error raised if invalid hyperparameter and/or label is specified.
        # missing label
        self.assertRaises(ValueError, pc.set_labeled_hyperparameter, labeled_hyperparameter='a', value=0)
        # xyz is a unknown hp
        self.assertRaises(ValueError, pc.set_labeled_hyperparameter, labeled_hyperparameter=f'xyz--{self.label}', value=0)
        # known hp, but unknown label
        self.assertRaises(ValueError, pc.set_labeled_hyperparameter, labeled_hyperparameter='a--BADLABEL', value=0)

    def test_verify_value_overriding_behavior(self):
        # precendence order: 1) value set on the pc, 2) value set on the pc when initializing, 3) func default
        # This is the order of precendence for passing of values to the ParameterizedCall func.
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 10, 'b': 20, 'c': None, 'd': None})
        pc.set_labeled_hyperparameter(labeled_hyperparameter='a', value=100)
        pc.set_labeled_hyperparameter(labeled_hyperparameter='c', value=300)
        call = pc.prepare_call()
        result = call()  # Note that the pc function, dummy_function, just returns the resolved value of its params
        self.assertEqual({'a': 100, 'b': 20, 'c': 300, 'd': 4}, result)

        # just to be sure, trying with a label now. The pc func doesn't know about the label, so the assert leaves
        # it out
        pc = ParameterizedCall(func=dummy_function, hyperparameters={'a': 10, 'b': 20, 'c': None, 'd': None},
                               label=self.label)
        pc.set_labeled_hyperparameter(labeled_hyperparameter=f'a--{self.label}', value=100)
        pc.set_labeled_hyperparameter(labeled_hyperparameter=f'c--{self.label}', value=300)
        call = pc.prepare_call()
        result = call()  # Note that the pc function, dummy_function, just returns the resolved value of its params
        self.assertEqual({'a': 100, 'b': 20, 'c': 300, 'd': 4}, result)


if __name__ == '__main__':
    unittest.main()
