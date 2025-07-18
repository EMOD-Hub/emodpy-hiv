# Countries Tests for emodpy-hiv

This module provides a framework and examples for running country-specific tests using `pytest` within the `emodpy-hiv` project.

---
## Contents

- [Prerequisites](#-prerequisites)
- [Platform Configuration](#️-platform-configuration)
  - [Extra Steps for ContainerPlatform](#-extra-steps-for-containerplatform)
      - [Extra Steps for Windows Users](#-extra-steps-for-windows-users)
- [Running the Tests](#-running-the-tests)
- [Adding a New Country Test](./ADDING_NEW_COUNTRY_TEST.md)
---

## 📦 Prerequisites

To get started, follow these steps:

1. **Install the main package**:
   Follow the setup instructions in the main `README.md` of the `emodpy-hiv` repository. This typically involves:
   - Creating a virtual environment
   - Installing the package in editable mode
   - Installing required dependencies

2. **Install test dependencies**:
   Navigate to the `tests/` directory and install additional packages:

   ```bash
   pip install -r requirements.txt
   ```

---

## ⚙️ Platform Configuration

If you wish to run tests on **CompsPlatform** instead of the default **ContainerPlatform**, modify the line in `base_sim_test.py`:

**Change:**

```python
self.platform = Platform(manifest.container_platform_name, job_directory="container_jobs")
```

**To:**

```python
self.platform = Platform(manifest.comps_platform_name)
```

> ℹ️ We recommend using `ContainerPlatform` to avoid needing a Comps account or access credentials.

---

### 🪟 Extra Steps for ContainerPlatform

If you're running tests on **ContainerPlatform**, follow these additional setup steps:
1. **Docker Requirements**
   - Install Docker on your machine.
   - Enable **WSL2 backend** in Docker settings (only for Windows users)
   - Make sure Docker is running

   See the [Docker Installation Guide](https://docs.docker.com/get-docker/) and [ContainerPlatform Docs](https://github.com/InstituteforDiseaseModeling/idmtools/tree/main/idmtools_platform_container) for details.

#### Extra steps for Windows users:

1. **Enable Developer Mode**  
   Go to: `Settings` → `Update & Security` → `For developers` → Turn on **Developer Mode**.

2. **Enable Long File Path Support(Optional if you did not get error with length limit)**  
   Windows has a default file path length limit of 255 characters. Enable long path support via Group Policy Editor.  
   [Microsoft's guide](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation)

---


## 🧪 Running the Tests

The default execution platform is `ContainerPlatform`. If Docker is installed, this will allow you to run tests in a self-contained environment.

### ➤ Run all country tests

```bash
pytest --dist loadfile -v -m country
```

### ➤ Run tests for a specific country (e.g., Zambia)

```bash
pytest tests/countries/zambia
```

### ➤ Run specific test using pytest with the test file path

```bash
pytest tests/countries/zambia/test_zambia.py
```

---


## 🌍 Adding a New Country Test

See [ADDING_NEW_COUNTRY_TEST.md](./ADDING_NEW_COUNTRY_TEST.md) for detailed instructions.
