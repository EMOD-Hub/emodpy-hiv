===================
ReportEventRecorder
===================

The health events and interventions report (ReportEventRecorder.csv) provides information on each
individual's demographics and health status at the time of an event. Additionally, it is possible to
see the value of specific **IndividualProperties**, as assigned in the demographics file (see
:ref:`demo-properties` for more information).

This report is highly customizable; see the `Configuration`_ section, below, for details and instructions.
Disease-specific information and examples are provided at the end of page.


Configuration
=============

To generate this report, the following parameters must be configured in the config.json file (applies
to all simulation types):


.. csv-table::
    :header: Parameter name, Data type, Min, Max, Default, Description
    :widths: 8, 5, 5, 5, 5, 20

    Report_Event_Recorder,"boolean","0","1","0","Set to 1 to generate the report."
    Report_Event_Recorder_Events,"array of strings","NA","NA","[]","The list of events to include or exclude in the output report, based on how **Report_Event_Recorder_Ignore_Events_In_List** is set. See :doc:`parameter-campaign-event-list` for a list of all possible built-in events. **Custom_Individual_Events** may also be included. Warning: If the list is empty and **Report_Event_Recorder_Ignore_Events_In_List** is set to 0, no events will be returned."
    Report_Event_Recorder_Ignore_Events_In_List,"boolean","0","1","0","If set to false (0), only the events listed in **Report_Event_Recorder_Events** will be included in the output report. If set to true (1), only the events listed in **Report_Event_Recorder_Events** will be excluded, and all other events will be included. To return all events from the simulation, set this value to 1 and leave the the **Report_Event_Recorder_Events** array empty."
    Report_Event_Recorder_Individual_Properties,"array of strings","NA","NA","[]","An array of optional individual property (IP) keys to be added to the report. One column will be added for each IP Key listed, indicating the individual's value for that IP Key at the time of the event. See :doc:`model-properties` for details on setting individual properties."
    Report_Event_Recorder_Start_Day,"float","0","3.40282e+38","0","The day of the simulation to start collecting data."
    Report_Event_Recorder_End_Day,"float","0","3.40282e+38","3.40282e+38","The day of the simulation to stop collecting data."
    Report_Event_Recorder_Node_IDs_Of_Interest,"array of integers","0","2.14748e+09","[]","Data will be collected for the nodes in this list. Leave the array empty (default value) to collect data on all nodes."
    Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest, string, NA, NA, \"\", "If the string is not empty, then the recorder will add the PropertyChange event to the list of events that the report is listening to. However, it will only record the events where the property changed the value of the given key."
    Report_Event_Recorder_Min_Age_Years,"float","0","9.3228e+35","0","Minimum age in years of people to collect data on."
    Report_Event_Recorder_Max_Age_Years,"float","0","9.3228e+35","9.3228e+35","Maximum age in years of people to collect data on."
    Report_Event_Recorder_Must_Have_IP_Key_Value,"string","NA","NA",\"\","An individual property (IP) Key:Value pair that an individual must have in order to be included in the report. Leave the string empty (default value) to not include IPs in the selection criteria. See :doc:`model-properties` for more information."
    Report_Event_Recorder_Must_Have_Intervention,"string","NA","NA",\"\","The name of the intervention that the individual must have in order to be included in the report. Leave the string empty (default value) to not include interventions in the selection criteria. See :doc:`parameter-campaign-individual-interventions` for more information."

.. code-block:: json

    {
        "Report_Event_Recorder": 1,
        "Report_Event_Recorder_Events": [],
        "Report_Event_Recorder_Ignore_Events_In_List": 1,
        "Report_Event_Recorder_Individual_Properties": ["Risk"],
        "Report_Event_Recorder_Start_Day": 1,
        "Report_Event_Recorder_End_Day": 300,
        "Report_Event_Recorder_Node_IDs_Of_Interest": [ 1, 2, 3 ],
        "Report_Event_Recorder_PropertyChange_IP_Key_Of_Interest": "",
        "Report_Event_Recorder_Min_Age_Years": 20,
        "Report_Event_Recorder_Max_Age_Years": 60,
        "Report_Event_Recorder_Must_Have_IP_Key_Value": "Risk:HIGH",
        "Report_Event_Recorder_Must_Have_Intervention": "",
    }


Output file data
================

The report contains the following data channels for HIV simulations.

.. csv-table::
    :header: Data channel, Data type, Description
    :widths: 10, 5, 20

    Time, float, "The time of the event, in days."
    Node_ID, integer, "The identification number of the node."
    Event_Name, string, "The event being logged. If **Report_Event_Recorder_Ignore_Events_In_List** is set to 0, then the event name will be one of the ones listed under **Report_Event_Recorder_Events**. Otherwise, it will be the name of any other event that occurs and is not listed under **Report_Event_Recorder_Events**."
    Individual_ID, integer, The individual's unique identifying number
    Age, integer, "The age of the individual in units of days. Divide by 365 to obtain age in years."
    Gender, character, "The gender of the individual: ""M"" for male, or ""F"" for female."
    Infected, boolean, "Describes whether the individual is infected or not; 0 when not infected, 1 for infected."
    Infectiousness, float, "A value ranging from 0 to 1 that indicates how infectious an individual is, with 0 = not infectious and 1 = very infectious. HIV and malaria simulation types have specific definitions listed below."
    "<IP Key>", string, "An additional column will be added to the report for each IP Key listed in **Report_Event_Recorder_Individual_Properties**. The values shown in each column will be the value for the indicated key, for that individual, at the time of the event."
    Year, float, "The time of the event in units of calendar year, including fractions of years up to two decimal places."
    Infectiousness, float, "The probability of HIV transmission per coital act, including intrahost factors like disease stage and ART, but excluding condoms. (Channel is included in all simulations, but definition varies by disease.)"
    HasHIV, character, "Indicates whether or not the individual is infected with HIV: ""N"" if not infected, ""Y"" if infected."
    OnART, character, "Indicates whether or not the individual is on ART: ""N"" if not on ART, ""Y"" if the individual is on ART."
    CD4, float, "The individual's current CD4 count, regardless of when CD4 testing was performed."
    WHO_Stage, float, "The individual's WHO stage, linearly interpolated between integer values. Round down to obtain the integer value for the WHO clinical stage. Uninfected individuals will be assigned a value of -1."
    HIV_Stage, enum, "Indicates the individual's HIV stage. Possible values are: NOT_INFECTED, ACUTE, LATENT, AIDS, ON_ART."
    InterventionStatus, string, "The value of the individual's **InterventionStatus** individual property at the time of the event. If **InterventionStatus** has not been configured, then the value will be ""None."""



Example
=======

The following is an example of a ReportEventRecorder.csv report from an HIV simulation:

.. csv-table::
    :header-rows: 1
    :file: ReportEventRecorder-Example.csv
