import json

def compare_intervention_name(iv_config_1: dict, iv_config_2: dict) -> int:
    """
    Compare two intervention names.
    Returns:
        -1 if iv_config_1 < iv_config_2, 0 if equal, 1 if iv_config_1 > iv_config_2
    """
    iv_name_1 = iv_config_1.get('Intervention_Name', None)
    iv_name_2 = iv_config_2.get('Intervention_Name', None)

    if iv_name_1 is None and iv_name_2 is None:
        return 0
    elif iv_name_1 is None:
        return -1
    elif iv_name_2 is None:
        return 1
    elif iv_name_1 < iv_name_2:
        return -1
    elif iv_name_1 > iv_name_2:
        return 1
    else:
        return 0


def convert_DelayedIntervention(iv_config: dict):
    """
    The old code had HIVDelayedIntervention while the new code uses
    DelayedIntervention with a nested BroadcastEvent class.  This converts
    the DelayedInterventions to be HIVDelayedIntervention.
    """
    if iv_config['class'] == 'DelayedIntervention':
        ac_iv_config_list = iv_config['Actual_IndividualIntervention_Configs']
        if len(ac_iv_config_list) == 1 and ac_iv_config_list[0]['class'] == 'BroadcastEvent':
            iv_config['class'] = 'HIVDelayedIntervention'
            iv_config["Broadcast_Event"] = ac_iv_config_list[0]['Broadcast_Event']
            iv_config.pop("Actual_IndividualIntervention_Configs", None)


def compare_intervention_config(iv_config_1: dict, iv_config_2: dict) -> int:
    """
    Compare two intervention configurations by class name and then intervention name.
    """
    convert_DelayedIntervention(iv_config_1)
    convert_DelayedIntervention(iv_config_2)

    if iv_config_1['class'] < iv_config_2['class']:
        return -1
    elif iv_config_1['class'] > iv_config_2['class']:
        return 1
    else:
        return compare_intervention_name(iv_config_1, iv_config_2)


def compare_sec(event1: dict, event2: dict) -> int:
    """
    Compares the campaign events for two StandardInterventionDistributionEventCoordinators.
    First sort on the intervention configuration, but have special handling if both SECs
    have NLHTIV.
    """
    ec_config_1 = event1['Event_Coordinator_Config']
    ec_config_2 = event2['Event_Coordinator_Config']
    iv_config_1 = ec_config_1['Intervention_Config']
    iv_config_2 = ec_config_2['Intervention_Config']
    
    if iv_config_1['class'] < iv_config_2['class']:
        return -1
    elif iv_config_1['class'] > iv_config_2['class']:
        return 1
    elif iv_config_1['class'] == 'NodeLevelHealthTriggeredIV':
        tcl_event_1 = iv_config_1['Trigger_Condition_List'][0]
        tcl_event_2 = iv_config_2['Trigger_Condition_List'][0]
        #print(tcl_event_1, tcl_event_2)
        if tcl_event_1 < tcl_event_2:
            #print(tcl_event_1)
            return -1
        elif tcl_event_1 > tcl_event_2:
            #print(tcl_event_2)
            return 1
        else:
            ac_iv_config_1 = iv_config_1['Actual_IndividualIntervention_Config']
            ac_iv_config_2 = iv_config_2['Actual_IndividualIntervention_Config']
            cmp = compare_intervention_config(ac_iv_config_1, ac_iv_config_2)
            if cmp == 0:
                node_set_1 = event1["Nodeset_Config"]
                node_set_2 = event2["Nodeset_Config"]
                return compare_node_set(node_set_1, node_set_2)
            else:
                return cmp
    else:
        cmp = compare_intervention_name(iv_config_1, iv_config_2)
        if cmp == 0:
            node_set_1 = event1["Nodeset_Config"]
            node_set_2 = event2["Nodeset_Config"]
            return compare_node_set(node_set_1, node_set_2)
        else:
            return cmp


def compare_node_set(node_set_1: dict, node_set_2: dict) -> int:
    """
    Sorting by node id is helpful when everything else is similar.
    """
    if node_set_1['class'] < node_set_2['class']:
        return -1
    elif node_set_1['class'] > node_set_2['class']:
        return 1
    elif node_set_1['class'] == 'NodeSetNodeList':
        node_list_1 = node_set_1.get('Node_List', [])
        node_list_2 = node_set_2.get('Node_List', [])
        if len(node_list_1) < len(node_list_2):
            return -1
        elif len(node_list_1) > len(node_list_2):
            return 1
        else:
            for i in range(len(node_list_1)):
                if node_list_1[i] < node_list_2[i]:
                    return -1
                elif node_list_1[i] > node_list_2[i]:
                    return 1
            return 0
    else:
        return 0


def compare_nchooser(event1: dict, event2: dict) -> int:
    """
    Compares the campaign events for two NChooserEventCoordinators.
    First sort on the intervention configuration, then sort on the nodeset configuration.
    Added this logic because the first campaign file for Zambia had an nchooser
    handing out MaleCircumcisions but were different for each node.  This would
    get them in order by node.
    """
    ec_config_1 = event1['Event_Coordinator_Config']
    ec_config_2 = event2['Event_Coordinator_Config']
    iv_config_1 = ec_config_1['Intervention_Config']
    iv_config_2 = ec_config_2['Intervention_Config']

    cmp = compare_intervention_config(iv_config_1, iv_config_2)
    if cmp == 0:
        node_set_1 = event1["Nodeset_Config"]
        node_set_2 = event2["Nodeset_Config"]
        return compare_node_set(node_set_1, node_set_2)
    else:
        return cmp


def compare_tracker(event1: dict, event2: dict) -> int:
    """
    Compares the campaign events for two ReferenceTrackingEventCoordinators.
    First sort on whether the target gender is different and then sort on the
    intervention configuration.
    """
    ec_config_1 = event1['Event_Coordinator_Config']
    ec_config_2 = event2['Event_Coordinator_Config']

    if ec_config_1['Target_Gender'] < ec_config_2['Target_Gender']:
        return -1
    elif ec_config_1['Target_Gender'] > ec_config_2['Target_Gender']:
        return 1
    else:
        iv_config_1 = ec_config_1['Intervention_Config']
        iv_config_2 = ec_config_2['Intervention_Config']
        return compare_intervention_config(iv_config_1, iv_config_2)


def compare_event_coordinator(event1: dict, event2: dict) -> int:
    """
    Compare two campaign events by their coordinator

    Returns:
        -1 if event1 < event2, 0 if equal, 1 if event1 > event2
    """
    ec_config_1 = event1['Event_Coordinator_Config']
    ec_config_2 = event2['Event_Coordinator_Config']
    
    if ec_config_1['class'] < ec_config_2['class']:
        return -1
    elif ec_config_1['class'] > ec_config_2['class']:
        return 1
    elif ec_config_1['class'] == 'StandardInterventionDistributionEventCoordinator':
        return compare_sec(event1, event2)
    elif ec_config_1['class'].startswith('NChooserEventCoordinator'):
        return compare_nchooser(event1, event2)
    elif ec_config_1['class'].startswith('ReferenceTrackingEventCoordinator'):
        return compare_tracker(event1, event2)
    else:
        return 0

def compare_campaign_event(event1: dict, event2: dict) -> int:
    """
    Compare two campaign events

    Returns:
        -1 if event1 < event2, 0 if equal, 1 if event1 > event2
    """
    if event1['class'] < event2['class']:
        return -1
    elif event1['class'] > event2['class']:
        return 1
    elif event1['class'] == 'CampaignEventByYear':
        if event1['Start_Year'] < event2['Start_Year']:
            return -1
        elif event1['Start_Year'] > event2['Start_Year']:
            return 1
        else:
            return compare_event_coordinator(event1, event2)
    elif event1['class'] == 'CampaignEvent':
        start_day_1 = event1.get('Start_Day', None)
        start_day_2 = event2.get('Start_Day', None)
        if start_day_1 is None and start_day_2 is None:
            return compare_event_coordinator(event1, event2)
        elif start_day_1 is None:
            return -1
        elif start_day_2 is None:
            return 1
        elif start_day_1 < start_day_2:
            return -1
        elif start_day_1 > start_day_2:
            return 1
        else:
            return compare_event_coordinator(event1, event2)


def sort_names_and_probabilities(iv_config: dict):
    """
    Sorting the names and probabilities makes sure that two campaign files
    have them in the same order.  If the numbers are exactly the same,
    being in the same order will make it obvious.
    """
    if iv_config['class'] == 'HIVRandomChoice':
        names = iv_config.get("Choice_Names", [])
        probs = iv_config.get("Choice_Probabilities", [])
        for i in range(len(probs) - 1):
            for j in range(i + 1, len(probs)):
                if probs[i] < probs[j]:
                    # Swap probabilities
                    probs[i], probs[j] = probs[j], probs[i]
                    # Swap names
                    names[i], names[j] = names[j], names[i]


def remove_defaults_from_intervention(iv_config: dict):
    """
    Remove default values from the intervention configuration.
    """

    # common parameters and their defaults
    if 'Dont_Allow_Duplicates' in iv_config and iv_config['Dont_Allow_Duplicates'] == 0:
        iv_config.pop("Dont_Allow_Duplicates", None)
    if 'New_Property_Value' in iv_config and iv_config['New_Property_Value'] == "":
        iv_config.pop("New_Property_Value", None)
    if 'Intervention_Name' in iv_config and iv_config['Intervention_Name'] == iv_config['class']:
        iv_config.pop("Intervention_Name", None)
    if 'Disqualifying_Properties' in iv_config and len(iv_config['Disqualifying_Properties']) == 0:
        iv_config.pop("Disqualifying_Properties", None)
    if 'Event_Or_Config' in iv_config:
        iv_config.pop("Event_Or_Config", None)
    
    # consider the specific intervention classes
    if iv_config['class'] == 'DelayedIntervention':
        if 'Coverage' in iv_config and iv_config['Coverage'] == 1:
            iv_config.pop("Coverage", None)
        if 'Delay_Period_Min' in iv_config and iv_config['Delay_Period_Min'] == 0:
            iv_config.pop("Delay_Period_Min", None)
        if (('Intervention_Name' in iv_config) and
            ((iv_config['Intervention_Name'] == 'DelayedIntervention') or 
             (iv_config['Intervention_Name'] == 'HIVDelayedIntervention'))):
            iv_config.pop("Intervention_Name", None)
        ac_iv_config_list = iv_config['Actual_IndividualIntervention_Configs']
        for config in ac_iv_config_list:
            remove_defaults_from_intervention(config)

    elif iv_config['class'] == 'HIVDelayedIntervention':
        if 'Coverage' in iv_config and iv_config['Coverage'] == 1:
            iv_config.pop("Coverage", None)
        if 'Delay_Period_Min' in iv_config and iv_config['Delay_Period_Min'] == 0:
            iv_config.pop("Delay_Period_Min", None)
        if 'Delay_Period_Min' in iv_config and iv_config['Delay_Period_Min'] == 0:
            iv_config.pop("Delay_Period_Min", None)
        if (('Intervention_Name' in iv_config) and
            ((iv_config['Intervention_Name'] == 'DelayedIntervention') or 
             (iv_config['Intervention_Name'] == 'HIVDelayedIntervention'))):
            iv_config.pop("Intervention_Name", None)
            
    elif iv_config['class'] == 'HIVRapidHIVDiagnostic':
        if 'Base_Sensitivity' in iv_config and iv_config['Base_Sensitivity'] == 1:
            iv_config.pop("Base_Sensitivity", None)
        if 'Base_Specificity' in iv_config and iv_config['Base_Specificity'] == 1:
            iv_config.pop("Base_Specificity", None)
        if 'Cost_To_Consumer' in iv_config and iv_config['Cost_To_Consumer'] == 1:
            iv_config.pop("Cost_To_Consumer", None)
        if 'Days_To_Diagnosis' in iv_config and iv_config['Days_To_Diagnosis'] == 0:
            iv_config.pop("Days_To_Diagnosis", None)
        if 'Enable_Is_Symptomatic' in iv_config and iv_config['Enable_Is_Symptomatic'] == 0:
            iv_config.pop("Enable_Is_Symptomatic", None)
        if 'Negative_Diagnosis_Event' in iv_config and iv_config['Negative_Diagnosis_Event'] == "":
            iv_config.pop("Negative_Diagnosis_Event", None)
        if 'Probability_Received_Result' in iv_config and iv_config['Probability_Received_Result'] == 1:
            iv_config.pop("Probability_Received_Result", None)
        if 'Sensitivity_Type' in iv_config and iv_config['Sensitivity_Type'] == "SINGLE_VALUE":
            iv_config.pop("Sensitivity_Type", None)

    elif iv_config['class'] == 'HIVSigmoidByYearAndSexDiagnostic':
        # "Female_Multiplier": 1,
        if 'Female_Multiplier' in iv_config and iv_config['Female_Multiplier'] == 1:
            iv_config.pop("Female_Multiplier", None)
        if 'Ramp_Min' in iv_config and iv_config['Ramp_Min'] == 0:
            iv_config.pop("Ramp_Min", None)
        if 'Ramp_Max' in iv_config and iv_config['Ramp_Max'] == 1:
            iv_config.pop("Ramp_Max", None)
        if 'Ramp_Rate' in iv_config and iv_config['Ramp_Rate'] == 1:
            iv_config.pop("Ramp_Rate", None)

    elif iv_config['class'] == 'HIVMuxer':
        if 'Broadcast_On_Expiration_Event' in iv_config and iv_config['Broadcast_On_Expiration_Event'] == "":
            iv_config.pop("Broadcast_On_Expiration_Event", None)
        if 'Coverage' in iv_config and iv_config['Coverage'] == 1:
            iv_config.pop("Coverage", None)
        if 'Expiration_Period' in iv_config and iv_config['Expiration_Period'] == 3.40282e+38:
            iv_config.pop("Expiration_Period", None)
        if 'Max_Entries' in iv_config and iv_config['Max_Entries'] == 1:
            iv_config.pop("Max_Entries", None)

    elif ((iv_config['class'] == 'HIVARTStagingCD4AgnosticDiagnostic') or
          (iv_config['class'] == 'HIVARTStagingByCD4Diagnostic')):
        if 'Adult_Treatment_Age' in iv_config and iv_config['Adult_Treatment_Age'] == 5:
            iv_config.pop("Adult_Treatment_Age", None)
        if 'Individual_Property_Active_TB_Key' in iv_config and iv_config['Individual_Property_Active_TB_Key'] == "UNINITIALIZED":
            iv_config.pop("Individual_Property_Active_TB_Key", None)
        if 'Individual_Property_Active_TB_Value' in iv_config and iv_config['Individual_Property_Active_TB_Value'] == "UNINITIALIZED":
            iv_config.pop("Individual_Property_Active_TB_Value", None)

    elif iv_config['class'] == 'HIVPiecewiseByYearAndSexDiagnostic':
        if 'Default_Value' in iv_config and iv_config['Default_Value'] == 0:
            iv_config.pop("Default_Value", None)
        if 'Interpolation_Order' in iv_config and iv_config['Interpolation_Order'] == 0:
            iv_config.pop("Interpolation_Order", None)
        if 'Female_Multiplier' in iv_config and iv_config['Female_Multiplier'] == 1:
            iv_config.pop("Female_Multiplier", None)
        if 'Negative_Diagnosis_Event' in iv_config and iv_config['Negative_Diagnosis_Event'] == "":
            iv_config.pop("Negative_Diagnosis_Event", None)

    elif iv_config['class'] == 'PropertyValueChanger':
        if 'Daily_Probability' in iv_config and iv_config['Daily_Probability'] == 1:
            iv_config.pop("Daily_Probability", None)
        if 'Maximum_Duration' in iv_config and iv_config['Maximum_Duration'] == 3.40282e+38:
            iv_config.pop("Maximum_Duration", None)
        if 'Revert' in iv_config and iv_config['Revert'] == 0:
            iv_config.pop("Revert", None)

    elif iv_config['class'] == 'MaleCircumcision':
        if 'Apply_If_Higher_Reduced_Acquire' in iv_config and iv_config['Apply_If_Higher_Reduced_Acquire'] == 0:
            iv_config.pop("Apply_If_Higher_Reduced_Acquire", None)
        if 'Circumcision_Reduced_Acquire' in iv_config and iv_config['Circumcision_Reduced_Acquire'] == 0.6:
            iv_config.pop("Circumcision_Reduced_Acquire", None)

    elif iv_config['class'] == 'HIVRandomChoice':
        # sorting makes these easier to compare
        sort_names_and_probabilities(iv_config)

    elif iv_config['class'] == 'OutbreakIndividual':
        if 'Antigen' in iv_config and iv_config['Antigen'] == 0:
            iv_config.pop("Antigen", None)
        if 'Genome' in iv_config and iv_config['Genome'] == 0:
            iv_config.pop("Genome", None)
        if 'Ignore_Immunity' in iv_config and iv_config['Ignore_Immunity'] == 1:
            iv_config.pop("Ignore_Immunity", None)
        if 'Outbreak_Source' in iv_config:
            iv_config.pop("Outbreak_Source", None)
        if 'Event_Name' in iv_config:
            iv_config.pop("Event_Name", None)


def remove_defaults_from_xxx_target_demographic(config: dict):
    """
    Remove the defaults that are common to SEC and NLHTIV
    """
    if 'Property_Restrictions' in config and len(config['Property_Restrictions']) == 0:
        config.pop("Property_Restrictions", None)
    if 'Property_Restrictions_Within_Node' in config and len(config['Property_Restrictions_Within_Node']) == 0:
        config.pop("Property_Restrictions_Within_Node", None)
    if 'Targeting_Config' in config and len(config['Targeting_Config']) == 0:
        config.pop("Targeting_Config", None)
    if 'Demographic_Coverage' in config and config['Demographic_Coverage'] == 1:
        config.pop("Demographic_Coverage", None)
    if 'Target_Residents_Only' in config and config['Target_Residents_Only'] == 0:
        config.pop("Target_Residents_Only", None)
    if 'Target_Demographic' in config and config['Target_Demographic'] == "Everyone":
        config.pop("Target_Demographic", None)
    if 'Target_Gender' in config and config['Target_Gender'] == "All":
        config.pop("Target_Gender", None)
    if 'Travel_Linked' in config:
        config.pop("Travel_Linked", None)


def remove_defaults_from_sec(ec_config: dict):
    """
    Remove default values from the StandardInterventionDistributionEventCoordinator configuration
    and its associated intervention configurations
    """

    # SEC specific defaults
    if 'Node_Property_Restrictions' in ec_config and len(ec_config['Node_Property_Restrictions']) == 0:
        ec_config.pop("Node_Property_Restrictions", None)
    if 'Number_Repetitions' in ec_config and ec_config['Number_Repetitions'] == 1:
        ec_config.pop("Number_Repetitions", None)
    if 'Timesteps_Between_Repetitions' in ec_config and ec_config['Timesteps_Between_Repetitions'] == -1:
        ec_config.pop("Timesteps_Between_Repetitions", None)
    if 'Individual_Selection_Type' in ec_config and ec_config['Individual_Selection_Type'] == "DEMOGRAPHIC_COVERAGE":
        ec_config.pop("Individual_Selection_Type", None)
    
    # defaults common with NLHTIV
    remove_defaults_from_xxx_target_demographic(ec_config)

    iv_config = ec_config.get('Intervention_Config', {})
    remove_defaults_from_intervention(iv_config)

    if iv_config.get('class', None) == 'NodeLevelHealthTriggeredIV':
        remove_defaults_from_xxx_target_demographic(iv_config)

        # NLHTIV specific defaults
        if 'Blackout_Event_Trigger' in iv_config and iv_config['Blackout_Event_Trigger'] == "":
            iv_config.pop("Blackout_Event_Trigger", None)
        if 'Blackout_On_First_Occurrence' in iv_config and iv_config['Blackout_On_First_Occurrence'] == 0:
            iv_config.pop("Blackout_On_First_Occurrence", None)
        if 'Blackout_Period' in iv_config and iv_config['Blackout_Period'] == 0:
            iv_config.pop("Blackout_Period", None)
        if 'Distribute_On_Return_Home' in iv_config and iv_config['Distribute_On_Return_Home'] == 0:
            iv_config.pop("Distribute_On_Return_Home", None)
        if 'Duration' in iv_config and iv_config['Duration'] == -1:
            iv_config.pop("Duration", None)
        if 'Node_Property_Restrictions' in iv_config and len(iv_config['Node_Property_Restrictions']) == 0:
            iv_config.pop("Node_Property_Restrictions", None)

        ac_iv_config = iv_config['Actual_IndividualIntervention_Config']
        remove_defaults_from_intervention(ac_iv_config)


def fix_nchooser_number_format(ec_config: dict):
    """
    The Nchoosers used for distributing VMMC had lots of places where it was comparing
    15 vs 15.0 or 14.999 vs 14.999999.  This made comparisons difficult.
    """
    distributions = ec_config.get("Distributions", [])
    for dist in distributions:
        for age_range in dist.get("Age_Ranges_Years", []):
            age_range["Max"] = int(age_range["Max"]) + 0.999
            age_range["Min"] = int(age_range["Min"])
        dist["End_Year"] = int(dist["End_Year"]) + 0.999
        num_targeted = ec_config.get("Num_Targeted", [])
        if len(num_targeted) == 0:
            dist.pop("Num_Targeted", None)


def remove_defaults(campaign_json: dict):
    """
    Remove default values from the campaign JSON.  This makes the resulting file smaller,
    easier to read, and easier to compare with other campaign files.
    """
    for event in campaign_json.get("Events", []):
        ec_config = event.get("Event_Coordinator_Config", {})
        if ec_config['class'] == 'StandardInterventionDistributionEventCoordinator':
            remove_defaults_from_sec(ec_config)
        elif ec_config['class'].startswith('NChooserEventCoordinator'):
            fix_nchooser_number_format(ec_config)
            iv_config = ec_config["Intervention_Config"]
            remove_defaults_from_intervention(iv_config)


def sort_campaign(campaign_json: dict):
    """
    Sorts the campaign events in the given campaign JSON.
    The sorting is done based on the event class, start year, and event coordinator configuration."""

    # -------------------------------------------------------------------------------------
    # --- NOTE:  I'm using my own bubble sort implementation here because I wasn't getting
    # --- what I wanted with the built-in sorted() function.
    # -------------------------------------------------------------------------------------

    n = len(campaign_json["Events"])
    for i in range(n - 1):
        for j in range(i+1,n):
            #print(f"Comparing event {i} with event {j}")
            event_i = campaign_json["Events"][i]
            event_j = campaign_json["Events"][j]
            cmp = compare_campaign_event(event_i, event_j)
            if cmp > 0:
                campaign_json["Events"][i], campaign_json["Events"][j] = campaign_json["Events"][j], campaign_json["Events"][i]

    return campaign_json

def sort_campaign_file(existing_filename: str, new_filename: str = None):
    """
    Sorts the campaign events in a given JSON file and writes the sorted events back to a file.
    """
    with open(existing_filename, 'r') as f:
        campaign_json = json.load(f)

    campaign_json = sort_campaign(campaign_json)

    # removing the defaults makes the file smaller, easier to read, and easier to compare
    # with other campaign files.
    remove_defaults(campaign_json)

    with open(new_filename, 'w') as f:
        campaign_json = json.dumps(campaign_json, indent=4, sort_keys=True)
        campaign_json = json.loads(campaign_json, parse_float=lambda x: round(float(x), 9))
        json.dump(campaign_json, f, indent=4, sort_keys=True)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('existing_filename', type=str, nargs=1, help='Name of campaign file to sort.')
    parser.add_argument('new_filename',      type=str, default=None, nargs='?',
                        help='Name of new campaign file to write sorted events to. ' +
                             'If not provided, will overwrite the existing file.')

    args = parser.parse_args()

    existing_filename = args.existing_filename[0]
    new_filename = args.new_filename if args.new_filename else args.existing_filename[0]

    sort_campaign_file(existing_filename=existing_filename, new_filename=new_filename)
    print(f"Sorted campaign events from {existing_filename} and saved to {new_filename}.")
