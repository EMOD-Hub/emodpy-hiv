#!/usr/bin/env python3

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...

from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
import emodpy.emod_task as emod_task

import manifest

from emodpy_hiv.demographics.relationship_types import RelationshipTypes

"""
    We create an intervention that sweeps over demographics parameters
"""


# When you're doing a sweep across campaign parameters, you want those parameters exposed
# in the build_camp function as done here
def build_camp(camp, start_day=365, initial_incidence=0.01 ):
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


def set_config_parameters(config):
    """
    This function is a callback that is passed to emod-api.config to set parameters The Right Way.
    """
    config.parameters.Simulation_Type = "HIV_SIM" # this should be set in the package.
    config.parameters.Simulation_Duration = 10*365.0 # maybe this should be a team-wide default?
    config.parameters.Base_Infectivity = 3.5 
    config.parameters.Enable_Demographics_Reporting = 0  # just because I don't like our default for this

    # config hacks until schema fixes arrive
    config.parameters.pop( "Serialized_Population_Filenames" )
    config.parameters.pop( "Serialization_Time_Steps" )
    config.parameters.Report_HIV_Event_Channels_List = []
    config.parameters.Male_To_Female_Relative_Infectivity_Ages = [] # 15,25,35 ]
    config.parameters.Male_To_Female_Relative_Infectivity_Multipliers = [] # 5, 1, 0.5 ]
    # This one is crazy! :(
    config.parameters.Maternal_Infection_Transmission_Probability = 0
    config.parameters['logLevel_default'] = "WARNING" # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys

    config.parameters.Incubation_Period_Distribution = 'EXPONENTIAL_DISTRIBUTION'
    config.parameters.Incubation_Period_Exponential = 30

    return config


def build_demographics(params: dict = None):
    """
    Build a demographics input file for the DTK using emod_api.
    Right now this function creates the file and returns the filename. If calling code just needs an asset that's fine.
    Also right now this function takes care of the config updates that are required as a result of specific demog settings. We do NOT want the emodpy-disease developers to have to know that. It needs to be done automatically in emod-api as much as possible.
    TBD: Pass the config (or a 'pointer' thereto) to the demog functions or to the demog class/module.

    """
    from emodpy_hiv.demographics.hiv_demographics import HIVDemographics  # OK to call into emod-api

    params = {} if params is None else params

    # creates a demographic file with 5k total people (randomly?) spread between 5 nodes
    # demographics = HIVDemographics.from_params(tot_pop=total_population, num_nodes=1,
    #                                            frac_rural=rural_fraction, id_ref="from_params")

    demographics = HIVDemographics.from_template_node(lat=0, lon=0, pop=10000, name='some node name', forced_id=1,
                                                      default_society_template='PFA-Southern-Africa')

    # TODO: redocument all functions and explain why we don't build the demographics at the beginning, too
    demographics.set_relationship_parameters(relationship_type=RelationshipTypes.transitory.value,
                                             condom_usage_min=params.get('condom_usage_min', None),
                                             condom_usage_max=params.get('condom_usage_max', None),
                                             condom_usage_mid=params.get('condom_usage_mid', None))

    # TBD: update birth rate 
    # this only has the defaults and not the information for individual nodes yet
    # demographics.AddIndividualPropertyAndHINT("Mood", ["Happy", "Sad"], [0.73, 0.27])

    return demographics


def update_demographics_multiple_params(simulation, params: dict):
    """
        This callback function modifies several demographics parameters
    Args:
        simulation:
        values: an array of values with which you want to update the paramters

    Returns:
        tag that will be used with the simulation
    """
    partial_build_demographics = partial(build_demographics, params=params)
    simulation.task.create_demographics_from_callback(partial_build_demographics, from_sweep=True)
    return params


def sim():
    """
        This function is designed to be a parameterized version of the sequence of things we do
    every time we run an emod experiment.
    Returns:
        Nothing
    """

    # Set platform
    # use Platform("SLURMStage") to run on comps2.idmod.org for testing/dev work
    platform = Platform("Calculon", node_group="idm_48cores")
    experiment_name = "Demographics Sweep example"
    # create EMODTask 
    print("Creating EMODTask (from files)...")
    task = emod_task.EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        campaign_builder=build_camp,
        schema_path=manifest.schema_file,
        config_builder=set_config_parameters)
    task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)
    task.set_sif(str(manifest.sif_path), platform=platform)

    # Create simulation sweep with builder
    # sweeping over start day AND killing effectiveness - this will be a cross product
    builder = SimulationBuilder()

    # this sweeps over one parameter, calling several of these one-parameter sweeps in
    # this script will cause only the last parameter to be swept, but there will be a cross-product-of-the-sweeps
    # number of simulations created.
    # comment out the builder below when using this
    # builder.add_sweep_definition(update_camp_start_day, [23, 3, 84, 1])
    # builder.add_sweep_definition(update_camp_start_day, [23, 3, 84, 1])


    # this is how you sweep over a multiple-parameters space:
    # itertools product creates a an array with all the combinations of parameters (cross-product)
    # so, 2x3x2 = 12 simulations
    import itertools
    # "birth_rate": values[0], "rural_fraction": values[1],"total_population": values[2]
    condom_settings = []
    for condom_max in [0.6, 0.8]:
        for condom_min in [0.2, 0.4]:
            for condom_mid in [1995.0, 2000.0]:
                condom_settings.append({'condom_usage_min': condom_min, 'condom_usage_max': condom_max,
                                        'condom_usage_mid': condom_mid})

    builder.add_sweep_definition(function=update_demographics_multiple_params, params=condom_settings)
                                 # list(itertools.product([0.000412, 0.000422], [0.95, 0.87, 0.58], [10000, 20000])))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=experiment_name)

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
    dtk.setup( pathlib.Path( manifest.eradication_path ).parent ) 
    sim()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--use_vpn', type=str, default='No', choices=['No', "Yes"],
                        help='get model files from Bamboo(needs VPN) or Pip installation(No VPN)')
    args = parser.parse_args()
    run()
