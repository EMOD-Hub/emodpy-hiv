#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

import emodpy.emod_task as emod_task

import manifest

# ****************************************************************
# Features to support:
#
#  Read experiment info from a json file
#  Add Eradication.exe as an asset (Experiment level)
#  Add Custom file as an asset (Simulation level)
#  Add the local asset directory to the task
#  Use builder to sweep simulations
#  How to run dtk_pre_process.py as pre-process
#  Save experiment info to file
# ****************************************************************

"""
    We create a basic HIV simulation and sweep over a parameter of the campaign.

"""


# When you're doing a sweep across campaign parameters, you want those parameters exposed
# in the build_campaign function as done here
def build_camp(camp, start_day=365, initial_incidence=0.01):
    """
    Build a campaign input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    """
    from emodpy_hiv.campaign.individual_intervention import OutbreakIndividual
    from emodpy_hiv.campaign.distributor import add_intervention_scheduled
    from emodpy_hiv.campaign.common import TargetDemographicsConfig as TDC

    ob = OutbreakIndividual(camp)
    add_intervention_scheduled(camp,
                               intervention_list=[ob],
                               start_day=start_day,
                               target_demographics_config=TDC(demographic_coverage=initial_incidence))
    return camp


def update_campaign_start_day(simulation, value):
    """
        This callback function updates the start day of the campaign.
    Args:
        simulation:
        value: value to which the start_day will be set

    Returns:
        tag that will be added to the simulation run
    """
    build_campaign_partial = partial(build_camp, start_day=value)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"start_day": value}


def update_campaign_multiple_parameters(simulation, values):
    """
        This is a callback function that updates several parameters in the build_campaign function.
        the sweep is achieved by the itertools creating a an array of inputs with all the possible combinations
        see builder.add_sweep_definition(update_campaign_multiple_parameters function below
    Args:
        simulation: simulation object to which we will attach the callback function
        values: a list of values to assign to this particular simuation

    Returns:
        tags for the simulation to use in comps
    """
    build_campaign_partial = partial(build_camp, start_day=values[0], initial_incidence=values[1])
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"start_day": values[0], "coverage": values[1]}


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "HIV_SIM"  # this should be set in the package.
    config.parameters.Simulation_Duration = 10 * 365.0  # maybe this should be a team-wide default?
    config.parameters.Enable_Demographics_Reporting = 0  # just because I don't like our default for this

    # config hacks until schema fixes arrive
    config.parameters.pop("Serialized_Population_Filenames")
    config.parameters.pop("Serialization_Time_Steps")
    config.parameters.Report_HIV_Event_Channels_List = []
    config.parameters.Male_To_Female_Relative_Infectivity_Ages = []  # 15,25,35 ]
    config.parameters.Male_To_Female_Relative_Infectivity_Multipliers = []  # 5, 1, 0.5 ]
    # This one is crazy! :(
    config.parameters.Maternal_Infection_Transmission_Probability = 0
    config.parameters[
        'logLevel_default'] = "WARNING"  # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys_

    config.parameters.Incubation_Period_Distribution = 'EXPONENTIAL_DISTRIBUTION'
    config.parameters.Incubation_Period_Exponential = 30

    return config


def build_demographics():
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    from emodpy_hiv.demographics.hiv_demographics import HIVDemographics  # OK to call into emod-api

    demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=10000, name=1, forced_id=1,
                                                      default_society_template='PFA-Southern-Africa')
    return demographics


def sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_defaults(eradication_path=manifest.eradication_path,
                                               campaign_builder=build_camp,
                                               schema_path=manifest.schema_file,
                                               config_builder=set_config_parameters,
                                               demographics_builder=build_demographics)
    task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    task.set_sif(str(manifest.sif_path), platform=platform)

    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this sweeps over one parameter, calling several of these one-parameter sweeps in
    # this script will cause only the last parameter to be swept, but there will be a cross-product-of-the-sweeps
    # number of simulations created.
    # comment out the builder below when using this
    builder.add_sweep_definition(update_campaign_start_day, [1, 60, 120, 240])

    # this is how you sweep over a multiple-parameters space:
    # itertools product creates a an array with all the combinations of parameters (cross-product)
    # so, 2x3x2 = 12 simulations
    # import itertools
    # .product([start_days],[spray_coverages], [killing_effectivenesses])
    # builder.add_sweep_definition(update_campaign_multiple_parameters,
    # list(itertools.product([3, 5], [0.95, 0.87, 0.58])))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name="Campaign Sweep, Outbreak")

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if not experiment.succeeded:
        print(f"Experiment {experiment.uid} failed.\n")
        exit()

    print(f"Experiment {experiment.uid} succeeded.")

    # Save experiment id to file
    with open("COMPS_ID", "w") as fd:
        fd.write(experiment.uid.hex)
    print()
    print(experiment.uid.hex)


def run():
    import emod_hiv.bootstrap as dtk
    dtk.setup(pathlib.Path(manifest.eradication_path).parent)
    sim()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--use_vpn', type=str, default='No', choices=['No', "Yes"],
                        help='get model files from Bamboo(needs VPN) or Pip installation(No VPN)')
    args = parser.parse_args()
    run()
