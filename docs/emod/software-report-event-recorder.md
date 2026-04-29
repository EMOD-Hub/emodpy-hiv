# ReportEventRecorder

The health events and interventions report (ReportEventRecorder.csv) provides information on each
individual's demographics and health status at the time of an event. Additionally, it is possible to
see the value of specific **IndividualProperties**, as assigned in the demographics file (see
[demo-properties](#demo-properties) for more information).

This report is highly customizable; see the `Configuration`_ section, below, for details and instructions.
Disease-specific information and examples are provided at the end of page.

## Configuration

To generate this report, the following parameters must be configured in the config.json file (applies
to all simulation types):

```json
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
```

## Output file data

The report contains the following data channels for HIV simulations.

## Example

The following is an example of a ReportEventRecorder.csv report from an HIV simulation:

*See parameter table: [ReportEventRecorder-Example.csv](ReportEventRecorder-Example.csv)*
