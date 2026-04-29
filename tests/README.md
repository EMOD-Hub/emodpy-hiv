# emodpy-hiv Tests

How to run these tests after installing emodpy-hiv.

## Prerequisites

- Python 3.13 (also supports 3.10–3.14)
- A virtual environment with emodpy-hiv installed

## Installation

Install the package with test dependencies from the repo root:

```bash
pip install -e ".[test]"
```

## Running Tests

### Unit tests (no EMOD execution required)

```bash
pytest -m unit
```

### Import/package tests

```bash
pytest unittests/test_emod_hiv_package.py
```

### Simulation tests (requires Docker for ContainerPlatform)

```bash
pytest -m container
```

### Country-specific tests

```bash
pytest -m country
```

Or for a specific country:

```bash
pytest tests/countries/zambia
```

### All tests in parallel

```bash
pytest -n auto
```

### ContainerPlatform requirements

- Docker installed and running
- **Windows only**: Enable WSL2 backend in Docker Desktop, enable Developer Mode (`Settings → Update & Security → For developers`), and enable long file path support via Group Policy Editor ([Microsoft guide](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation))

See the [Docker installation guide](https://docs.docker.com/get-docker/) and [ContainerPlatform docs](https://github.com/EMOD-Hub/idmtools/tree/main/idmtools_platform_container) for more details.

## Country Tests

For prerequisites, platform configuration, and instructions on adding new country tests, see [countries/README.md](countries/README.md).
