# ReportEventRecorder

The health events and interventions report (ReportEventRecorder.csv) provides information on each
individual's demographics and health status at the time of an event. Additionally, it is possible to
see the value of specific **IndividualProperties**, as assigned in the demographics file (see
[NodeProperties and IndividualProperties](parameter-demographics.md#nodeproperties-and-individualproperties) for more information).

This report is highly customizable; see the [Configuration](#configuration) section, below, for details and instructions.
Disease-specific information and examples are provided at the end of page.

## Configuration

To generate this report, the following parameters must be configured in the config.json file (applies
to all simulation types):

{{ read_csv('../csv/report-event-recorder.csv', keep_default_na=False) }}

```json
{
    "Report_Event_Recorder": 1,
    "Report_Event_Recorder_Events": [],
    "Report_Event_Recorder_Ignore_Events_In_List": 1,
    "Report_Event_Recorder_Individual_Properties": ["Risk"],
    "Report_Event_Recorder_Start_Day": 1,
    "Report_Event_Recorder_End_Day": 300,
    "Report_Event_Recorder_Start_Year": 2000,
    "Report_Event_Recorder_End_Year": 2050,
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

| Data channel | Data type | Description |
|---|---|---|
| Time | float | The time of the event, in days. |
| Node_ID | integer | The identification number of the node. |
| Event_Name | string | The event being logged. If **Report_Event_Recorder_Ignore_Events_In_List** is set to 0, then the event name will be one of the ones listed under **Report_Event_Recorder_Events**. Otherwise, it will be the name of any other event that occurs and is not listed under **Report_Event_Recorder_Events**. |
| Individual_ID | integer | The individual's unique identifying number. |
| Age | integer | The age of the individual in units of days. Divide by 365 to obtain age in years. |
| Gender | character | The gender of the individual: "M" for male, or "F" for female. |
| Infected | boolean | Describes whether the individual is infected or not; 0 when not infected, 1 for infected. |
| Infectiousness | float | A value ranging from 0 to 1 that indicates how infectious an individual is, with 0 = not infectious and 1 = very infectious. HIV and malaria simulation types have specific definitions listed below. |
| &lt;IP Key&gt; | string | An additional column will be added to the report for each IP Key listed in **Report_Event_Recorder_Individual_Properties**. The values shown in each column will be the value for the indicated key, for that individual, at the time of the event. |
| Year | float | The time of the event in units of calendar year, including fractions of years up to two decimal places. |
| Infectiousness | float | The probability of HIV transmission per coital act, including intrahost factors like disease stage and ART, but excluding condoms. (Channel is included in all simulations, but definition varies by disease.) |
| HasHIV | character | Indicates whether or not the individual is infected with HIV: "N" if not infected, "Y" if infected. |
| OnART | character | Indicates whether or not the individual is on ART: "N" if not on ART, "Y" if the individual is on ART. |
| CD4 | float | The individual's current CD4 count, regardless of when CD4 testing was performed. |
| WHO_Stage | float | The individual's WHO stage, linearly interpolated between integer values. Round down to obtain the integer value for the WHO clinical stage. Uninfected individuals will be assigned a value of -1. |
| HIV_Stage | enum | Indicates the individual's HIV stage. Possible values are: NOT_INFECTED, ACUTE, LATENT, AIDS, ON_ART. |
| InterventionStatus | string | The value of the individual's **InterventionStatus** individual property at the time of the event. If **InterventionStatus** has not been configured, then the value will be "None." |

## Example

The following is an example of a ReportEventRecorder.csv report from an HIV simulation:

{{ read_csv('ReportEventRecorder-Example.csv', keep_default_na=False) }}
