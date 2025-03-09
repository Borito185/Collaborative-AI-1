import os, requests
import sys
import csv
import glob
import pathlib

def output_logger(fld):
    recent_dir = max(glob.glob(os.path.join(fld, '*/')), key=os.path.getmtime)
    recent_dir = max(glob.glob(os.path.join(recent_dir, '*/')), key=os.path.getmtime)
    action_file = glob.glob(os.path.join(recent_dir,'world_1/action*'))[0]
    action_header = []
    action_contents=[]
    trustfile_header = []
    trustfile_contents = []
    # Calculate the unique human and agent actions
    unique_agent_actions = []
    unique_human_actions = []
    with open(action_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in reader:
            if action_header==[]:
                action_header=row
                continue
            if row[2:4] not in unique_agent_actions and row[2]!="":
                unique_agent_actions.append(row[2:4])
            if row[4:6] not in unique_human_actions and row[4]!="":
                unique_human_actions.append(row[4:6])
            if row[4] == 'RemoveObjectTogether' or row[4] == 'CarryObjectTogether' or row[4] == 'DropObjectTogether':
                if row[4:6] not in unique_agent_actions:
                    unique_agent_actions.append(row[4:6])
            res = {action_header[i]: row[i] for i in range(len(action_header))}
            action_contents.append(res)

    with open(fld+'/beliefs/currentTrustBelief.csv') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar="'")
        for row in reader:
            if trustfile_header==[]:
                trustfile_header=row
                continue
            if row:
                res = {trustfile_header[i] : row[i] for i in range(len(trustfile_header))}
                trustfile_contents.append(res)
    # Retrieve the stored trust belief values
    name = trustfile_contents[-1]['name']
    # UPDATED TRUSTFILE CONTENTS
    competence_search = trustfile_contents[-1]['competence_search']
    competence_rescue = trustfile_contents[-1]['competence_rescue']
    competence_remove = trustfile_contents[-1]['competence_remove']
    willingness_search = trustfile_contents[-1]['willingness_search']
    willingness_rescue = trustfile_contents[-1]['willingness_rescue']
    willingness_remove = trustfile_contents[-1]['willingness_remove']
    # Retrieve the number of ticks to finish the task, score, and completeness
    no_ticks = action_contents[-1]['tick_nr']
    score = action_contents[-1]['score']
    completeness = action_contents[-1]['completeness']
    # Save the output as a csv file
    print("Saving output...")
    with open(os.path.join(recent_dir,'world_1/output.csv'),mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['completeness','score','no_ticks','agent_actions','human_actions'])
        csv_writer.writerow([completeness,score,no_ticks,len(unique_agent_actions),len(unique_human_actions)])

    all_trust_path = os.path.join(fld, 'beliefs', 'allTrustBeliefs.csv')
    updated_alltrust_contents = []
    entry_exists = False

    with open(all_trust_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in reader:
            if row and row[0] == name:
                updated_alltrust_contents.append([name, competence_search, competence_rescue, competence_remove,
                                                  willingness_search, willingness_rescue, willingness_remove])
                entry_exists = True
            else:
                updated_alltrust_contents.append(row)

    if not entry_exists:
        updated_alltrust_contents.append([name, competence_search, competence_rescue, competence_remove,
                                          willingness_search, willingness_rescue, willingness_remove])

    with open(all_trust_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(updated_alltrust_contents)

    # Remove the row with the ID from currentTrustBelief.csv
    current_trust_path = os.path.join(fld, 'beliefs', 'currentTrustBelief.csv')
    updated_trustfile_contents = []

    with open(current_trust_path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        trustfile_header = next(reader)  # Read header
        updated_trustfile_contents.append(trustfile_header)
        for row in reader:
            if row and row[0] != name:
                updated_trustfile_contents.append(row)

    with open(current_trust_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(updated_trustfile_contents)