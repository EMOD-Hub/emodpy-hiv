===============================================
ReferenceTrackingEventCoordinatorTrackingConfig
===============================================

The **ReferenceTrackingEventCoordinatorTrackingConfig** coordinator class defines a particular prevalence of 
an individual-level attribute that should be present in a population over time, and a corresponding intervention 
that will cause individuals to acquire that attribute. The coordinator tracks the actual prevalence of that attribute against 
the desired prevalence; it will poll the population of nodes it has been assigned to determine how many people 
have the attribute. When coverage is less than the desired prevalence, it will distribute enough of the designated 
intervention to reach the desired prevalence. This coordinator is similar to the **ReferenceTrackingEventCoordinator**, but 
allows an *attribute* in the population to be polled, not only the intervention itself having been received. This allows for
tracking overall coverage when, potentially, multiple routes exist for individuals to have acquired the same target attribute.

.. include:: ../reuse/warning-case.txt

.. include:: ../reuse/campaign-example-intro.txt

.. csv-table::
    :header: Parameter, Data type, Minimum, Maximum, Default, Description, Example
    :widths: 10, 5, 5, 5, 5, 20, 5
    :file: ../csv/campaign-referencetrackingeventcoordinatortrackingconfig.csv

Example: Use **Tracking_Config** to look at men who are not circumcised (by any route, not only via the **MaleCircumcision** 
intervention); if coverage is below the target level at the time of polling, apply the **MaleCircumcision** 
intervention to uncircumcised men to reach the target coverage.

.. literalinclude:: ../json/campaign-referencetrackingeventcoordinatortrackingconfig.json
   :language: json