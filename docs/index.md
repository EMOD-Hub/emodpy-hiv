---
title: Home
---

# Welcome to emodpy-hiv

This documentation set describes how to use Epidemiological MODeling software (EMOD) for simulating HIV transmission
and interventions and how to use emodpy-hiv for creating model configuration files,
submitting simulation jobs to a compute cluster, and more.

## Epidemiological MODeling software (EMOD)

EMOD is a stochastic, agent-based model developed by the Institute for Disease Modeling (IDM) that simulates
sexual and vertical HIV transmission. It is used to evaluate the cost and impact of treatment
and control programs across national-level epidemics. See [Overview](emod/overview.md) for a full
description of the model.

If you encounter any issues while using the software, please visit our [discussion board][discussions].

## emodpy-hiv

emodpy-hiv is the primary interface for working with EMOD. It provides the tools to configure
the model, define interventions, set up simulation runs, and analyze results — everything a
researcher needs to go from a scientific question to a completed simulation.

## emodpy-workflow

[emodpy-workflow](https://emod.idmod.org/emodpy-workflow/) is built on top of emodpy-hiv and
provides an alternative approach for working with EMOD. It is a collection of commands and
interfaces intended to support data-driven scientific computing workflows. Its core standardizes
the process of creating, calibrating, running, and obtaining output from EMOD-HIV model
scenarios, making it easier for teams to collaborate and work with each other's projects.
Users who previously ran EMOD-HIV using DtkTools will find emodpy-workflow's approach more
familiar.
