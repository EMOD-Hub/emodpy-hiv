"""
=== Tutorial #4 - Overriding a State in the Cascade of Care ===
Sometimes the default cascade of care doesn't do exactly what you need.
For instance, you might need to add a decision point to determine if someone 
gets Antiretroviral Therapy (ART) or whether they wait. Maybe you want to 
break ART into effective ART and non-suppressive ART. This tutorial provides 
you an example on how to customize the cascade of care to meet your needs.

--- To override state, subclass country model ---
We use the concept of a "country model" to combine the collection of data 
and code needed to model a particular country. As you may have noticed from
the previous tutorials, the country model has its own build functions that 
we use for creating our `EMODTask`. The base class `Country` has a default 
`build_campaign()` method that defines a default set of methods to call for 
constructing the cascade of care. You can override this method or any of the 
methods that are part of the construction algorithm.

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

import emod_api
from emodpy_hiv.campaign import cascade_of_care as coc
from emodpy_hiv.campaign.individual_intervention import (HIVSigmoidByYearAndSexDiagnostic, Sigmoid, ControlledVaccine,
                                                         BroadcastEvent)
from emodpy_hiv.campaign.waning_config import MapPiecewise
from emodpy_hiv.campaign.common import (CommonInterventionParameters as CIP, PropertyRestrictions,
                                        TargetDemographicsConfig as TDC)
from emodpy_hiv.campaign.distributor import add_intervention_scheduled, add_intervention_triggered

from emodpy_hiv.countries.zambia.zambia import ZambiaForTraining
import emodpy.emod_task as emod_task

import manifest

# Will make the warnings off by default in 2.0
import emod_api.schema_to_class as s2c

s2c.show_warnings = False


class MyZambia(ZambiaForTraining):
    country_name = 'MyZambia'

    @classmethod
    def add_state_HCTUptakeAtDebut(cls, campaign: emod_api.campaign, start_year: float, node_ids: list = None):
        """
        The baseline `HCTUptakeAtDebut` state listens for the `STIDebut` built-in 
        event. This event is broadcast when the person decides to start seeking 
        sexual relationships. When this state hears this event, it will use a sigmoid 
        distribution to determine the probability that the person will enter the 
        testing loop or wait and consider it again later.

        In this example, we override this method by making the baseline implementation 
        only last the first 35 years (i.e., 1990 to 2025). In 2025, when it expires, 
        we start a new listener for `STIDebut` that will distribute a very long-lasting 
        PrEP and then send the person through the same sigmoid logic.

        __NOTE:__ In the last `add_triggered_event`, notice that it is distributing the 
        same `uptake_choice` intervention as the first one. This is one of those 
        benefits of using Python. If this were done in JSON, the configuration of 
        `uptake_choice` would have to be copy and pasted. Not having this data duplicated
        multiple times should lead to fewer bugs.
        """
        disqualifying_properties = [coc.CascadeState.LOST_FOREVER,
                                    coc.CascadeState.ON_ART,
                                    coc.CascadeState.LINKING_TO_ART,
                                    coc.CascadeState.ON_PRE_ART,
                                    coc.CascadeState.LINKING_TO_PRE_ART,
                                    coc.CascadeState.ART_STAGING]

        # --------------------------------------------------------------------
        # --- Do the same thing as baseline but only for 35 years / unitl 2025
        # --- i.e. stop listing for the STIDebut event so new code can
        # --------------------------------------------------------------------
        duration = 35 * 365  # this should cause the current logic to end in 2025
        uptake_choice = HIVSigmoidByYearAndSexDiagnostic(campaign,
                                                         year_sigmoid=Sigmoid(min=-0.005,
                                                                              max=0.05,
                                                                              mid=2005,
                                                                              rate=1),
                                                         positive_diagnosis_event=coc.HCT_TESTING_LOOP_TRIGGER,
                                                         negative_diagnosis_event=coc.HCT_UPTAKE_POST_DEBUT_TRIGGER_1,
                                                         female_multiplier=1.0,
                                                         common_intervention_parameters=CIP(
                                                             disqualifying_properties=disqualifying_properties,
                                                             new_property_value=coc.CascadeState.HCT_UPTAKE_AT_DEBUT))
        add_intervention_triggered(campaign,
                                   intervention_list=[uptake_choice],
                                   triggers_list=[coc.CustomEvent.STI_DEBUT],
                                   start_year=start_year,
                                   property_restrictions=PropertyRestrictions(
                                       individual_property_restrictions=[['Accessibility:Yes']]),
                                   node_ids=node_ids,
                                   event_name='HCTUptakeAtDebut: state 0 (decision, sigmoid by year and sex)',
                                   duration=duration) # !!! This is difference from baseline code

        # ---------------------------------------------------------------------
        # --- Insert the handing out of a very long lasting PrEP before making
        # --- the same sigmoid decision
        # ---------------------------------------------------------------------
        laprep_start_year = start_year + duration/365.0
        sigmoid_event = "Enter_Health_Care_System"
        laprep= ControlledVaccine(campaign,
                                  waning_config=MapPiecewise(days=[0, 1825, 1900, 2000, 2100, 2200],
                                                             effects=[0.8, 0.8, 0.5, 0.3, 0.1, 0.0]),
                                  common_intervention_parameters=CIP(disqualifying_properties=disqualifying_properties,
                                                                     new_property_value=coc.CascadeState.HCT_UPTAKE_AT_DEBUT,
                                                                     intervention_name="LA-PrEP"))

        broadcast_sigmoid = BroadcastEvent(campaign, sigmoid_event)

        add_intervention_triggered(campaign,
                                   intervention_list=[laprep, broadcast_sigmoid],
                                   triggers_list=[coc.CustomEvent.STI_DEBUT],
                                   property_restrictions=PropertyRestrictions(
                                       individual_property_restrictions=[['Accessibility:Yes']]),
                                   node_ids=node_ids,
                                   start_year=laprep_start_year,
                                   event_name='Tutorial 4 - LA-PrEP on STIDebut')

        # Distribute the uptake_choice but do it based on the sigmoid_event
        add_intervention_triggered(campaign,
                                   intervention_list=[uptake_choice],
                                   triggers_list=[sigmoid_event],
                                   property_restrictions=PropertyRestrictions(
                                     individual_property_restrictions=[['Accessibility:Yes']]),
                                   node_ids=node_ids,
                                   start_year=laprep_start_year,
                                   event_name='HCTUptakeAtDebut: Tutorial 4 LA-PrEP')


def build_config(config):
    """
    In our example function, we are going to double the initial population of the 
    baseline and reduce the duration of the simulation by 10 years.  The increased 
    population will make the simulations take longer, but the reduction in length 
    should reduce that increase.  (Simulations might take 5-7 minutes.)
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overridden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia

    config = zambia.build_config(config)

    config.parameters.x_Base_Population = config.parameters.x_Base_Population * 2.0
    config.parameters.Simulation_Duration = config.parameters.Simulation_Duration - (10 * 365)

    return config


def build_campaign(campaign):
    """
    In this example, we are going to add the distribution of a Long Lasting PrEP-like 
    intervention.  We will do a mass distribution every year for 15 years and increase 
    the coverage each year.

    One goal of this example is to demonstrate how we can use a `for-loop` in Python 
    instead of copying and pasting a large amount of JSON.
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overridden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia

    zambia.build_campaign(campaign)
    laprep = ControlledVaccine(campaign,
                               waning_config=MapPiecewise(days=[0, 180, 210, 240, 270, 300, 330],
                                                          effects=[0.8, 0.8, 0.7, 0.5, 0.3, 0.1, 0.0]),
                               common_intervention_parameters=CIP(intervention_name="LA-PrEP"))

    # Target only people who have accessibility to healthcare AND who's Risk is either HIGH or MEDIUM
    ip_restrictions = [
        ["Accessibility:Yes", "Risk:HIGH"],
        ["Accessibility:Yes", "Risk:MEDIUM"]
    ]
    property_restrictions = PropertyRestrictions(individual_property_restrictions=ip_restrictions)

    laprep_coverages = [0.1, 0.3, 0.5, 0.5, 0.5, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9]
    start_year = 2025
    for coverage in laprep_coverages:
        add_intervention_scheduled(campaign,
                                   intervention_list=[laprep],
                                   start_year=start_year,
                                   target_demographics_config=TDC(demographic_coverage=coverage),
                                   property_restrictions=property_restrictions,
                                   event_name=("Tutorial 4 LA-PrEP with coverage=" + str(coverage)),
                                   node_ids=None)
        start_year = start_year + 1

    return campaign


def build_demographics():
    """
    In the demographics example, we are simply going to increase the accessibility 
    to health care to 90%
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overridden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia

    demographics = zambia.build_demographics()

    demographics.AddIndividualPropertyAndHINT(Property="Accessibility",
                                              Values=["Yes", "No"],
                                              InitialDistribution=[0.9, 0.1],
                                              overwrite_existing=True)
    return demographics


def add_reports(reporters):
    """
    To organize our logic, we will create a method that configures the reports we want EMOD to produce.
    EMOD is already generating the default InsetChart.json (by setting
    `config.parameters.Enable_Default_Reporting = 1`). We will add two more reports so you can see how
    it is done and get everyone's favorite `ReportHIVByAgeAndGender`.
    """
    from emodpy_hiv.reporters.reporters import ReportSimulationStats, ReportHIVByAgeAndGender, ReportFilter

    reporters.add(ReportSimulationStats(reporters_object=reporters))
    reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                          report_filter=ReportFilter(start_year=1985,
                                                                     end_year=2070),
                                          reporting_period=365/6,
                                          collect_gender_data=True,
                                          collect_age_bins_data=[15, 20, 25, 30, 35, 40, 45, 50],
                                          collect_circumcision_data=True,
                                          collect_hiv_stage_data=False,
                                          collect_ip_data=[],
                                          collect_intervention_data=[],
                                          add_transmitters=False,
                                          stratify_infected_by_cd4=False,
                                          event_counter_list=[],
                                          add_relationships=False,
                                          add_concordant_relationships=False))
    return reporters


def process_results(experiment, platform, output_path):
    """
    We add another function to call that will use the `idmtools` concept of an "analyzer".
    Analyzers are intended to be Python logic that you use to process the output of your
    simulations.  In this tutorial, we will use the built-in `DownloadAnalyzer` to copy
    the reports to a directory called `tutorial_2_results`.

    In this method, we will also use the `AnalyzeManager` to execute the `DownloadAnalyzer`.
    One could have multiple analyzers. Imagine you have multiple report files and want to
    summarize each of those reports separately. You could create an analyzer for each report.
    """
    import os, shutil
    from idmtools.analysis.analyze_manager import AnalyzeManager
    from idmtools.analysis.download_analyzer import DownloadAnalyzer

    # Clean up 'outputs' dir
    if os.path.exists(output_path):
        shutil.rmtree(output_path)

    # files to be downloaded from each sim
    filenames = [
        'output/InsetChart.json',
        'output/ReportHIVByAgeAndGender.csv'
    ]
    analyzers = [DownloadAnalyzer(filenames=filenames, output_path=output_path)]

    manager = AnalyzeManager(platform=platform, analyzers=analyzers)
    manager.add_item(experiment)
    manager.analyze()
    return


def plot_results(output_path):
    """
    The following code uses the emodpy_hiv plotting utilities to plot the results
    of these simulations.  The images should be put into the 'output_path'.
    """
    import emodpy_hiv.plotting.plot_inset_chart as ic
    import emodpy_hiv.plotting.plot_hiv_by_age_and_gender as ang
    
    ic.plot_inset_chart(dir_name=output_path,
                        title="Tutorial #2 - Add Reports - InsetChart",
                        include_filenames_in_title=True,
                        output=output_path)

    ang.plot_population_by_age(dir_or_filename=output_path,
                               exp_dir_or_filename=None,
                               node_id=None,
                               gender=None,
                               age_bin_list=None,
                               show_avg_per_run=False,
                               img_dir=output_path)

    ang.plot_prevalence_for_dir(dir_or_filename=output_path,
                                exp_dir_or_filename=None,
                                node_id=None,
                                gender=None,
                                age_bin_list=None,
                                show_avg_per_run=None,
                                show_fraction=True,
                                img_dir=output_path)
    
    ang.plot_onART_by_age(dir_or_filename=output_path,
                          exp_dir_or_filename=None,
                          node_id=None,
                          gender=None,
                          age_bin_list=None,
                          show_avg_per_run=False,
                          show_fraction=True,
                          fraction_of_infected=True,
                          img_dir=output_path)

    return


def sweep_run_number(simulation, value):
    """
    This is a function used by the SimulationBuilder to sweep the parameter `Run_Number`.
    `Run_Number` is the random number seed to help us get different statistical 
    realizations of our scenario.
    """
    simulation.task.config.parameters.Run_Number = value
    return {"Run_Number": value}


def run_experiment():
    """
    The following code is the code we used in Tutorial #3.
    """

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE - Select the correct Platform below
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    platform = Platform('Container', job_directory="tutorial_output")

    # platform = Platform("Calculon",
    #                     node_group="idm_abcd",
    #                     priority="Normal")

    # platform = Platform( "SLURM_LOCAL",
    #                     job_directory="experiments",
    #                     time="02:00:00",
    #                     partition="cpu_short",
    #                     mail_user="XXX@YYY.org", # !!!! UPDATE !!!!
    #                     mail_type="ALL",
    #                     max_running_jobs=1000000,
    #                     array_batch_size=1000000 )

    task = emod_task.EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_file,
        config_builder=build_config,  # !!! from above !!!
        campaign_builder=build_campaign,  # !!! from above !!!
        demographics_builder=build_demographics,  # !!! from above !!!
        report_builder=add_reports)  # !!! from above !!!

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE- Select the following line given your platform
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # task.set_sif( path_to_sif=manifest.sif_path, platform=platform ) # SLURM
    # task.set_sif(path_to_sif=manifest.sif_path, platform=platform) # COMPS

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [1, 2, 3])

    experiment = Experiment.from_builder(builder, task, name="Tutorial_4")

    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if experiment.succeeded:
        print(f"Experiment {experiment.uid} succeeded.")

        output_path = "tutorial_4_results"
        process_results(experiment, platform, output_path)

        print(f"Downloaded resuts for experiment {experiment.uid}.")

        plot_results(output_path)

        print(f"\nLook in the '{output_path}' directory for the plots of the data.")
    else:
        print(f"Experiment {experiment.uid} failed.\n")

    print("\nTutorial #4 is done.")
    return


if __name__ == "__main__":
    import emod_hiv.bootstrap as dtk

    dtk.setup(local_dir=manifest.executables_dir)

    run_experiment()
