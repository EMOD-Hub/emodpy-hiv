from emodpy_hiv.reporters.reporters import (ReportEventRecorder, ReportHIVByAgeAndGender, ReportHIVART,
                                            PropertyReport, ReportHIVMortality, ReportHIVInfection, ReportTransmission,
                                            ReportFilter, InsetChart, ReportRelationshipStart)


def reports_builder(reports):
    reports.add(ReportEventRecorder(reporters_object=reports,
                                    event_list=["NewInfectionEvent",
                                                "NewlySymptomatic",
                                                "STIDebut",
                                                "CSW_Uptake",
                                                "CSW_Dropout",
                                                "CaughtNonHIVSTI"]))
    reports.add(ReportHIVByAgeAndGender(reporters_object=reports,
                                        add_relationships=True,
                                        add_transmitters=True,
                                        collect_age_bins_data=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100],
                                        collect_circumcision_data=True,
                                        collect_gender_data=True,
                                        collect_hiv_data=True,
                                        collect_intervention_data=["Traditional_MC"],
                                        event_counter_list=["NewInfectionEvent"],
                                        report_filter=ReportFilter(start_year=1980,
                                                                   end_year=2199
                                                                   ),
                                        reporting_period=365))
    reports.add(ReportHIVART(reporters_object=reports))
    reports.add(InsetChart(reporters_object=reports,
                           event_channels_list=["NewInfectionEvent"]))
    reports.add(ReportHIVMortality(reporters_object=reports))
    reports.add(ReportHIVInfection(reporters_object=reports,
                                   report_filter=ReportFilter(start_year=1980,
                                                              end_year=2050)))
    reports.add(ReportTransmission(reporters_object=reports))
    reports.add(PropertyReport(reporters_object=reports))
    reports.add(ReportRelationshipStart(reporters_object=reports))
    return reports


def config_non_schema_params(conf):
    conf.parameters["Enable_Continuous_Log_Flushing"] = 0
    conf.parameters["logLevel_default"] = "WARNING"
    # conf.parameters.alpha__logLevel_Memory = "WARNING"
    # conf.parameters.logLevel_InfectionHIV = "ERROR"
    # conf.parameters.logLevel_Instrumentation = "ERROR"
    # conf.parameters.logLevel_Memory = "ERROR"
    # conf.parameters.logLevel_OutbreakIndividual = "ERROR"
    # conf.parameters.logLevel_Simulation = "ERROR"
    # conf.parameters.logLevel_SusceptibilityHIV = "ERROR"


def set_config(conf):
    # 'Useless' params (not actually used by HIV) -- will be gone after merging in multi-parent depends-on solution from G-O.
    conf.parameters.Incubation_Period_Distribution = 'CONSTANT_DISTRIBUTION'
    conf.parameters.Incubation_Period_Constant = 0

    # HIV Science Params
    conf.parameters.Simulation_Type = "HIV_SIM"
    conf.parameters.Base_Infectivity = 0.002327836
    conf.parameters.CD4_Post_Infection_Weibull_Heterogeneity = 0
    conf.parameters.CD4_Post_Infection_Weibull_Scale = 540.55
    conf.parameters.Coital_Dilution_Factor_2_Partners = 0.75
    conf.parameters.Coital_Dilution_Factor_3_Partners = 0.6
    conf.parameters.Coital_Dilution_Factor_4_Plus_Partners = 0.45
    conf.parameters.Days_Between_Symptomatic_And_Death_Weibull_Heterogeneity = 0.5
    conf.parameters.Days_Between_Symptomatic_And_Death_Weibull_Scale = 618.341625
    conf.parameters.Enable_Maternal_Infection_Transmission = 1
    conf.parameters.HIV_Age_Max_for_Adult_Age_Dependent_Survival = 50
    conf.parameters.Male_To_Female_Relative_Infectivity_Ages = [0, 15, 25]
    conf.parameters.Male_To_Female_Relative_Infectivity_Multipliers = [4.684, 4.684, 2.962]
    conf.parameters.Maternal_Infection_Transmission_Probability = 0.3
    conf.parameters.Maternal_Transmission_ART_Multiplier = 0.03334
    conf.parameters.Min_Days_Between_Adding_Relationships = 0
    conf.parameters.PFA_Burnin_Duration_In_Days = 5475
    conf.parameters.STI_Coinfection_Acquisition_Multiplier = 5.5
    conf.parameters.STI_Coinfection_Transmission_Multiplier = 5.5
    conf.parameters.Sexual_Debut_Age_Female_Weibull_Heterogeneity = 0.299281948
    conf.parameters.Sexual_Debut_Age_Female_Weibull_Scale = 16.34494123
    conf.parameters.Sexual_Debut_Age_Male_Weibull_Heterogeneity = 0.053712118
    conf.parameters.Sexual_Debut_Age_Male_Weibull_Scale = 17.72188303

    # Simulation Setup
    conf.parameters.x_Base_Population = 0.05
    conf.parameters.Individual_Sampling_Type = "FIXED_SAMPLING"
    conf.parameters.Load_Balance_Filename = ""
    conf.parameters.Node_Grid_Size = 0.009
    conf.parameters.Random_Number_Generator_Policy = "ONE_PER_NODE"
    conf.parameters.Random_Number_Generator_Type = "USE_AES_COUNTER"

    config_non_schema_params(conf)
