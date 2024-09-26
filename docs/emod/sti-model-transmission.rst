============
Transmission
============

In the |EMOD_s| STI model, disease transmission can occur via two routes: sexual transmission or
vertical transmission (e.g. mother-to-child). The probability of transmission is calculated for each
discordant coital act and each childbirth.

.. add more.

Unlike the relationship parameters (see :doc:`sti-model-relationships`), parameters that govern
transmission are found in the configuration file (see :doc:`parameter-configuration` for a
complete list of configuration parameters). Parameters used to interrupt transmission will be found
in the campaign file (see :doc:`parameter-campaign` for a complete list of campaign events and
their parameters).



Sexual transmission
===================

Sexual transmission occurs between disease-discordant individuals that are paired in a relationship.
Transmission occurs via coital acts, so the probability of transmission will vary by relationship
type (see :doc:`sti-model-relationships` for information on relationship type, formation, and coital
frequencies).  In addition, there are numerous configurable factors that can influence the
transmission rate.

.. add more?

.. I think this following section can be generalized to be relevant for any STI

Base infectivity and its multipliers
-------------------------------------

Sexual transmission is configured through a base rate of infectivity, which is the transmission rate
per total coital acts. See :doc:`parameter-configuration-infectivity` parameters for more
information. This base rate can be modified through various multipliers and scalars, such that
transmission rates can vary by:

* **Age and gender.** The rate of male-to-female heterosexual transmission can be configured to be
  different than the rate of female-to-male heterosexual transmission. This gender bias in
  transmission can also be varied according to the age of the female partner. Both the gender and
  age multipliers on transmission are configured through a pair of matched arrays in the config.json
  file (**Male_to_Female_Relative_Infectivity_Ages** and
  **Male_to_Female_Relative_Infectivity_Multipliers**). Note that the lengths of both arrays must be
  equal, so each multiplier has a corresponding age. To remove age dependence, put just one value in
  each array. When multiple values are provided, the multiplier on the probability of transmission
  is linearly interpolated between the specified ages. Ages do not have to be integer values, and
  ages younger than the youngest specified age are assigned the value for the youngest specified age.
  Likewise, ages older than the oldest specified age are assigned the value for the oldest specified
  age.
* **Individuals.** The transmission rate can also be configured to be heterogeneous among individuals,
  with a multiplier on infectiousness sampled from a log normal scale. The multiplier is
  assigned to each individual at birth, and will be applied to every infection in that individual’s
  lifetime.
* **STI co-infection.** While the |EMOD_s| STI model does not support simultaneous transmission of
  more than one sexually transmitted infection, it does support the inclusion of non-transmitting
  co-infections that increase infectiousness and susceptibility for the transmission of the primary
  disease being modeled. Co-infection multipliers are set in the configuration file, while seeding
  or clearing co-infections is accomplished by using campaign interventions.
* **Condom usage.** Unlike the above multipliers, condom usage configures a blocking effect on
  transmission, such that the parameter represents the proportion of reduction in transmission. Each
  relationship type can have an independent probability of condom usage, which changes over time
  (recall that relationship types are configured in the demographics file; see :doc:`sti-model-relationships`
  for more information). The transmission blocking properties of condoms are then set in the
  config.json file. This blocking probability will be applied to condom use across all relationship
  types. Finally, it should be noted that condoms may also be distributed through a campaign
  intervention. For more information, see :doc:`parameter-campaign-individual-stibarrier`.

.. TODO check on the "individuals" section. In the HIV PDF, it uses "Heterogeneous_Infectiousness_Weibull_Heterogeneity"
.. and "Heterogeneous_Infectiousness_Weibull_Scale" but those params seem to only be in TBHIV...(pg. 64)


Note that in addition to configuration parameters, there are campaign interventions that will also
impact the transmission rate. For example, voluntary male medical circumcision, the use of
vaccines, and the use of treatments, can be distributed to individuals to
lower the transmission rate. For more information, see :doc:`parameter-campaign-individual-interventions`.


Vertical (mother-to-child)
==========================

The |EMOD_s| STI model supports vertical transmission of STIs via mother-to-child transmission (MTCT).
The model links the STI status of specific mothers with exposure to specific children, and does this
through the simulation of individual pregnancies. While overall fertility rates and birth rates are
configured in the demographics file, the transmission parameters governing MTCT are configured in
the configuration file.

To implement MTCT, maternal transmission must be enabled. This will allow infectious mothers to
transmit to their children. Additionally, there are parameters that can modify the transmission
probability. Finally, in order to simulate individual pregnancies, the **Birth_Rate_Dependence**
parameter must be set to INDIVIDUAL_PREGNANCIES_BY_AGE_AND_YEAR. For more information on these
parameters, see :doc:`parameter-configuration-population`.



.. will need figures and such!!


Note that there is a campaign intervention that can be configured to disrupt MTCT, the prevention
of mother-to-child transmission (PMTCT) intervention. For more information, see
:doc:`parameter-campaign-individual-pmtct`.
