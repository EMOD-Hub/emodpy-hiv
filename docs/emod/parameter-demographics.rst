=======================
Demographics parameters
=======================

.. include:: ../reuse/demo-param-intro.txt

The tables below contain only parameters available when using the HIV :term:`simulation type`.

.. include:: ../reuse/warning-case.txt

.. contents:: Contents
   :local:

.. _demo-metadata:

Metadata
========

.. include:: ../reuse/demo-metadata.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-metadata-hiv.csv

.. _demo-properties:

NodeProperties and IndividualProperties
=======================================

.. include:: ../reuse/demo-properties.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-properties-hiv.csv


.. _demo-nodeattributes:

NodeAttributes
==============

.. include:: ../reuse/demo-nodeattributes.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-nodeattributes-hiv.csv



.. _demo-individualattributes:

IndividualAttributes
====================

.. include:: ../reuse/demo-individualattributes.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-individualattributes-hiv.csv

.. _demo-simpledistro:

Simple distributions
--------------------

.. include:: ../reuse/demo-simpledistro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-simpledistro-hiv.csv

.. _demo-complexdistro:

Complex distributions
---------------------

.. include:: ../reuse/demo-complexdistro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-complexdistro-hiv.csv

.. _demo-society:

Society
=======

The **Society** section defines the behavioral-based parameters of a relationship type in the STI
and HIV models, such as rates of partnership formation, partner preference, relationship duration,
or concurrent partnerships. It must contain the four sets of relationship type parameters and the
**Concurrency_Configuration** section. Note that the name used for each relationship type is only a
guide; |EMOD_s| does not include specific logic for each type and the settings for each depend only
upon the parameters you provide.

The section for each relationship type must include the **Relationship_Parameters**,
**Pair_Formation_Parameters**, and **Concurrency_Parameters** sections. These sections define the
settings for the specific relationship type they are nested under.

The **Concurrency_Configuration** section defines how the simultaneous relationship parameters are
used across all relationship types.

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-society-hiv.csv

.. _demo-concurrency-config:

Concurrency_Configuration
-------------------------

The **Concurrency_Configuration** section is at the same level as each relationship type section and
defines how the simultaneous relationship parameters are used across all relationship types. For
example, how flags that allow an individual to seek out different types of extra-relational
partnerships are distributed.


.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-concurrency-config-hiv.csv

.. _demo-relationship:

Relationship_Parameters
-----------------------

The **Relationship_Parameters** section defines basic attributes such as relationship duration, what
happens if one member of a relationship migrates, and condom usage.

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-relationship-hiv.csv

.. _demo-pair-formation:

Pair_Formation_Parameters
-------------------------

The **Pair_Formation_Parameters** section defines the rate at which new relationships are formed and
partnership preference using the main pair forming algorithm that finds potential
partners based on their age and the **Joint_Probabilities** matrix.

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-pairing-hiv.csv


.. _demo-assortivity:

Assortivity
~~~~~~~~~~~

The **Assortivity** section refines who partners with whom. After the main pair forming algorithm
reduces the set of potential partners to a subset based on age, **Assortivity** allows for selection
based on other criteria.


.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-assortivity-hiv.csv

.. _demo-concurrency-param:

Concurrency_Parameters
----------------------

The **Concurrency_Configuration** section at the top level of the **Society** section defines the
simultaneous relationship parameters for super spreader probabilities, whether simultaneous
relationships type probabilities are independent or correlated, and, if correlated, the order of the
relationship types. If you want to base concurrency on **IndividualProperties** settings, you can
list the relevant properties in **Individual_Property_Name**, using "NONE" if the properties are
irrelevant for concurrency.

Under each relationship type, the **Concurrency_Parameters** section defines simultaneous relationship
parameters for that relationship type. In this section, all parameters should be nested under the
name of the individual property relevant for setting concurrency. Again, if the properties are irrelevant,
use "NONE".

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/demo-concurrency-params-hiv.csv