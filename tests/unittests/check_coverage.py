import coverage
import unittest

from test_demographics import HIVDemographicsTest
from test_import import HIVTestImports
from test_intervention import HIVInterventionTest

loader = unittest.TestLoader()
cov = coverage.Coverage(source=[
    "emodpy_hiv.interventions",
    "emodpy_hiv.demographics"])
cov.start()

# First, load and run the unittest tests
test_classes_to_run = [HIVDemographicsTest,
                       HIVTestImports,
                       HIVInterventionTest,
                       ]

suites_list = []
for tc in test_classes_to_run:
    suite = loader.loadTestsFromTestCase(tc)
    suites_list.append(suite)
    pass

big_suite = unittest.TestSuite(suites_list)
runner = unittest.TextTestRunner()
results = runner.run(big_suite)

cov.stop()
cov.save()
cov.html_report()
