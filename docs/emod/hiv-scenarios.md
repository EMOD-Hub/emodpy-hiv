# HIV model scenarios

The EMOD HIV model is explained in detail in [hiv-model-overview](hiv-model-overview.md). While the various
components that comprise the model are explained with examples, it may be more useful to learn the
model through hands-on implementation. The following sections will introduce sets of example files
that illustrate how the HIV model works on particular topics. All files are available in a
downloadable `EMOD scenarios`_ zip file and, in addition to the explanations below, each scenario will
have a more detailed README file to cover relevant information. Within the
EMODScenarios > Scenarios > HIV folder is an Excel worksheet titled "Weibull.xlsx," which
can be used to explore how Weibull parameters influence the shape of the distribution. Note that
Weibull parameters are used often in the HIV model, so it will be useful to to understand the
factors governing their shape.

For more information on the software architecture and inheritance, see [software-overview](software-overview.md).

## HIV-specific biology

HIV parameters are added to the STI relationship networks when the **Simulation_Type** is set to
HIV_SIM. Specifically, this adds transmission rates, mortality rates, and the evolution of
biomarkers such as CD4 count specific to HIV-infected individuals. These factors impact the survival
of HIV+ individuals according to their age, disease state, co-infection status, and use of
antiretroviral therapy (ART) or other interventions.

In the `EMOD scenarios`_ > Scenarios > HIV > HIVBiology folder you will find files to run an
HIV simulation. In the README file, you will find instructions on how to configure baseline HIV
transmission, how to change survival time for children and adults, how CD4 count and WHO stage
progress, and how to configure heterogeneity in CD4 count.

## Transmission

HIV can be transmitted via two routes: sexually through a relationship network, or vertically by
mother-to-child transmission. In EMOD, to initially seed a population with disease, you must use
the campaign interventions **Outbreak** or **OutbreakIndividual**  (see
[parameter-campaign-node-outbreak](parameter-campaign-node-outbreak.md) or [parameter-campaign-individual-outbreakindividual](parameter-campaign-individual-outbreakindividual.md)
for more information). These two campaign intervention classes work by "distributing" HIV to the
configured population. After the initial seeding, transmission can occur via the sexual or vertical
routes.

In the `EMOD scenarios`_ > Scenarios > HIV > Transmission folder you will find files to run an
HIV simulation. In the README file, you will find instructions on how to configure sexual
transmission, vertical transmission, and how to initiate co-infections.

For detailed configuration instructions and example exercises to try, see the README in the
Transmission folder.

## Health care

Health care is critical for individuals with HIV. In EMOD, a system of health care can be
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
