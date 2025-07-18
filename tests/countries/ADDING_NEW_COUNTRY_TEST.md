# 🌍 Adding a New Country Test

This guide explains how to develop and validate tests for a new country class in the `emodpy-hiv` project.

---

## 1. Overview

Assume you have created a new country class (e.g., `ZambiaPrepAtDebut`) by subclassing the existing Zambia country class. You have modified:
- Demographics: different population distribution
- Campaign: different `HCTUptakeAtDebut` Cascade of care state
- Reporters: additional report

Follow these steps to create and validate tests for your new class.

---

## 2. Create a Test Folder

- Copy the existing test folder (e.g., `zambia`) in `tests/countries/`.
- Rename the copied folder to match your new country class (e.g., `zambia_prep_at_debut`).

---

## 3. Update Test Files

There are four test files in the folder:
- `test_zambia.py`: Runs the simulation, checks completion, and validates output files/reports.
- `test_zambia_campaign.py`: Validates campaign file generation against a reference.
- `test_zambia_demographics.py`: Validates demographics file generation against a reference.
- `test_zambia_config.py`: Validates config file generation against a reference.

**Steps:**
- Rename each file to reflect the new country class (e.g., `test_zambia_prep_at_debut.py`).
- Update import statements to use your new country class.
- Change test class and function names accordingly.
- Replace all references to the old country class with the new one.

**Example: `test_zambia_prep_at_debut.py`**
```python
import emodpy_hiv.countries.zambia.zambia as cm
# becomes
import emodpy_hiv.countries.zambia_prep_at_debut.zambia_prep_at_debut as cm

class TestZambia(BaseSimTest):
    def test_zambia(self):
        zambia = cm.Zambia
# becomes
class TestZambiaPrepAtDebut(BaseSimTest):
    def test_zambia_prep_at_debut(self):
        zambia_prep_at_debut = cm.ZambiaPrepAtDebut
```
Update all references from zambia to zambia_prep_at_debut in the test functions.

---

## 4. Prepare Reference Files
Assume you run a simulation using the new country class and you are able to get the expected results. You can use the output files from the simulation run as reference files for the new test.
Here are the steps to prepare the reference files using the `test_zambia_prep_at_debut.py` test file:(You can write a script to do this too)

- Comment out all lines that validate the simulation result for now (e.g., all lines after `self.assertTrue(experiment.succeeded, ...)`).
- Run the test to ensure it executes without errors and generates output files.
```bash
pytest tests/countries/zambia_prep_at_debut/test_zambia_prep_at_debut.py
```
- Inspect output files (e.g., `InsetChart.json`) to verify the new country class works as expected.
- Copy `InsetChart.json` from the simulation output folder to `tests/countries/zambia_prep_at_debut/inputs` and rename it to `test_zambia_prep_at_debut_InsetChart.json`.
- Copy campaign, demographics, and config reference files from the simulation output folder to the new test folder's `inputs` subdirectory, renaming them to match reference filenames in the campaign, demographics and config tests.

---

## 5. Update Validation Logic
- Uncomment or update validation lines in `test_zambia_prep_at_debut.py` to check for expected results.
- Adjust expected filenames and report names to match your new country class.
- Add extra validation checks for new features (e.g., population distribution, campaign states, additional reports).
For demographics tests, keep the `test_demographics()` function and remove any Zambia-specific tests (e.g., `test_demographics_v2()`) that do not apply.

---

## 6. Run and Verify Tests
- Run all tests for your new country class:
```bash
pytest tests/countries/zambia_prep_at_debut
```
You can also run individual test files to isolate issues:
```bash
pytest tests/countries/zambia_prep_at_debut/test_zambia_prep_at_debut.py
```
Ensure all tests pass and outputs match expectations.

---

## 7. Tips
- Update and test each file individually to isolate issues. Repeat steps 3 to 6 for each file, but note that step 4 (preparing reference files) only needs to be done once after running the simulation.
- Remove or update any Zambia-specific tests that do not apply to your new country class.
- Add comments to highlight changes and custom validations.
- You can add more validation checks to test specific changes, such as population distribution in the demographics file or cascade of care states in the campaign file.
- `pytest` markers can be used to categorize tests (e.g., `@pytest.mark.country`, `@pytest.mark.container`). You can run tests with specific markers using `pytest -m <marker>`.

---

For more details on the test structure, see the main [README.md](README.md).

