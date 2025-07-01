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
from emodpy_hiv.campaign.individual_intervention import (PropertyValueChanger, BroadcastEvent,
                                                         ModifyStiCoInfectionStatus, AntiretroviralTherapy,
                                                         DelayedIntervention)
from emodpy_hiv.campaign.distributor import add_intervention_scheduled, add_intervention_triggered, add_intervention_reference_tracking
from emodpy_hiv.campaign.common import (TargetDemographicsConfig as TDC, TargetGender, PropertyRestrictions,
                                        CommonInterventionParameters as CIP, ValueMap)
from emodpy_hiv.campaign.waning_config import MapPiecewise
from emodpy_hiv.utils.distributions import ConstantDistribution, GaussianDistribution
from emodpy_hiv.utils.targeting_config import HasIP

import params
import manifest
import campaign_knobs as ck
import conf

ART_eligible_tag = "Accessibility:Easy"


def _add_sti_by_risk_and_coverage(camp, risk, coverage, include_ongoing=True):
    """
    Internal function to do the "dirty work" to support add_sti_coinfection_complex.
    1) Add a 'scheduled' campaign event to give some %age of people in a given risk group an STI (co-)infection.
    2) Optionally add a 'triggered' campaign event (at STIDebut) to give some %age of people in a given risk group an STI (co-)infection.
    """
    property_restrictions = PropertyRestrictions(individual_property_restrictions=[[risk]])
    set_sti_coinf = ModifyStiCoInfectionStatus(camp, new_sti_coinfection_status=True)
    broadcast_event = BroadcastEvent(camp, broadcast_event="CaughtNonHIVSTI")
    add_intervention_scheduled(camp, intervention_list=[set_sti_coinf, broadcast_event], start_day=1,
                               event_name="STI Co-Infection Setup",
                               property_restrictions=property_restrictions,
                               target_demographics_config=TDC(demographic_coverage=coverage))

    if include_ongoing:
        add_intervention_triggered(camp, triggers_list=["STIDebut"], intervention_list=[set_sti_coinf, broadcast_event],
                                   property_restrictions=property_restrictions, event_name="STI Co-Infection Setup",
                                   target_demographics_config=TDC(demographic_coverage=coverage))
    return camp


def add_sti_coinfection_complex(camp, low_coverage=0.1, med_coverage=0.3, high_coverage=0.3):
    """
    # ScheduledCampaignEvent @ t=0:
    Folks with Risk=LOW get one prob (10%) of STI CoInf
    Folks with Risk=MED or HIGH get another prob (30%) of STI CoInf

    TriggeredCampaigEvent @ OnDebut:
        Same thing as above.
    """
    _add_sti_by_risk_and_coverage(camp, "Risk:LOW", low_coverage, include_ongoing=True)
    _add_sti_by_risk_and_coverage(camp, "Risk:MEDIUM", med_coverage, include_ongoing=True)
    _add_sti_by_risk_and_coverage(camp, "Risk:HIGH", high_coverage, include_ongoing=True)


def add_csw(camp):
    # STIDebut -(HIVDelay)-> Uptake -(PVC)-> Dropout (PVC)
    broadcast_event = BroadcastEvent(camp, "CSW_Uptake")

    # 1: STIDebut->Uptake delay (males)
    add_intervention_triggered(camp,
                               intervention_list=[broadcast_event],
                               triggers_list=["STIDebut"],
                               start_day=1,
                               delay_distribution=GaussianDistribution(mean=ck.CSW_Male_Uptake_Delay, std_dev=30),
                               target_demographics_config=TDC(target_gender=TargetGender.MALE,
                                                              demographic_coverage=ck.CSW_Male_Uptake_Coverage),
                               event_name="Male CSW Debut->Uptake")
    # 2: STIDebut->Uptake delay (females)
    add_intervention_triggered(camp,
                               intervention_list=[broadcast_event],
                               triggers_list=["STIDebut"],

                               start_day=1,
                               delay_distribution=ConstantDistribution(value=ck.CSW_Female_Uptake_Delay),
                               target_demographics_config=TDC(target_gender=TargetGender.FEMALE,
                                                              demographic_coverage=ck.CSW_Female_Uptake_Coverage),
                               event_name="Female CSW Debut->Uptake")


    broadcast_event = BroadcastEvent(camp, "CSW_Dropout")

    # 4: Uptake->Dropout delay (males)
    add_intervention_triggered(camp,
                               intervention_list=[broadcast_event],
                               triggers_list=["CSW_Uptake"],
                               start_day=1,
                               delay_distribution=ConstantDistribution(value=ck.CSW_Male_Dropout_Delay),
                               target_demographics_config=TDC(target_gender=TargetGender.MALE,
                                                              demographic_coverage=ck.CSW_Male_Dropout_Coverage),
                               event_name="Male CSW Uptake->Dropout")
    # 5: Uptake->Dropout delay (females)
    add_intervention_triggered(camp,
                               intervention_list=[broadcast_event],
                               triggers_list=["CSW_Uptake"],
                               start_day=1,
                               delay_distribution=ConstantDistribution(value=ck.CSW_Female_Dropout_Delay),
                               target_demographics_config=TDC(target_gender=TargetGender.FEMALE,
                                                              demographic_coverage=ck.CSW_Female_Dropout_Coverage),
                               event_name="Female CSW Uptake->Dropout")

    # 3: Actually do the CSW Uptake (via PropertyValueChanger)
    pvc_go_high = PropertyValueChanger(camp, target_property_key="Risk", target_property_value="HIGH")
    add_intervention_triggered(camp, intervention_list=[pvc_go_high], triggers_list=["CSW_Uptake"],
                               event_name="CSW Uptake")

    # 6: Actually do the CSW Dropout (via PropertyValueChanger)
    pvc_go_med = PropertyValueChanger(camp, target_property_key="Risk", target_property_value="MEDIUM")
    add_intervention_triggered(camp, intervention_list=[pvc_go_med], triggers_list=["CSW_Dropout"],
                                 event_name="CSW Dropout")
    return camp


def _distribute_psk_tracker_by_age_and_sex(camp, min_age, max_age, sex, tvmap):
    """
    Internal function to do the 'dirty work' to support 'add_pos_status_known_tracker'.
    """
    from emodpy.campaign.individual_intervention import _SimpleHealthSeekingBehavior
    # First, give everyone who enters the HIV Latent stage a property that lets 
    # us target them with a "Faux Tested" intervention AND property.
    # Listen for LatentStage events and set PositiveStatus
    pvc_psk = PropertyValueChanger(camp, target_property_key="TestingStatus", target_property_value="POSITIVE")
    add_intervention_triggered(camp, intervention_list=[pvc_psk], triggers_list=["HIVInfectionStageEnteredLatent"],
                               event_name="Set Positive Status Known")

    # Now, here's what we're going to do...
    # 1) Give out something like the above, that triggers off of HIVInfectionStageEnteredLatent and set an IP for targeting.
    # 2) Give out a ref tracker that filters on the target IP above but distributes a Placebo/MedicalRecord with the name "PositiveStatusKnown" or something. This also sets an IP InterventionStatus:ARTEligible or something nasty. The placebo can be a delay or no-effect vaccine or something for now.
    status_known_medrec = _SimpleHealthSeekingBehavior(camp, intervention_event="PositiveStatusKnown", tendency=0,
                                                       common_intervention_parameters=CIP(new_property_value=ART_eligible_tag)) # Placeholder for "InterventionStatus:ARTEligible
    add_intervention_reference_tracking(camp, intervention_list=[status_known_medrec], start_year=1960,
                                        time_value_map=ValueMap(times=tvmap.keys(), values=tvmap.values()),
                                        target_demographics_config=TDC(target_gender=sex, target_age_min=min_age,
                                                                       target_age_max=max_age),
                                        tracking_config=HasIP(ip_key_value="TestingStatus:ELIGIBLE"))
    return camp


def add_pos_status_known_tracker(camp):
    """
    Put some subset of people who have entered latent infection stage into "Positive status known" 'state',
    which makes them ART-eligible. Drive this from data instead of creating a complex cascade that
    uses actually testing, etc. These coverages can vary by age group, sex, and simulation date.
    """
    tvmap = {1962: 0.5, 1963: 0.6, 1964: 0.7}  # just some simple test version
    # tvmap = { "1962": 0.99, 1963: 0.99, 1964: 0.99 } # almost everyone
    _distribute_psk_tracker_by_age_and_sex(camp, ck.PSK_Male_Age_Lower_Bound, ck.PSK_Male_Age_Upper_Bound, TargetGender.MALE,
                                           tvmap)
    _distribute_psk_tracker_by_age_and_sex(camp, ck.PSK_Female_Age_Lower_Bound, ck.PSK_Female_Age_Upper_Bound, TargetGender.FEMALE,
                                           tvmap)


def _distribute_art_by_ref_counter_by_age_and_sex(camp, art_coverage, min_age, max_age, sex, tvmap):
    """
    Internal utility function to do the 'dirty work' to support distribute_art_by_ref_counter for a given
    min_age, max_age, and sex. art_coverage is simply for a demonstration campaign sweep.
    """
    new_art = AntiretroviralTherapy(camp)
    iv = BroadcastEvent(camp, "ARTDropout")
    delayed_dropout_iv = DelayedIntervention(camp, intervention_to_distribute_at_delay_completion=iv,
                                             delay_period_distribution=ConstantDistribution(value=ck.ART_Duration)) # make this duration a bit more sophisticated

    # Old way of doing ART is ARTBasic + Delay->ARTDropout
    add_intervention_reference_tracking(camp, intervention_list=[new_art, delayed_dropout_iv], start_year=1960,
                                        time_value_map=ValueMap(times=tvmap.keys(), values=tvmap.values()),
                                        tracking_config=HasIP(ip_key_value=ART_eligible_tag),
                                        target_demographics_config=TDC(target_gender=sex, target_age_min=min_age,
                                                                       target_age_max=max_age))

    return camp


def distribute_art_by_ref_counter(camp, art_coverage):
    """
    For the ART:
    3) Give out a ref tracker that filters on the target IP InterventionStatus:ARTEligible and distributes ART.
    """
    # tvmap = { "1970": art_coverage/10, 1976: art_coverage/2, 1983: art_coverage }
    tvmap = {"1972": art_coverage / 10, 1978: art_coverage / 2, 1985: art_coverage}
    _distribute_art_by_ref_counter_by_age_and_sex(camp, art_coverage, ck.ART_Male_Age_Lower_Bound,
                                                  ck.ART_Male_Age_Upper_Bound, "Male", tvmap)
    _distribute_art_by_ref_counter_by_age_and_sex(camp, art_coverage, ck.ART_Female_Age_Lower_Bound,
                                                  ck.ART_Female_Age_Upper_Bound, "Female", tvmap)


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
    simulation.task.config.parameters.Run_Number = 3


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
        'logLevel_default'] = "WARNING"  # 'LogLevel_Default' is not in scheme, so need to use the old style dict keys

    # config hacks until schema fixes arrive
    config.parameters.pop("Serialized_Population_Filenames")
    config.parameters.pop("Serialization_Time_Steps")


    conf.set_config(config)
    import emodpy_hiv.utils.config_utils as config_utils
    config_utils.non_schema_checks(config)

    return config


def timestep_from_year(year):
    return (year - params.base_year) * 365


def build_camp(camp, art_coverage=1.0):
    """
        Build a campaign input file for the DTK using emod_api type functions or helpers from this module. 
        Note that 'camp' is short for 'campaign'.
        You can name this function whatever you want, it just has to match what you pass in from_default2.
    """
    # Crudely seed the infection
    event = ob.seed_infections(camp, start_day=timestep_from_year(1961.5))
    camp.add(event)

    add_sti_coinfection_complex(camp, ck.STI_Low_Risk_Coverage, ck.STI_Med_Risk_Coverage, ck.STI_High_Risk_Coverage)
    add_csw(camp)
    add_pos_status_known_tracker(camp)
    distribute_art_by_ref_counter(camp, art_coverage)
    return camp


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

    demog.set_fertility(manifest.fertility)
    demog.set_mortality(manifest.male_mortality, manifest.female_mortality)

    demog.AddIndividualPropertyAndHINT(Property="Accessibility", Values=["Easy", "Hard"],
                                       InitialDistribution=[0.0, 1.0])
    demog.AddIndividualPropertyAndHINT(Property="TestingStatus", Values=["INELIGIBLE", "ELIGIBLE"],
                                       InitialDistribution=[1.0, 0])
    demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.commercial.value,
                                        assortivity_matrix=[[1, 1, 1], [1, 1, 1], [1, 1, 1]])
    demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.informal.value,
                                        assortivity_matrix=[[0.6097767084, 0.3902232916, 0],
                                                            [0.3902232916, 0.6097767084, 0.6097767084],
                                                            [0, 0.6097767084, 0.3902232916]])
    demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.marital.value,
                                        assortivity_matrix=[[0.6097767084, 0.3902232916, 0],
                                                            [0.3902232916, 0.6097767084, 0.6097767084],
                                                            [0, 0.6097767084, 0.3902232916]])
    demog.set_pair_formation_parameters(relationship_type=RelationshipTypes.transitory.value,
                                        assortivity_matrix=[[0.6097767084, 0.3902232916, 0],
                                                            [0.3902232916, 0.6097767084, 0.6097767084],
                                                            [0, 0.6097767084, 0.3902232916]])

    demog.set_concurrency_params_by_type_and_risk("COMMERCIAL", "HIGH", 59, 59, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("COMMERCIAL", "MEDIUM", 0, 0, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("COMMERCIAL", "LOW", 0, 0, 1, 1)

    demog.set_concurrency_params_by_type_and_risk("INFORMAL", "HIGH", 1, 1, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("INFORMAL", "MEDIUM", 0.916, 0.916, 0.371, 0.399)
    demog.set_concurrency_params_by_type_and_risk("INFORMAL", "LOW", 1.605, 1.605, 0.533, 0)

    demog.set_concurrency_params_by_type_and_risk("MARITAL", "HIGH", 1, 1, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("MARITAL", "MEDIUM", 0.9, 0.9, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("MARITAL", "LOW", 1, 1, 0, 0)

    demog.set_concurrency_params_by_type_and_risk("TRANSITORY", "HIGH", 1, 1, 1, 1)
    demog.set_concurrency_params_by_type_and_risk("TRANSITORY", "MEDIUM", 2.738, 2.738, 0.588, 0.584)
    demog.set_concurrency_params_by_type_and_risk("TRANSITORY", "LOW", 1.5, 1.5, 0.260, 0.137)

    demog.set_pair_formation_parameters("COMMERCIAL", 0.15)
    demog.set_pair_formation_parameters("INFORMAL", 0.0010841069)
    demog.set_pair_formation_parameters("MARITAL", 5.47945e-05)
    demog.set_pair_formation_parameters("TRANSITORY", 0.0010478386)

    demog.set_relationship_parameters("COMMERCIAL", coital_act_rate=0.00274)
    demog.set_relationship_parameters("INFORMAL", coital_act_rate=0.33)
    demog.set_relationship_parameters("MARITAL", coital_act_rate=0.33)
    demog.set_relationship_parameters("TRANSITORY", coital_act_rate=0.33)

    demog.set_relationship_parameters("COMMERCIAL", condom_usage_min=0.5, condom_usage_mid=1999.5,
                                      condom_usage_max=0.85, condom_usage_rate=1)
    demog.set_relationship_parameters("INFORMAL", condom_usage_min=0, condom_usage_mid=1998.5140953411,
                                      condom_usage_max=0.3276293852, condom_usage_rate=1.4303827593)
    demog.set_relationship_parameters("MARITAL", condom_usage_min=0, condom_usage_mid=1997.7147536264,
                                      condom_usage_max=0.223467644, condom_usage_rate=2.8631895001)
    demog.set_relationship_parameters("TRANSITORY", condom_usage_min=0, condom_usage_mid=2006.3329995924,
                                      condom_usage_max=0.6093379311, condom_usage_rate=3.0)

    demog.set_relationship_parameters("COMMERCIAL", duration_heterogeneity=1, duration_scale=0.01917808219)
    demog.set_relationship_parameters("INFORMAL", duration_heterogeneity=0.75, duration_scale=2.03104913138)
    demog.set_relationship_parameters("MARITAL", duration_heterogeneity=0.666666667, duration_scale=22.154455184937)
    demog.set_relationship_parameters("TRANSITORY", duration_heterogeneity=0.833333333, duration_scale=0.956774771214)

    return demog


def art_coverage_test_sweep(simulation, sweep_param):
    art_coverage = sweep_param / 10.0
    build_campaign_partial = partial(build_camp, art_coverage=art_coverage)
    simulation.task.create_campaign_from_callback(build_campaign_partial)
    return {"ART_Target_Coverage": art_coverage}


def sim():
    """
    This function is designed to be a parameterized version of the sequence of things we do 
    every time we run an emod experiment. 
    """
    print_params()

    # Create a platform
    # Show how to dynamically set priority and node_group
    platform = Platform("Calculon", node_group="idm_48cores", priority="Highest")

    task = EMODTask.from_defaults(eradication_path=manifest.eradication_path,
                                  campaign_builder=build_camp,
                                  demographics_builder=build_demog,
                                  schema_path=manifest.schema_file,
                                  config_builder=set_param_fn,
                                  report_builder=conf.reports_builder)
    task.config.parameters.Run_Number = 55  # just to demo this because people ask about it.
    task.set_sif(str(manifest.sif_path), platform=platform)

    # Set task.campaign to None to not send any campaign to comps since we are going to override it later with
    # dtk-pre-process.
    print("Adding local assets (py scripts mainly)...")

    # Create simulation sweep with builder
    builder = SimulationBuilder()
    builder.add_sweep_definition(art_coverage_test_sweep, range(params.nSims))

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

    from emodpy_hiv.download import download
    download(experiment.uid.hex, manifest.output_dl_folder, manifest.output_files_to_get)
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
