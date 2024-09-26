"""
=== Tutorial #1 - Introduction to emodpy-hiv ===
`emodpy-hiv` is the new way for configuring, running, and analyzing EMOD-HIV simulations. 
It replaces the previous DtkTools/HIV-Analyzers/run_scenarios.py.  Tutorial #1 will
introduce you to the key components.

=== INSTRUCTIONS ===
There are two/three places below that you need to change depending on your platform
(COMPS or SLURM).  Look for the lines with UPDATE.


--- SLURM platform parameters ---
SLURM_LOCAL      - This tells idmtools you are on a ... local slurm cluster
job_directory    - directory containing suite/experiment/simulation directories
time             - maximum allowed runtime of a simulation (HH:MM:SS)
partition        - the set of nodes to submit the simulation jobs to
mail_user        - you can get emailed updates when your experiments finish here
mail_type        - ... if you set this parameter (ALL means jobs begin, finish, ...
max_running_jobs - This and the next param are for idmtools to allow parallel simulations
array_batch_size - ???
"""
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder

import emodpy_hiv.emod_task as emod_task
import emodpy_hiv.country_model as cm
import manifest

# Will make the warnings off by default in 2.0
import emod_api.schema_to_class as s2c
s2c.show_warnings = False


def sweep_run_number( simulation, value ):
    """
    This is a function used by the SimulationBuilder to sweep the parameter `Run_Number`.
    `Run_Number` is the random number seed to help us get different statistical 
    realizations of our scenario.
    """
    simulation.task.config.parameters.Run_Number = value
    return { "Run_Number": value }


def run_experiment():

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE - Select the correct Platform below
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    platform = Platform( "Calculon",
                         node_group="idm_abcd",
                         priority="Normal" )

    #platform = Platform( "SLURM_LOCAL",
    #                     job_directory="experiments",
    #                     time="02:00:00",
    #                     partition="cpu_short",
    #                     mail_user="XXX@YYY.org", # !!!! UPDATE !!!!
    #                     mail_type="ALL",
    #                     max_running_jobs=1000000,
    #                     array_batch_size=1000000 )

    zambia = cm.Zambia()
    task = emod_task.EMODHIVTask.from_default(
        eradication_path = manifest.eradication_path,
        schema_path      = manifest.schema_file,
        param_custom_cb  = zambia.build_config,
        campaign_builder = zambia.build_campaign,
        demog_builder    = zambia.build_demographics,
        ep4_path         = None
    )

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE- Select the following line given your platform
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #task.set_sif( path_to_sif=manifest.sif_path, platform=platform ) # SLURM
    task.set_sif( path_to_sif=manifest.sif_path ) # COMPS

    builder = SimulationBuilder()
    builder.add_sweep_definition( sweep_run_number, [1,2,3] )

    experiment = Experiment.from_builder( builder, task, name="Tutorial_1" )

    experiment.run( wait_until_done=True, platform=platform )

    print("\nTutorial #1 is done.")
    return


if __name__ == "__main__":
    import emod_hiv.bootstrap as dtk
    dtk.setup(local_dir=manifest.executables_dir)

    run_experiment()