"""
=== Tutorial #2 - Add reports, download the reports, and plot the data ===
The objective of this tutorial is to give you a very simple way of getting
the results from your experiement. It will start with the code we used in
Tutorial #1 and:
- Show you how to add new reports
- Show you how to download the reports
- Plot the data in the reports so we can see how the simulation is performing

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
import os

from idmtools.core.platform_factory import Platform
from idmtools.entities.experiment import Experiment
from idmtools.builders import SimulationBuilder

import emodpy.emod_task as emod_task
import emodpy_hiv.countries.zambia.zambia as cm
import manifest

# Will make the warnings off by default in 2.0
import emod_api.schema_to_class as s2c

s2c.show_warnings = False


def build_reports(reporters):
    """
    To organize our logic, we will create a method that configures the reports we want EMOD to produce.
    We will add three reports so you can see how it is done and get everyone's favorite `ReportHIVByAgeAndGender`.
    """
    from emodpy_hiv.reporters.reporters import ReportSimulationStats, ReportHIVByAgeAndGender
    from emodpy_hiv.reporters.reporters import ReportFilter, InsetChart

    reporters.add(InsetChart(reporters_object=reporters,
                             has_ip=None,                 # default
                             has_interventions=None,      # default
                             include_pregnancies=False,   # default
                             include_coital_acts=False,
                             event_channels_list=["NonDiseaseDeaths"]))
    reporters.add(ReportSimulationStats(reporters_object=reporters))
    reporters.add(ReportHIVByAgeAndGender(reporters_object=reporters,
                                          report_filter=ReportFilter(start_year=1985,
                                                                     end_year=2070),
                                          reporting_period=365 / 6,
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
    The following code is the code we used in Tutorial #1, but all bunched together.
    Please note the following:
    - The `sweep_run_number()` function was placed right after the reports.
    - `build_reports()` is called right after the creation of the EMODTask.
    - Logic is added after `experiment.run()` to check if the experiment 
      succeeded and call `process_results()'.
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

    zambia = cm.ZambiaForTraining
    task = emod_task.EMODTask.from_defaults(
        eradication_path=manifest.eradication_path,
        schema_path=manifest.schema_file,
        config_builder=zambia.build_config,
        campaign_builder=zambia.build_campaign,
        demographics_builder=zambia.build_demographics,
        report_builder=build_reports
    )

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # UPDATE- Select the following line given your platform
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # task.set_sif( path_to_sif=manifest.sif_path, platform=platform ) # SLURM
    # task.set_sif(path_to_sif=manifest.sif_path, platform=platform)  # COMPS

    builder = SimulationBuilder()
    builder.add_sweep_definition(sweep_run_number, [1, 2, 3])

    experiment = Experiment.from_builder(builder, task, name="Tutorial_2")

    experiment.run(wait_until_done=True, platform=platform)

    # Check result
    if experiment.succeeded:
        print(f"Experiment {experiment.uid} succeeded.")

        output_path = "tutorial_2_results"
        process_results(experiment, platform, output_path)

        print(f"Downloaded resuts for experiment {experiment.uid}.")

        plot_results(output_path)

        print(f"\nLook in the '{output_path}' directory for the plots of the data.")
    else:
        print(f"Experiment {experiment.uid} failed.\n")

    print("\nTutorial #2 is done.")
    return


if __name__ == "__main__":
    import emod_hiv.bootstrap as dtk

    dtk.setup(local_dir=manifest.executables_dir)

    run_experiment()
