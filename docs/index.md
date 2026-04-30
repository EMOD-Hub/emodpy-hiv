---
title: Home
---

# Welcome to emodpy-hiv

This documentation set describes how to use Epidemiological MODeling software (EMOD) for simulating HIV transmission
and interventions and how to use emodpy-hiv for creating input files, submitting 
simulation jobs to a compute cluster, and more.

## Epidemiological MODeling software (EMOD)

The Institute for Disease Modeling (IDM) develops disease modeling software that is thoroughly tested and shared with the
research community to advance the understanding of disease dynamics. This software helps determine
the combination of health policies and intervention strategies that can lead to disease eradication.
If you encounter any issues while using the software, please post on our [discussion board][discussions].

EMOD, is an *agent-based model* (ABM) that simulates the
simultaneous interactions of agents in an effort to recreate complex phenomena. Each human agent can be assigned a variety of "properties" (for example, age, gender, etc.), and
their behavior and interactions with one another are determined by using decision rules. These
models have strong predictive power and are able to leverage spatial and temporal dynamics.

EMOD is also *stochastic*, meaning that there is randomness built into the model. Infection
and recovery processes are represented as probabilistic Bernoulli random draws. In other words, when
a susceptible person comes into contact with a pathogen, they are not guaranteed to become infected.
Instead, you can imagine flipping a coin that has a λ chance of coming up tails S(t) times, and for
every person who gets a "head" you say they are infected. This randomness better approximates what
happens in reality. It also means that you must run many simulations to determine the probability of particular outcomes. 

The EMOD documentation is broken up into disease-specific sets that provide
guidance for researchers modeling particular diseases. The documentation contains only the
parameters, output reports, and other components of the model that are available to use for HIV modeling.

## emodpy-hiv

emodpy-hiv is a collection of Python scripts and utilities created to
streamline user interactions with EMOD and idmtools for modeling generic
diseases. Much of the functionality is inherited from [emod-api][emod-api-docs] and [emodpy][emodpy-docs].

Additional information about how to use idmtools can be found in the [idmtools documentation][idmtools].
Additional information about EMOD HIV parameters can be found in [parameter overview](emod/parameter-overview.md).
