============
HIVMortality
============

The HIV mortality report (HIVMortality.csv) provides information about individuals at the time of
their death, including disease status, CD4 count, medical history, and relationship history.



Configuration
=============

To generate the report, set the **Report_HIV_Mortality** parameter to 1 in the config.json file.


Output file data
================

The output report will contain the following information.

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    Node_ID, integer, "The identification number of the node."
    id, integer, "The unique identification number of the individual."
    Death_time, float, "Simulation time, in days, when the individual died."
    Death_was_HIV_cause, boolean, "Indicates whether or not the death was due to HIV infection: 0 if death was due to background mortality, and 1 if death was due to HIV."
    Gender, boolean, "Identifies the individual's gender: 0 is assigned to males, 1 is assigned to females."
    Age, float, "The age of the individual, in years, including fractions of years up to four decimal places."
    Num_rels_just_prior_to_death, integer, "The number of relationships in which the individual was participating just prior to death."
    Num_rels_lifetime, integer, "The total number of lifetime relationships for the individual."
    HIV_disease_state_just_prior_to_death, integer, "Describes the disease state prior to the individual's death. Possible values are:

    .. hlist::
        :columns: 1

        * 0 = Uninfected
        * 1 = Untreated acute HIV infection
        * 2 = Untreated latent HIV infection
        * 3 = Untreated late/AIDS stage
        * 4 = On ART
    "
    Years_since_infection, float, "The number of years since the individual was most recently infected. This can be reset if the infection is suppressed by the **AntiretroviralTherapy** or **ARTMortalityTable** interventions."
    CD4_count_first_recorded, float, "The first CD4 count ever recorded with CD4 testing (via the **HIVDrawBlood** intervention). The value will be -1 if the person never received an **HIVDrawBlood** intervention."
    CD4_count_last_recorded, float, "The most recent CD4 count recorded with CD4 testing (via the **HIVDrawBlood** intervention). The value will be -1 if the person never received an **HIVDrawBlood** intervention."
    CD4_count_current, float, "The actual CD4 count at the time of death (regardless of when CD4 testing was performed)."
    Days_since_CD4_blood_draw, integer, "The time lag between the last CD4 test (via the **HIVBloodDraw** intervention) and the time of death."
    Total_number_of_times_initiating_ART, integer, The number of lifetime ART initiations. ART initiation and adherence are determined by the **AntiretroviralTherapy** and **ARTMortalityTable** interventions.
    Total_years_on_ART, float, "The cumulative number of years on ART, including fractions of years."
    Years_since_first_ART_initiation, float, "The number of years since first ART initiation, including fractions of years."
    Years_since_most_recent_ART_initiation, float, "The number of years since the most recent ART initiation, including fractions of years."
    ART_status_just_prior_to_death, enum, "Describes the individual's ART eligibility status at the time of death. Possible values are:

    .. hlist::
        :columns: 1

        * WITHOUT_ART_UNQALIFIED
        * WITHOUT_ART_QUALIFIED_BY_BASELINE
        * ON_PRE_ART
        * LOST_TO_FOLLOW_UP
        * ON_ART_BUT_NOT_VL_SUPPRESSED
        * ON_VL_SUPPRESSED
        * ON_BUT_FAILING
        * ON_BUT_ADHERENCE_POOR
        * OFF_BY_DROPOUT

    "
    Intervention_Status, string, "The value of the **InterventionStatus** individual property (IP) for the person that died, at the time of death. If **InterventionStatus** has not been configured, then the value will be ""None."" See :doc:`model-properties` for information on configuring interventions."
    Ever_tested, boolean, "Describes whether or not the individual has ever received a diagnostic via the **HIVRapidHIVDiagnostic** intervention: 0 if the individual has not, and 1 if they have. Note that other diagnostics (such as **SimpleDiagnostic** and **HIVSimpleDiagnostic**) do not count toward Ever_tested."
    Ever_tested_positive, boolean, "Describes whether or not the individual has ever received a positive HIV test via the **HIVRapidHIVDiagnostic** intervention: 0 if the individual has not, and 1 if they have. Note that other diagnostics (such as **SimpleDiagnostic** and **HIVSimpleDiagnostic**) do not count toward Ever_tested_positive."
    Ever_received_CD4_result, boolean, "Describes whether or not individuals have received a CD4 test via the **HIVDrawBlood** intervention: 0 if the individual has not, and 1 if they have."
    Ever_in_ART, boolean, "Describes whether the individual has ever received ART via the **AntiretroviralTherapy** or **ARTMortalityTable** interventions: 0 if the individual has not, and 1 if they have."
    Currently_in_ART, boolean, "Describes whether or not the individual was receiving ART via the **AntiretroviralTherapy** or **ARTMortalityTable** interventions at the time of their death: 0 if the individual was not, and 1 if they were. Individual adherence to ART may be modified by the **ARTMortalityTable** intervention."





Example
=======

The following is an example of a HIVMortality.csv report:

.. csv-table::
    :file: HIVMortality.csv