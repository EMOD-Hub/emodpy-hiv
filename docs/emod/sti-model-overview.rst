==================
STI model overview
==================

The |EMOD_s| STI model is an agent-based stochastic simulator of sexual and vertical disease
transmission. The model utilizes microsolvers to combine detailed information on contact networks, pair formation, and human population dynamics. |EMOD_s| can be calibrated to particular
geographic locations, and the :term:`microsolver` framework enables the model's functionality to be
highly modifiable. To use the STI model, set the configuration parameter **Simulation_Type** to
STI_SIM.

The STI transmission mode framework enables
person-to-person transmission through a network of relationships or contact networks, each of
which has a specific transmitter and recipient of every transmission event. To organize the
networks, individuals form one or more relationships that are remembered over time.

Preference for partners is configurable through the model’s input files. Inside the model, the
"supply and demand" for types of partners is balanced by a pair formation algorithm (PFA) that, if
desired, can dynamically adjust the rates of relationship formation in each demographic category to
produce a constant mixing pattern, even with demographic changes in the population. Alternatively,
the dynamic adjustments can be turned off to allow mixing patterns to change in response to
demographic changes. For more information on the PFA, see :doc:`sti-model-relationships`.

The contact networks formed within the STI model are driven by the behavioral parameters found in
the **Society** section of the demographics file. These parameters control pair formation,
relationship types, and level of relationship concurrency. For more information about this section
of the demographics file, see :ref:`demo-society`. 

Because the STI model is built around person-to-person contact networks, human relationships impact
nearly every aspect of model functionality. For example, migration is supported in the STI model, but
is more complicated than in other disease types, as now it impacts the relationships experienced
by the migrating individual (see :doc:`sti-model-relationships` for more information).

The following pages describe the structure of the STI model and explore the model components. Additionally,
the specifics of the HIV model, which is based on the STI model, are discussed in detail in the articles
`Bershteyn, Klein, Wenger, and Eckhoff, arXiv.org <https://arxiv.org/pdf/1206.3720.pdf>`__, and
`Klein, Bershteyn, and Eckhoff, AIDS 2014 <https://journals.lww.com/aidsonline/Abstract/2014/01001/Dropout_and_re_enrollment__implications_for.6.aspx>`__.

.. toctree::
   :maxdepth: 3
   :titlesonly:

   sti-model-relationships
   sti-model-transmission
