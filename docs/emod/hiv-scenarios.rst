===================
HIV model scenarios
===================

The |EMOD_s| HIV model is explained in detail in :doc:`hiv-model-overview`. While the various
components that comprise the model are explained with examples, it may be more useful to learn the
model through hands-on implementation. The following sections will introduce sets of example files
that illustrate how the HIV model works on particular topics. All files are available in a
downloadable `EMOD scenarios`_ zip file and, in addition to the explanations below, each scenario will
have a more detailed README file to cover relevant information. Within the
EMODScenarios > Scenarios > HIV folder is an Excel worksheet titled "Weibull.xlsx," which
can be used to explore how Weibull parameters influence the shape of the distribution. Note that
Weibull parameters are used often in the HIV model, so it will be useful to to understand the
factors governing their shape.


For more information on the software architecture and inheritance, see :doc:`software-overview`.



.. include figures and graphs on this page??

.. contents:: Contents
   :local:


HIV-specific biology
====================

HIV parameters are added to the STI relationship networks when the **Simulation_Type** is set to
HIV_SIM. Specifically, this adds transmission rates, mortality rates, and the evolution of
biomarkers such as CD4 count specific to HIV-infected individuals. These factors impact the survival
of HIV+ individuals according to their age, disease state, co-infection status, and use of
antiretroviral therapy (ART) or other interventions.

In the `EMOD scenarios`_ > Scenarios > HIV > HIVBiology folder you will find files to run an
HIV simulation. In the README file, you will find instructions on how to configure baseline HIV
transmission, how to change survival time for children and adults, how CD4 count and WHO stage
progress, and how to configure heterogeneity in CD4 count.


.. base files: config, campaign from 2A. Additional campaign files from each specific scenario.


Transmission
============

HIV can be transmitted via two routes: sexually through a relationship network, or vertically by
mother-to-child transmission. In |EMOD_s|, to initially seed a population with disease, you must use
the campaign interventions **Outbreak** or **OutbreakIndividual**  (see
:doc:`parameter-campaign-node-outbreak` or :doc:`parameter-campaign-individual-outbreakindividual`
for more information). These two campaign intervention classes work by "distributing" HIV to the
configured population. After the initial seeding, transmission can occur via the sexual or vertical
routes.

In the `EMOD scenarios`_ > Scenarios > HIV > Transmission folder you will find files to run an
HIV simulation. In the README file, you will find instructions on how to configure sexual
transmission, vertical transmission, and how to initiate co-infections.

For detailed configuration instructions and example exercises to try, see the README in the
Transmission folder.


.. using the config file from 3-a, campaign from 2-a as the base files. Note: set enable maternal
.. trans to 0 to start with.

.. added campaign file from 3-e for coinfections



.. the following scenarios don't have files yet!

Health care
===========

Health care is critical for individuals with HIV. In |EMOD_s|, a system of health care can be
created by using multiple interventions. Interventions can be linked to create a network of actions
and results, where the outcome of one intervention can initiate the start of the next. This creates
a cascade of care, where individuals enter the system due to a positive diagnostic test, and then
move through the healthcare system created, with options for follow-up tests, and treatment options.
Some individuals will exit the care system (e.g. "lost to follow up"), and in some cases, individuals
that exit the care system may re-initiate care and return.

In the `EMOD scenarios`_ > Scenarios > HIV > Health_care folder, you will find files to run
simulations with a configured cascade of care. In the README file, you will be provided with
instructions for working with cascades of care.

Care systems can range from simple diagnostics to a series of complex interventions, and the files
within this section highlight these important aspects. Several interventions involved with care are
highlighted, namely:

* Voluntary male medical circumcision (VMMC)

* Prevention of mother-to-child transmission (PMTCT)

* Antiretroviral treatment (ART)

* Steps in the care process, such as testing, staging, linking to care, treatment eligibility,
  and how to prevent individuals from entering care cascades multiple times.

.. instructions on how to create a care cascade, how individuals become eligible for treatment, how to
.. initiate retention in the care system, how to re-initiate care for those that have exited, and how
.. to configure delays in care.


.. Current base files are the 4-3 Health Care Model Baseline files. Also using 4-2-2-c for ART eligibility.

.. Would like to include something about retention, but tbh I can't figure out how they are configuring
.. dropout rates. I don't see how they're specifying the retention rates (campaign file from 5-4-a)

.. also did not include the files for re-initiation of care or delaying/removing delays to care (those seem
.. pretty clear by using parameter settings). re-initiation of care (5-5, a-b), -Delays in care (5-6, a,b)







.. Interventions
.. =============

.. Tests and diagnostics
.. ---------------------

.. -section 4-2-2...(a, b, c)
.. -decisions: 4-2-3 (random: a; CD4 count: b; calendar time: c; age: d; sexual debut status: e)
.. -section 4-3-5 (symptom-driven: a; pediactric: b; antenatal: c; routine/voluntary: d)
.. -one time testing campaign: 5-3-a
.. -regular annual testing: 5-3-b
.. community testing: 5-3-c, d


.. Antiretroviral therapy (ART)
.. ----------------------------

.. -survival time on ART (2-f)
.. -reconstitution of cd4 on ART (2-g)
.. -evo of cd4 on/off ART
.. -effect of ART on sexual transmission (3-c)
.. -section 4-2-1-a
.. -section 4-3-4
.. -ART staging...4-3-6
.. -linking to ART 4-3-7
.. -section 4-3-9
.. -age-targeted 5-2-d


.. PrEP
.. ----

.. -PrEP & vaccines (3-f)
.. -section 5-7 (uniform efficacy: a; heterogeneous efficacy or adherence: b; long-acting: c)

.. PMTCT
.. -----

.. -section 4-2-1-c
.. -section 4-3-3
.. -second half of 3-g

.. used files from 3-g


.. Voluntary male medical circumcision (VMMC)
.. ------------------------------------------

.. -effect of vmmc on transmission (3-b)
.. -section 4-2-1-b
.. -section 4-3-2
.. -one-time campaign: 5-1-a
.. -one-time, age-targeted: 5-1-b
.. -continuous availability: 5-1-c
.. -age-triggered: 5-1-d
.. -driven by other tests: 5-1-e
.. -expansion of hiv testing & vmmc: 5-1-f


.. Condom use
.. ----------

.. -section 4-2-1-e
.. -effect of condoms on sexual transmission (3-d)






.. _EMOD scenarios: https://github.com/InstituteforDiseaseModeling/docs-emod-scenarios/releases