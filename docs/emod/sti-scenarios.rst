=======================
STI model scenarios
=======================


The |EMOD_s| STI model is explained in detail in :doc:`sti-model-overview`. While the various
components that comprise the model are explained with examples, it may be more useful to learn the
model through hands-on implementation. The following sections will introduce sets of example files
that illustrate how the STI model works on particular topics. All files are available in a
downloadable `EMOD scenarios`_ zip file and, in addition to the explanations below, each scenario will
have a more detailed README file to cover relevant information.

For more information on the software architecture and inheritance, see :doc:`software-overview`.



.. include figures and graphs on this page??


Relationship networks
=====================

To use a contact network as the basis for disease transmission, the **Simulation_Type** should be
set to STI_SIM.

In the `EMOD scenarios`_ > Scenarios > STI > Relationship_networks folder, you will find sets of
files to run simulations modeling contact networks. These simulations do not include disease
outbreaks or subsequent transmission, but will demonstrate how to configure relationship networks
beginning with eligibility for pair formation, preference for particular partner ages, relationship
types and durations, concurrency in relationships, and coital frequency and dilution.

.. include graph on p. 12 of pdf for age of sexual debut?

.. base files used for age of sexual debut, and then from 1-c; used concurrency campaign too.



.. _EMOD scenarios: https://github.com/InstituteforDiseaseModeling/docs-emod-scenarios/releases