"""
=== Tutorial #3 - Build Functions ===
This tutorial will introduce you to creating your own build functions so that
you can modify the baseline country model.

--- What are build functions? ---
These are the functions that `EMODTask` calls to build the configuration files
for each simulation in the experiement. They are called once for each simulation,
so if you were to have a significant amount of processing in a build function,
it will get multiplied by the number of simulations in your experiement. While
you probably won't have extensive processing, it is something to be aware of.

Your build functions can have whatever name you wish, but users typically
choose build_config, build_campaign, and build_demographics.

`build_config()`      - This function will get called first to set the basic,
                        simulation-wide configuration parameters.
`build_campaign()`    - This function is used for creating the logic of when, 
                        who, why, and how interventions are distributed.
`build_demograpics()` - The demographics configuration determines the number
                        of initial people in your scenario, fertility rates, 
                        mortality rates, and relationship parameters.

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

import emodpy_hiv.interventions.prep as prep
import emodpy_hiv.interventions.cascade_helpers as helpers

import emodpy_hiv.emod_task as emod_task
import emodpy_hiv.country_model as cm
import manifest

# Will make the warnings off by default in 2.0
import emod_api.schema_to_class as s2c
s2c.show_warnings = False


def build_config( config ):
    """
    In our example function, we are going to double the initial population of the 
    baseline and reduce the duration of the simulation by 10 years.  The increased 
    population will make the simulations take longer, but the reduction in length 
    should reduce that increase.  (Simulations might take 5-7 minutes.)
    """
    zambia = cm.Zambia()
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
    zambia = cm.Zambia()
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
    zambia = cm.Zambia()
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
    The following code is the code we used in Tutorial #2.
    Please note how the param_custom_cb, campaign_builder, and demog_builder arguments
    in the EMODHIVTask are now using the functions we defined above.
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

    experiment = Experiment.from_builder( builder, task, name="Tutorial_3" )

    experiment.run( wait_until_done=True, platform=platform )

    # Check result
    if experiment.succeeded:
        print(f"Experiment {experiment.uid} succeeded.")

        output_path = "tutorial_3_results"
        process_results( experiment, platform, output_path )

        print(f"Downloaded resuts for experiment {experiment.uid}.")

        plot_results( output_path )
        
        print(f"\nLook in the '{output_path}' directory for the plots of the data.")
    else:
        print(f"Experiment {experiment.uid} failed.\n")

    print("\nTutorial #3 is done.")
    return


if __name__ == "__main__":
    import emod_hiv.bootstrap as dtk
    dtk.setup(local_dir=manifest.executables_dir)

    run_experiment()