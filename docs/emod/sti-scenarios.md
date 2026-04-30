# STI model scenarios

The EMOD STI model is explained in detail in [sti-model-overview](sti-model-overview.md). While the various
components that comprise the model are explained with examples, it may be more useful to learn the
model through hands-on implementation. The following sections will introduce sets of example files
that illustrate how the STI model works on particular topics. All files are available in a
downloadable `EMOD scenarios` zip file and, in addition to the explanations below, each scenario will
have a more detailed README file to cover relevant information.

For more information on the software architecture and inheritance, see [software-overview](software-overview.md).

## Relationship networks

To use a contact network as the basis for disease transmission, the **Simulation_Type** should be
set to STI_SIM.

In the `EMOD scenarios` > Scenarios > STI > Relationship_networks folder, you will find sets of
files to run simulations modeling contact networks. These simulations do not include disease
outbreaks or subsequent transmission, but will demonstrate how to configure relationship networks
beginning with eligibility for pair formation, preference for particular partner ages, relationship
types and durations, concurrency in relationships, and coital frequency and dilution.
