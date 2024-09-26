============
ReportHIVART
============

The ART initiation and discontinuation report (ReportHIVART.csv) provides information on individuals
at time of ART initiation and discontinuation, including ID, age, gender, and CD4 count
at ART initiation.


Configuration
=============

To generate the report, set the configuration parameter **Report_HIV_ART** to 1.


Output file data
================

The output report will contain the following information.

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    Year, float, "The time of the event (ART initiation or discontinuation) in units of calendar year, including fractions of years up to two decimal places."
    Node_ID, integer, "The identification number of the node."
    ID, integer, "The individual's unique identifying number."
    Gender, boolean, "Identifies the individual's gender: 0 is assigned to males, 1 is assigned to females."
    Age, integer, "The age of the individual in units of days. Divide by 365 to obtain age in years."
    CD4, float, "The last CD4 count taken when the person started or stopped ART, as measured with the **HIVDrawBlood** intervention. -1 indicates that the person has not had their CD4 count measured using **HIVDrawBlood**."
    StartingART, boolean, "Identifies the ART initiation or discontinuation event: 1 indicates the individual has initiated ART, 0 indicates they are discontinuing ART."




Example
=======

The following is an example of a ReportHIVART.csv report:

.. csv-table::
    :file: ReportHIVART-Example.csv