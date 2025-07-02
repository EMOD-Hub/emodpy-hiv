import unittest
import pytest

@pytest.mark.unit
class HIVTestImports(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_items = None
        self.found_items = None
        print(f"running test: {self._testMethodName}:")
        pass

    def verify_expected_items_present(self, namespace):
        self.found_items = dir(namespace)
        for item in self.expected_items:
            self.assertIn(
                item,
                self.found_items
            )

    def tearDown(self) -> None:
        pass

    def test_requirements(self):
        import emod_api
        import emodpy_hiv
        import emodpy
        # Testing that we can import all requirements
        checks = [dir(package) for package in [emod_api, emodpy_hiv, emodpy]]
        for package in checks:
            self.assertIn('__package__', package)
        return

    # region demographics
    def test_demographics_imports(self):
        from emodpy_hiv.demographics.hiv_demographics import HIVDemographics

        self.expected_items = [
            "from_template_node", "from_population_dataframe"
        ]
        self.verify_expected_items_present(namespace=HIVDemographics)

    def test_demographics_template_imports(self):
        import emodpy_hiv.demographics.DemographicsTemplates as DemographicsTemplates

        self.expected_items = [
            "get_society_dict"
        ]
        self.verify_expected_items_present(namespace=DemographicsTemplates)

    # endregion


if __name__ == '__main__':
    unittest.main()
