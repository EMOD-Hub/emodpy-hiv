import unittest
from unittest import TestSuite

import sys
from pathlib import Path
parent = Path(__file__).resolve().parent
sys.path.append(str(parent))

test_cases_to_run_first = ['test_emod_hiv_package.TestDownloadFromPackage']


class CustomizeTestOrder(unittest.TestCase):
    """
    This class is used to customize the order of the tests in the test suite.
    """
    pass


def customize_load_tests(loader, standard_tests, pattern):
    """
    Customize how tests are loaded from them during normal test runs or test discovery.
    The first test case to run is specified in test_cases_to_run_first then the rest of the test cases followed the default order.
    See load_tests Protocol in: https://docs.python.org/3.7/library/unittest.html#load-tests-protocol
    """
    suite = TestSuite()
    for test_cases in test_cases_to_run_first:
        tests = loader.loadTestsFromName(name=test_cases)
        suite.addTests(tests)
        while tests in standard_tests:
            standard_tests._tests.remove(tests)
    suite.addTests(standard_tests)
    return suite


load_tests = customize_load_tests


if __name__ == '__main__':
    unittest.main()
