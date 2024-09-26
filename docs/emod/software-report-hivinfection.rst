==================
ReportHIVInfection
==================

The HIV disease progression report (ReportHIVInfection.csv) provides information on each individual's disease state at each time step, including age, gender, CD4 count, survival prognosis, ART status, and factors impacting transmission and acquisition.


Configuration
=============

To generate the report, the following parameters must be configured in the config.json file:

.. csv-table::
    :header: Parameter, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Report_HIV_Infection, boolean, NA, NA, 0, "Set this to 1 to generate the report."
    Report_HIV_Infection_Start_Year, float, 1900, 2200, 1900, "Simulation time in years to start collecting data."
    Report_HIV_Infection_Stop_Year, float, 1900, 2200, 2200, "Simulation time in years to start collecting data."


.. code-block:: json

    {
        "Report_HIV_Infection": 1,
        "Report_HIV_Infection_Start_Year": 1940,
        "Report_HIV_Infection_Stop_Year": 2000
    }


Output file data
================

The output report will contain the following information.

Data columns
------------

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    Year, float, "Simulation time in years, including fractions of years."
    Node_ID, integer, "The identification number of the node."
    Id, integer, "The unique identification number of the individual."
    MCWeight, integer, "Not currently supported. This column will always show a Monte Carlo weight of 1."
    Age, float, "The age of the individual in years, including fractions of years."
    Gender, boolean, "Identifies the individual's gender: 0 is assigned to males, 1 is assigned to females."
    getProbMaternalTransmission, float, "The hypothetical probability of mother-to-child transmission (MTCT), if the individual were to give birth at the present time and not receive any interventions such as **PMTCT** or **AntiretroviralTherapy**. Not applicable for males or for females of non-childbearing age."
    TimeSinceHIV, float, "The number of days since the individual became infected. Note: If the individual was infected by an **OutbreakIndividual** intervention with the **Incubation_Period_Override** parameter set to 0, the infected date will be randomly set in the past (uniformly selected from the amount of time until death). TimeSinceHIV will count accordingly from the 'historic' infection date."
    CD4count, float, "The current CD4 count, regardless of when CD4 testing was performed."
    PrognosisCompletedFraction, float, "The proportion of the total untreated HIV survival time that has already been lived; only relevant when the individual is not on ART."
    Prognosis, float, "The remaining untreated survival time until AIDS-related death; only relevant when the individual is not on ART."
    Stage, integer, "The individual's disease stage. Possible values are:

    .. hlist::
        :columns: 1

        * 0 = Uninfected
        * 1 = Untreated acute HIV infection
        * 2 = Untreated latent HIV infection
        * 3 = Untreated late/AIDS stage
        * 4 = On ART"
    ViralLoad, float, Not currently supported.
    WHOStage, float, "The individual's WHO stage, linearly interpolated between integer values. Round down to obtain the integer value for the WHO clinical stage. Uninfected individuals will be assigned a value of -1."
    Infectiousness, float, "Describes the individual's infectiousness, which depends on the disease stage and ART status, and includes effects of heterogeneous infectiousness."
    ModAcquire, float, "Multiplicative modifier on disease acquisition; will be set to 1 by default for HIV, but can be impacted by the **IndividualImmunityChanger** intervention or by setting **Enable_Maternal_Protection** to 1 in the config.json file."
    ModTransmit, float, "Multiplicative modifier on disease transmission; will be set to 1 by default for HIV, but can be impacted by the **IndividualImmunityChanger** intervention."
    ModMortality, float, "Multiplicative modifier on disease mortality; will be set to 1 by default for HIV, but can be impacted by the **IndividualImmunityChanger** intervention."
    ArtStatus, integer, "Describes the individual's ART status. Possible values are:

    .. hlist::
        :columns: 1

        * 1 = The individual is not currently receiving ART.
        * 5 = The individual is on ART, but their viral load is not yet suppressed.
        * 6 = The individual is on ART, and their viral load is suppressed.
        * 7 = The individual is on ART, but is experiencing virological failure.
        * 8 = The individual has had poor adherence to ART.
        * 9 = The individual has dropped out of ART."
    InfectivitySuppression, float, "The multiplier acting on **Base_Infectivity** to determine the per-act transmission probability of a virally suppressed HIV-positive individual. This can be reduced from **ART_Viral_Suppression_Multiplier** due to **ARTBasic**'s **Days_To_Achieve_Viral_Suppression**."
    DurationOnArt, integer, "The number of days since the individual most recently started ART. Set to -1 if they are not on ART."
    ProbMaternalTransmissionModifier, float, "The better maternal transmission multiplier provided by **PMTCT**, or zero."
    OnArtQuery, boolean, "Describes whether the individual is on ART or not: 0 if individual is not on ART, and 1 if they are."
    CoInfectiveTransmissionFactor, float, "If the person has an STI co-infection (set by the **ModifyStiCoInfectionStatus** intervention), then this will be the value from the parameter **STI_Coinfection_Transmission_Multiplier**. Otherwise, the value will be 1."
    CoInfectiveAcquisitionFactor, float, "If the person has an STI co-infection (set by the **ModifyStiCoInfectionStatus** intervention), then this will be the value from the parameter **STI_Coinfection_Acquisition_Multiplier**. Otherwise, the value will be 1."
    DebutAge, float, "The age of sexual debut in days."
    IsCircumcised, boolean, "Indicates whether or not the individual is circumcised (only applicable to males): 0 for not circumcised (and females), 1 for circumcised."
    InterventionReducedAcquire, float, "The multiplier, based on interventions like **SimpleVaccine**, used to reduce the probability that an individual will acquire an infection."
    InterventionReducedTransmit, float, "The multiplier, based on interventions like **SimpleVaccine**, used to reduce the probability that an individual will transmit an infection."
    InterventionReducedMortality, float, "The multiplier, based on interventions like **SimpleVaccine**, used to reduce the probability that an individual will die due to an infection."



Example
=======

The following is an example of a ReportHIVInfection.csv file.

.. csv-table::
    :header: Year, Node_ID, Id, MCWeight, Age, Gender, getProbMaternalTransmission, TimeSinceHIV, CD4count, PrognosisCompletedFraction, Prognosis, Stage, ViralLoad, WHOStage, Infectiousness, ModAcquire, ModTransmit, ModMortality, ArtStatus, InfectivitySuppression, DurationOnART, ProbMaternalTransmissionModifier, OnArtQuery, CoInfectiveTransmissionFactor, CoInfectiveAcquisitionFactor, DebutAge, IsCircumcised, InterventionReducedAcquire, InterventionReducedTransmit, InterventionReducedMortality
    :file: ReportHIVInfection-Example.csv
