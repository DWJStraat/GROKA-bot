import tkinter.filedialog as fd
from Tables import *
import pandas as pd

def import_schedule(dialog=True):
    with open(r'E:\Scouting GROKA\GROKA-bot\test.csv', 'r', encoding='utf8') as f:
        schedule = pd.read_csv(f)
    return schedule

def schedule_to_json(schedule):
    schedule_json = '{}'
    schedule_json = json.loads(schedule_json)
    start_time = schedule['start_time'].to_list()
    end_time = schedule['end_time'].to_list()
    id = schedule['Unnamed: 0'].to_list()
    for i in schedule:
        if i not in ['Unnamed: 0','start_time', 'end_time']:
            schedule_dict = schedule[i].to_dict()
            schedule_json[i]= {}
            for j in range(len(start_time)):
                start = start_time[j]
                end = end_time[j]
                entry = schedule_dict[j]
                if '$' in str(entry):
                    entry = entry.split('$')
                    activity = entry[0]
                    leader = entry[2]
                    job = entry[1]
                    schedule_json[i][j] = {'start_time': start, 'end_time': end, 'job': job, 'leader': leader, 'activity': activity}
    return schedule_json

def enter_schedule(schedule_json):
    schedule = Table('Schedule')
    job = Table('Job')
    activity = Table('Activity')
    for i in schedule_json:
        for j in schedule_json[i]:
            start = schedule_json[i][j]['start_time']
            end = schedule_json[i][j]['end_time']
            job_name = schedule_json[i][j]['job']
            leader = schedule_json[i][j]['leader']
            activity_name = schedule_json[i][j]['activity']
            print(f"INSERT INTO Schedule VALUES ('{start}', '{end}', '{job_name}', '{leader}', '{activity_name}')")

schedule = import_schedule(False)
json = schedule_to_json(schedule)
enter_schedule(json)