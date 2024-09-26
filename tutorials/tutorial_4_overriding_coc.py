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
from emod_api.interventions.common import BroadcastEvent
from emodpy_hiv.country_model import Zambia
from emodpy_hiv.campaign import coc
from emodpy_hiv.interventions import sigmoiddiag
import emodpy_hiv.interventions.prep as prep
import emodpy_hiv.interventions.cascade_helpers as helpers

import emodpy_hiv.emod_task as emod_task
import emodpy_hiv.country_model as cm
import manifest

# Will make the warnings off by default in 2.0
import emod_api.schema_to_class as s2c
s2c.show_warnings = False


class MyZambia(Zambia):
    def __init__(self):
        super().__init__('MyZambia')

    def add_state_HCTUptakeAtDebut(self, campaign: emod_api.campaign, start_day: int):
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
        `uptake_choise` would have to be copy and pasted. Not having this data duplcated
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
        duration = 35 * 365 # this should cause the current logic to end in 2025
        uptake_choice = sigmoiddiag.new_diagnostic( 
            campaign,
            Positive_Event=coc.HCT_TESTING_LOOP_TRIGGER,
            Negative_Event=coc.HCT_UPTAKE_POST_DEBUT_TRIGGER_1,
            ramp_min=-0.005,
            ramp_max=0.05,
            ramp_midyear=2005,
            ramp_rate=1,
            female_multiplier=1.0,
            disqualifying_properties=disqualifying_properties,
            new_property_value=coc.CascadeState.HCT_UPTAKE_AT_DEBUT) 
        
        helpers.add_triggered_event( 
            campaign,
            event_name='HCTUptakeAtDebut: state 0 (decision, sigmoid by year and sex)',
            in_trigger=coc.CustomEvent.STI_DEBUT,
            out_iv=[uptake_choice],
            property_restrictions=['Accessibility:Yes'],
            node_ids=None,
            start_day=start_day,
            duration=duration ) # !!! This is difference from baseline code

        # ---------------------------------------------------------------------
        # --- Insert the handing out of a very long lasting PrEP before making
        # --- the same sigmoid decision
        # ---------------------------------------------------------------------
        laprep_start_day = start_day + duration
        sigmoid_event = "Enter_Health_Care_System"

        laprep = prep.new_intervention( 
            campaign,
            efficacy_times=   [  0, 1825, 1900, 2000, 2100, 2200 ],
            efficacy_values=  [0.8, 0.8,   0.5,  0.3,  0.1,  0.0 ],
            intervention_name="LA-PrEP",
            disqualifying_properties=disqualifying_properties,
            new_property_value=coc.CascadeState.HCT_UPTAKE_AT_DEBUT )
        
        broadcast_sigmoid = BroadcastEvent( campaign, sigmoid_event )

        helpers.add_triggered_event(
            campaign,
            event_name='Tutorial 4 - LA-PrEP on STIDebut',
            in_trigger=coc.CustomEvent.STI_DEBUT,
            out_iv=[laprep,broadcast_sigmoid],
            property_restrictions=['Accessibility:Yes'],
            node_ids=None,
            start_day=laprep_start_day )

        # Distribute the uptake_choice but do it based on the sigmoid_event
        helpers.add_triggered_event( 
            campaign,
            event_name='HCTUptakeAtDebut: Tutorial 4 LA-PrEP',
            in_trigger=sigmoid_event, # event broadcast when the person gets PrEP
            out_iv=[uptake_choice],
            property_restrictions=['Accessibility:Yes'],
            node_ids=None,
            start_day=laprep_start_day )

        return


def build_config( config ):
    """
    In our example function, we are going to double the initial population of the 
    baseline and reduce the duration of the simulation by 10 years.  The increased 
    population will make the simulations take longer, but the reduction in length 
    should reduce that increase.  (Simulations might take 5-7 minutes.)
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overriden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia() 

    config = zambia.build_config( config )

    config.parameters.x_Base_Population = config.parameters.x_Base_Population * 2.0
    config.parameters.Simulation_Duration = config.parameters.Simulation_Duration - (10 * 365)
    
    return config


def build_campaign( ):
    """
    In this example, we are going to add the distribution of a Long Lasting PrEP-like 
    intervention.  We will do a mass distribution every year for 15 years and increase 
    the coverage each year.

    One goal of this example is to demonstrate how we can use a `for-loop` in Python 
    instead of copying and pasting a large amount of JSON.
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overriden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia() 

    campaign = zambia.build_campaign( manifest.schema_file )

    laprep = prep.new_intervention( campaign,
                                    efficacy_times=   [  0, 180, 210, 240, 270, 300, 330 ],
                                    efficacy_values=  [0.8, 0.8, 0.7, 0.5, 0.3, 0.1, 0.0 ],
                                    intervention_name="LA-PrEP",
                                    disqualifying_properties=None,
                                    new_property_value=None )
    
    # Target only people who have accessibility to healthcare AND who's Risk is either HIGH or MEDIUM
    ip_restrictions = [
        { "Accessibility": "Yes", "Risk": "HIGH"  },
        { "Accessibility": "Yes", "Risk": "MEDIUM" }
    ]

    laprep_coverages = [ 0.1, 0.3, 0.5, 0.5, 0.5, 0.7, 0.7, 0.7, 0.8, 0.8, 0.8, 0.8, 0.9, 0.9, 0.9  ]
    start_year = 2025
    for coverage in laprep_coverages:
        start_day = (start_year - 1960.5) * 365
        helpers.add_scheduled_event( campaign,
                                     event_name=("Tutorial 3 LA-PrEP with coverage="+str(coverage)),
                                     start_day=start_day,
                                     coverage=coverage,
                                     property_restrictions=ip_restrictions,
                                     out_iv=[laprep],
                                     node_ids=None )
        start_year = start_year + 1

    return campaign


def build_demographics():
    """
    In the demographics example, we are simply going to increase the accessibility 
    to health care to 90%
    """
    # !!!!!!!!!!!!!!!!!!!!!!!!
    # Overriden Country Model 
    # !!!!!!!!!!!!!!!!!!!!!!!!
    zambia = MyZambia() 

    demographics = zambia.build_demographics()

    demographics.AddIndividualPropertyAndHINT( Property="Accessibility",
                                               Values=[ "Yes", "No" ],
                                               InitialDistribution=[ 0.9, 0.1 ],
                                               overwrite_existing=True )
    return demographics


def add_reports( task, mainifest ):
    """
    To organize our logic, we will create a method that configures the reports we want EMOD to produce.
    EMOD is already generating the default InsetChart.json (by setting 
    `config.parameters.Enable_Default_Reporting = 1`). We will add two more reports so you can see how
    it is done and get everyone's favorite `ReportHIVByAgeAndGender`.
    """
    import emodpy_hiv.reporters.builtin as rp

    rp.add_report_simulation_stats( task, manifest )
    rp.add_report_hiv_by_age_and_gender(task,
                                        start_year=1985, #avoid outbreak so newly infected plot isn't overwhelmed
                                        end_year=2070,
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
                                        add_concordant_relationships=False)
    return


def process_results( experiment, platform, output_path ):
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
    if os.path.exists( output_path ):
        shutil.rmtree( output_path )

    # files to be downloaded from each sim
    filenames = [
        'output/InsetChart.json',
        'output/ReportHIVByAgeAndGender.csv'
    ]
    analyzers = [ DownloadAnalyzer( filenames=filenames, output_path=output_path ) ]

    manager = AnalyzeManager( platform=platform, analyzers=analyzers )
    manager.add_item( experiment )
    manager.analyze()
    return


def plot_results( output_path ):
    """
    The following code uses some tutorial-helper functions to plot the results
    of these simulations.  The images should be put into the 'output_path'.
    """
    import plot_report_hiv_by_age_and_gender as my_plt

    report_filenames = my_plt.get_report_filenames( output_path,
                                                    "ReportHIVByAgeAndGender.csv" )
    
    df = my_plt.create_dataframe_from_csv_reports( report_filenames )
    num_runs = len(report_filenames)

    my_plt.plot_age_based_data( output_path, df, num_runs,  "Population (15-49) Over Time",                                  " Population" )
    my_plt.plot_age_based_data( output_path, df, num_runs,  "Number of People (15-49) on ART Over Time",                     " On_ART" )
    my_plt.plot_age_based_data( output_path, df, num_runs,  "Number of Newly Infected People (15-49) (Incidence) Over Time", " Newly Infected" )
    my_plt.plot_age_based_data( output_path, df, num_runs,  "Number of Infected People (15-49) (Prevalence) Over Time",      " Infected" )

    return


def sweep_run_number( simulation, value ):
    """
    This is a function used by the SimulationBuilder to sweep the parameter `Run_Number`.
    `Run_Number` is the random number seed to help us get different statistical 
    realizations of our scenario.
    """
    simulation.task.config.parameters.Run_Number = value
    return { "Run_Number": value }


def run_experiment():
    """
    The following code is the code we used in Tutorial #3.
    """

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

    task = emod_task.EMODHIVTask.from_default(
        eradication_path = manifest.eradication_path,
        schema_path      = manifest.schema_file,
        param_custom_cb  = build_config,       # !!! from above !!!
        campaign_builder = build_campaign,     # !!! from above !!!
        demog_builder    = build_demographics, # !!! from above !!!
        ep4_path         = None
    )
    add_reports( task, manifest )
    task.config.parameters.Report_HIV_Period = 365/6

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE- Select the following line given your platform
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #task.set_sif( path_to_sif=manifest.sif_path, platform=platform ) # SLURM
    task.set_sif( path_to_sif=manifest.sif_path ) # COMPS

    builder = SimulationBuilder()
    builder.add_sweep_definition( sweep_run_number, [1,2,3] )

    experiment = Experiment.from_builder( builder, task, name="Tutorial_4" )

    experiment.run( wait_until_done=True, platform=platform )

    # Check result
    if experiment.succeeded:
        print(f"Experiment {experiment.uid} succeeded.")

        output_path = "tutorial_4_results"
        process_results( experiment, platform, output_path )

        print(f"Downloaded resuts for experiment {experiment.uid}.")

        plot_results( output_path )
        
        print(f"\nLook in the '{output_path}' directory for the plots of the data.")
    else:
        print(f"Experiment {experiment.uid} failed.\n")

    print("\nTutorial #4 is done.")
    return


if __name__ == "__main__":
    import emod_hiv.bootstrap as dtk
    dtk.setup(local_dir=manifest.executables_dir)

    run_experiment()