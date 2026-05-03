# Tutorial 1: Run a simulation

This tutorial introduces the key components of emodpy-hiv by running a baseline HIV simulation
using the built-in Zambia country model. The simulation creates three runs with different random
seeds, using Docker to run EMOD locally.

**File:** `tutorials/tutorial_1_intro.py`

## Obtaining the EMOD executable

The `if __name__ == "__main__"` block calls `emod_hiv.bootstrap.setup()` before running the
experiment. This extracts the EMOD executable and schema from the `emod_hiv` package (installed
with emodpy-hiv) into the `tutorials/executables/` directory.

```python
import emod_hiv.bootstrap as dtk
dtk.setup(local_dir=manifest.executables_dir)
```

Paths used throughout the tutorials are defined in `manifest.py`.

## Country model

emodpy-hiv includes built-in country models that package the data and code needed to model a
specific country's HIV epidemic. This tutorial uses `ZambiaForTraining`, a simplified version
of the Zambia model.

The country model provides three build functions used to construct each simulation:

| Function | Purpose |
|----------|---------|
| `build_config(config)` | Sets simulation-wide configuration parameters |
| `build_campaign(campaign)` | Defines the care cascade and interventions |
| `build_demographics()` | Sets up the initial population, mortality, fertility, and relationship parameters |

## Platform

The `Platform` specifies where the simulations run. The tutorial file includes commented-out
configurations for all three supported platform types — uncomment the one that matches your
environment:

```python
# Container platform — runs EMOD in a Docker container on your local machine
platform = Platform('Container', job_directory="tutorial_output", docker_image=manifest.plat_image)

# COMPS platform — runs on IDM's COMPS cluster
# platform = Platform("Calculon", node_group="idm_48cores", priority="Normal")

# SLURM platform — runs on a local SLURM cluster
# platform = Platform("SLURM_LOCAL",
#                     job_directory="experiments",
#                     time="02:00:00",
#                     partition="cpu_short",
#                     mail_user="XXX@YYY.org",
#                     ...)
```

## EMODTask

`EMODTask.from_defaults()` assembles the simulation task from the country model's build
functions and the paths to the EMOD executable and schema:

```python
zambia = cm.ZambiaForTraining
task = emod_task.EMODTask.from_defaults(
    eradication_path=manifest.eradication_path,
    schema_path=manifest.schema_file,
    config_builder=zambia.build_config,
    campaign_builder=zambia.build_campaign,
    demographics_builder=zambia.build_demographics)
```

## Sweeping parameters

`SimulationBuilder` creates multiple simulations by sweeping a parameter across a list of
values. The `sweep_run_number` function sets `Run_Number`, which is the random seed. Sweeping
it produces statistically independent realizations of the same scenario:

```python
def sweep_run_number(simulation, value):
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}

builder = SimulationBuilder()
builder.add_sweep_definition(sweep_run_number, [1, 2, 3])
```

This creates three simulations, each with a different `Run_Number`.

## Running the experiment

The experiment is created from the builder and task, then run:

```python
experiment = Experiment.from_builder(builder, task, name="Tutorial_1")
experiment.run(wait_until_done=True, platform=platform)
```

`wait_until_done=True` causes Python to pause at this line until all simulations finish.

When using the Container platform, simulations run inside `tutorial_output/`. Inside that
directory you will find an experiment folder named after the experiment and its unique ID, for
example:

```
tutorial_output/
  e_Tutorial_1_949f773e-d09e-4212-80b3-3e7c10a4e16c/
    551dfe56-f2f8-4831-9f15-b7c0ac529557/   ← simulation 1
    7a3c9d12-e4b1-4f22-a1d8-8e5f2b6c3a01/   ← simulation 2
    9f2d1e45-c7a3-4b18-b2e6-1d8c4f7a9e23/   ← simulation 3
```

Each simulation directory is where EMOD runs. If a simulation fails, check `stderr.txt` and
`stdout.txt` in that directory to diagnose the problem. The output report files are also in
those directories, but Tutorial 2 introduces a more convenient way to retrieve them.
