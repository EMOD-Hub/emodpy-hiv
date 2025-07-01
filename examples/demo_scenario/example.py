#!/usr/bin/env python

import pathlib  # for a join
from functools import \
    partial  # for setting Run_Number. In Jonathan Future World, Run_Number is set by dtk_pre_proc based on generic param_sweep_value...

# idmtools ...
from idmtools.assets import Asset, AssetCollection  #
from idmtools.builders import SimulationBuilder
from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment

# emodpy
from emodpy.emod_task import EMODTask

from emodpy_hiv.demographics.relationship_types import RelationshipTypes
from emodpy_hiv.campaign.individual_intervention import (OutbreakIndividual, AntiretroviralTherapy, ControlledVaccine,
                                                         HIVRandomChoice, HIVRapidHIVDiagnostic, BroadcastEvent)
from emodpy_hiv.campaign.distributor import add_intervention_scheduled, add_intervention_triggered
from emodpy_hiv.utils.distributions import ConstantDistribution
import conf

import params
import manifest


# ****************************************************************
# Basic flow:
#
#  Read experiment info from a json file
#  Add Eradication.exe as an asset (Experiment level)
#  Add Custom file as an asset (Simulation level)
#  Add the local asset directory to the task
#  Use builder to sweep simulations
#  How to run dtk_pre_process.py as pre-process
#  Save experiment info to file
# ****************************************************************

def update_sim_bic(simulation, value):
    """
        Update the value of a (scientific) configuration parameter, in this case Base_Infectivity_Constant 
        (which may or may not be part of this sim_type's parameters), as part of a sweep.
    """
    simulation.task.config.parameters.Base_Infectivity_Constant = value * 0.1
    return {"Base_Infectivity": value}


def update_sim_random_seed(simulation, value):
    """
        Update the value of the Run_Number as part of the most basic configuration sweep example.
    """
    simulation.task.config.parameters.Run_Number = value


def print_params():
    """
        Print the values of the _experiment_ params. Note these are not DTK scenario params.
    """
    # Display exp_name and nSims
    # TBD: Just loop through them
    print("exp_name: ", params.exp_name)
    print("nSims: ", params.nSims)


def set_param_fn(config):
    """
        Set the configuration parameters. Every parameter must be in the schema and every value must be valid
        per the schema. You usually don't need to set Enable's as they are set implicitly now. Refer to the schema
        for the possible params for your model. You can name this function whatever you want, it just has to 
        match what you pass in from_default2.
    """
    config.parameters.Simulation_Duration = 35300
    config.parameters.Simulation_Timestep = 30.4166666666667
    config.parameters.Start_Time = 0
    config.parameters.Base_Year = params.base_year
    config.parameters.Run_Number = 11016
    config.parameters[
        'logLevel_default'] = "WARNING"  # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys_

    # config hacks until schema fixes arrive
    config.parameters.pop("Serialized_Population_Filenames")
    config.parameters.pop("Serialization_Time_Steps")

    conf.set_config(config)
    return config


def timestep_from_year(year):
    return (year - params.base_year) * 365


def build_camp(camp):
    """
        Build a campaign input file for the DTK using emod_api type functions or helpers from this module. 
        Note that 'camp' is short for 'campaign'.
        You can name this function whatever you want, it just has to match what you pass in from_default2.
    """

    # Setup
    from emodpy_hiv.campaign.individual_intervention import OutbreakIndividual
    from emodpy_hiv.campaign.distributor import add_intervention_scheduled

    ob = OutbreakIndividual(camp)
    add_intervention_scheduled(camp,
                               intervention_list=[ob],
                               start_day=timestep_from_year(1961.5))

    # Design your campaign
    """
    Let's build a cascade like:
    NewInfection->Delay(simulating time to onset of symptoms)->RandomChoice->Tested->OnART

    Long description of what's happening here:

    - Each of these functions below is in cascade_helpers.py. 
    - Each one is using default arguments to exaggerate the simplicity.
    - The best way to view what this ultimately does is in ReportEventCounter.csv, prefeably imported into SQLite.
    - Each function populates campaign.json, not that you have to know that, with intervention structures that 
      say 'If you hear this signal, do this other thing'.

    1) add_choice( camp, sympto_signal="NewlySymptomatic", get_tested_signal="GetTested" )
       Intent: Some people who feel sick go to doctor. (Some don't.)
       Listen for a 'NewlySymptomatic' signal, and 'toss a coin', and immediately broacast a 'GetTested' signal
       for those who get 'heads'. More literally, 50% of folks broadcast 'GetTested', and the other 50% broadcast
       'Ignore'. The probs and 'Ignore' are hard-coded right now but of course don't have to be.

    2) add_test( camp, get_tested_signal="GetTested" )
       Intent: People who go to doctor get tested.
       Listen for a 'NewlySymptomatic' signal, and administer an HIV RapidDiagonstic intervention. 30 days later,
       broadcast an 'HIVPositiveTest' signal for the +ves, and an 'HIVNegativeTest' for the -ves. Since the current
       design starts with NewInfectionEvent, 100% of those tested will be +ve unless we have false negatives.

    3) trigger_art_from_pos_test( camp, input_signal="HIVPositiveTest", output_signal="StartTreatment", lag_time=30 )
       Intent: Get people who test positive into ART pipeline.
       Listen for "HIVPositiveTest", and 30 timesteps later broadcast a "StartTreatment" signal.  
    
    4) add_art_from_trigger( camp, signal="StartTreatment" )
       Intent: Actually put people on ART (in a standard way).
       Listen for StartTreatment signal and immediately distribute ART intervention.
    """
    add_choice(camp)
    add_test(camp)
    trigger_art_from_pos_test(camp)
    add_art_from_trigger(camp)

    return camp


def add_choice(campaign):
    ob_start_day = 2
    sympto_signal = "NewInfectionEvent"
    get_tested_signal = 'get_tested_signal'
    ob = OutbreakIndividual(campaign=campaign)
    add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)
    choice = HIVRandomChoice(campaign=campaign, choice_names=[get_tested_signal, "Ignore"],
                             choice_probabilities=[0.5, 0.5])
    add_intervention_triggered(intervention_list=[choice], campaign=campaign, start_day=1,
                               triggers_list=[sympto_signal], event_name="Decide_On_Testing")


def add_test(campaign):
    ob_start_day = 2
    get_tested_signal = "NewInfectionEvent"
    builtin_pos_event = "HIVPositiveTest"
    builtin_delay = 30

    ob = OutbreakIndividual(campaign=campaign)
    add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

    test = HIVRapidHIVDiagnostic(campaign=campaign, positive_diagnosis_event=builtin_pos_event,
                                 negative_diagnosis_event="HIVNegativeTest", base_sensitivity=1)
    add_intervention_triggered(intervention_list=[test], campaign=campaign, start_day=1,
                               delay_distribution=ConstantDistribution(builtin_delay),
                               triggers_list=[get_tested_signal], event_name="Test")


def trigger_art_from_pos_test(campaign):
    ob_start_day = 2
    input_signal = "NewInfectionEvent"
    output_signal = "StartTreatment"
    delay = 15

    ob = OutbreakIndividual(campaign=campaign)
    add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

    broadcast_event = BroadcastEvent(campaign, output_signal)
    add_intervention_triggered(intervention_list=[broadcast_event], campaign=campaign, start_day=1,
                               delay_distribution=ConstantDistribution(delay),
                               triggers_list=[input_signal], event_name="NeedTreatment")


def add_art_from_trigger(campaign):
    ob_start_day = 20
    signal = "NewInfectionEvent"

    ob = OutbreakIndividual(campaign=campaign)
    add_intervention_scheduled(intervention_list=[ob], campaign=campaign, start_day=ob_start_day)

    art = AntiretroviralTherapy(campaign=campaign)
    add_intervention_triggered(intervention_list=[art], campaign=campaign, start_day=1,
                               triggers_list=[signal], event_name="ART on trigger")


def build_demog():
    """
        Build a demographics input file for the DTK using emod_api. 
    """
    from emodpy_hiv.demographics.hiv_demographics import HIVDemographics

    demog = HIVDemographics.from_template_node(lat=0, lon=0, pop=100000, name='some place', forced_id=1,
                                               default_society_template="PFA-Southern-Africa")
    demog.SetEquilibriumAgeDistFromBirthAndMortRates(node_ids=[None])

    # TODO: this is a WORKAROUND of emod-api bug that doesn't swap out the age distributions properly
    #  https://github.com/InstituteforDiseaseModeling/emod-api/issues/705
    demog.default_node.individual_attributes.age_distribution_flag = None

    demog.set_fertility("Malawi_Fertility_Historical.csv")
    demog.set_mortality("Malawi_male_mortality.csv", "Malawi_female_mortality.csv")

    demog.add_or_update_initial_health_care_accessibility_distribution(distribution=[0.9, 0.1])
    demog.add_or_update_initial_risk_distribution(distribution=[0.99, 0, 0.01])
    demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.commercial.value,
                                        assortivity_matrix=[[1, 1, 1], [1, 1, 1], [1, 1, 1]])

    return demog


def sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    # Create a platform
    # Show how to dynamically set priority and node_group
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")
    # pl = RequirementsToAssetCollection( platform, requirements_path=manifest.requirements ) 

    task = EMODTask.from_defaults(eradication_path=manifest.eradication_path,
                                  campaign_builder=build_camp,
                                  demographics_builder=build_demog,
                                  schema_path=manifest.schema_file,
                                  config_builder=set_param_fn,
                                  report_builder=conf.config_reports)
    task.set_sif(str(manifest.sif_path), platform=platform)


    # task.common_assets.add_asset( demog_path )

    # print("Adding asset dir...")
    # task.common_assets.add_directory(assets_directory=manifest.assets_input_dir)

    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    """
    if ep4_scripts is not None:
        for asset in ep4_scripts:
            pathed_asset = Asset(pathlib.PurePath.joinpath(manifest.embedded_python_scripts_path, asset), relative_path="python")
            task.common_assets.add_asset(pathed_asset)
    """

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(update_sim_random_seed, range(params.nSims))

    # create experiment from builder
    experiment = Experiment.from_builder(builder, task, name=params.exp_name)

    # The last step is to call run() on the ExperimentManager to run the simulations.
    experiment.run(wait_until_done=True, platform=platform)

    # other_assets = AssetCollection.from_id(pl.run())
    # experiment.assets.add_assets(other_assets)

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
    assert experiment.succeeded


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
