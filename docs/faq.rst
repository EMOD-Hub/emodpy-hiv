===
FAQ
===

As you get started with |EMODPY_hiv|, you may have questions. The most common
questions are answered below. For questions related to functionality in
related packages, see the following documentation:

* :doc:`idmtools:faq` for |IT_s|
* :doc:`emod-api:faq` for |emod_api|
* :doc:`emodpy:faq` for |EMODPY_s|  

This section also includes a topic on troubleshooting when working with
|EMOD_s| and |EMODPY_hiv|.

.. contents:: Contents
   :local:

How do I set configuration parameters?
=========================================

Define your own parameter-setting function such as ``set_param_fn`` and pass
that function to the |EMODPY_s| task creator as the ``config_builder``
parameter. In that function, you can set the parameters directly. For
example:

.. literalinclude:: ../examples/start_here/example.py
   :lines: 49-66

See examples/start_here/example.py. for additional information.

If you prefer something more modular, you can call a function in a standalone
script/file that sets the configuration parameters.

Are there parameter defaults?
================================

Great question. If you don't set any configuration parameters, they will have
defaults based on the schema. There are not yet configuration parameter
defaults specific to HIV.

The HIV team has some demographic parameter defaults set using
:py:meth:`emodpy_hiv.demographics.DemographicsTemplates.AddDefaultSociety`.
They can be seen in demographics/DemographicsTemplates.py.

How do I create a minimal campaign that just seeds an outbreak?
===============================================================

You can use the following code::

<Coming Soon>

The code above creates a new intervention from the outbreak submodule that causes 1% of the population to
get an infection at timestep 365, and then adds that to the campaign. The only remaining thing to do is pass
the 'build_campaign' function to the task creator function ('from_defaults' ). To see the documentation for
the hiv outbreak module go :doc:`emodpy_hiv.campaign.individual_intervention`.

How do I give a therapeutic intervention, like ART, to people?
=================================================================

<Coming Soon>

How do I give out an intervention to people based on a trigger instead of at a particular time?
==================================================================================================

<Coming Soon>

What if I want to broadcast an event when I distribute the intervention?
===========================================================================

<Coming Soon>

What if I want to have a delay between the trigger (signal) and when the intervention is actually distributed?
=================================================================================================================

<Coming Soon>

What if I want to change someone's individual property?
==========================================================

<Coming Soon>

Now I want to distribute tests and distribute interventions to only those who test positive?
============================================================================================

<Coming Soon>

I pip installed |EMODPY_hiv|, but I want to make changes. How should I do that?
==================================================================================

Install at a command prompt using the following::

   pip install -e .

This method is the most popular and proven, though there are some other
options. Installing this way means that the |EMODPY_hiv| module in
site-packages actually points to the same code as you have checked out in git.

However, we aim to get the desired changes quickly tested and included in the
versioned module we release via pip install.

What's the command to get all the latest (stable) Python packages?
=====================================================================
::
    pip install emodpy_hiv --upgrade --upgrade-strategy eager


How do I install from conda?
=========================================

Once you have a conda environment created and activated, go ahead and conda install pip::

    conda install -n emodpy_env pip

And then pip install::

    pip install emodpy-hiv --extra-index-url https://packages.idmod.org/api/pypi/pypi-production/simple


What is the difference between "Transitory" and "Informal" relationships? 
=================================================================================
See :ref:`relationships`. (Transitory relationships are like “one night stands" or commercial relationships whereas Informal are generally intended to represent pre-marital or extra-marital relationships of some length.)
 

How do individual properties like "risk" change model behavior if they are just tags?
======================================================================================
The demographics parameters docs (:doc:`emod/model-properties`) say that individual properties, such as risk and accessibility, do not add logic, in and of themselves. Then how does one make people at "high risk" actually have more sexual partners and other actually more risky behaviors?

The answer is two-fold: 1) Risk is actually a "special IP" in HIV_SIM that we use in PFA configuration. See the :py:func:`emodpy_hiv.demographics.HIVDemographics.HIVDemographics.set_concurrency_params_by_type_and_risk` for example; and 2) Behavioral interventions can be targeted to people based on Risk.


What is the difference between individual-targeted interventions and node-targeted interventions?
====================================================================================================
See :doc:`emod/parameter-campaign-individual-interventions` and :doc:`emod/parameter-campaign-node-interventions`. Node interventions tend to be much rarer and are usually "meta-interventions" that are really ways of distributing individual interventions.

Why doesn't anything happen when I double-click |exe_s|?
========================================================

Unlike many executable files, |exe_s| does not open a software installer when double-clicked.
Instead, you must provide |exe_s| with various input files used to run a simulation and create
outputs. You can run simulations in a number of ways. The simplest way to learn about the model
is to run individual simulations at the command line. However, because |EMOD_s| is a stochastic
model, this is not feasible when you must run many simulations to create useful output for
statistical analysis. Once you advance to that stage, you will want to use other software tools
to run multiple simulations either locally or, more often, on an HPC cluster. For more
information, see :doc:`installation` and :doc:`emod/software-run-simulation`.


How do I plot my output? 
========================

|EMOD_s| does not produce plots of the data by default. Instead, it produces 
:term:`JSON (JavaScript Object Notation)` or CSV files that you can then parse and plot using
Python, MATLAB, R, or another programming language.

emodpy-hiv does provide some plotting utilities in :doc:`emodpy_hiv.plotting`.


Does your model include X?
==========================

Many aspects of disease dynamics are explicitly modeled in |EMOD_s|. Review :doc:`emod/parameter-overview` 
for an exhaustive list of all parameters that can be used to enable functionality in
|EMOD_s|. If you want to model something that isn't listed there, |EMOD_s| provides highly
flexible functionality with the individual and node property feature. These properties label
individuals or regional nodes in a simulation so you can change disease outbreaks, transmission
dynamics, behavior, or treatment based on the assigned values. For example, you can add
properties to represent vitamin deficiencies, comorbidities, and more. For more information, see
:doc:`emod/model-properties`.

If individual and node properties cannot incorporate the functionality you need, |EMOD_s| is
open-source software that can be extended to meet your needs. For more information, see 
:doc:`emod:dev-install-overview`.

Can I model regions, countries, provinces, or cities? 
=====================================================

|EMOD_s| uses nodes to represent geographic areas. Each :term:`node` has a population and
associated characteristics. Individuals and, if relevant, vectors can migrate between nodes.
Nodes can represent areas of any scale you like, from entire countries to individual
households. 


.. toctree::
   :maxdepth: 3
   :titlesonly:

   emod/troubleshooting
