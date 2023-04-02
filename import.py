import contextlib
import tkinter.filedialog as fd
from Tables import *
import pandas as pd


def import_schedule(dialog=True):
    with open(r"C:\Users\dstra\Downloads\Planning Groka.csv", 'r', encoding='utf8') as f:
        schedule = pd.read_csv(f, sep=';')
    schedule = schedule.set_index('Column1')
    return schedule


def schedule_to_json(schedule):
    schedule_json = '{}'
    schedule_json = json.loads(schedule_json)
    timeblocks = [i[0] for i in schedule.iterrows()]
    print(timeblocks)
    for i in schedule:
        if i not in ['Unnamed: 0', 'start_time', 'end_time']:
            schedule_dict = schedule[i].to_dict()
            schedule_json[i] = {}
            for j in timeblocks:
                entry = schedule_dict[j]
                if '$' in str(entry):
                    entry = entry.split('$')
                    activity = entry[0]
                    job = entry[1]
                    schedule_json[i][j] = {'timeblock': j, 'job': job, 'activity': activity}
    return schedule_json


def handle_job(job_name, activity_id):
    job = Table('Job')
    job_id = job.query(f'SELECT id FROM Job WHERE name = "{job_name}" AND ActivityId = {activity_id} LIMIT 1')
    if len(job_id) < 1:
        print(f'Job {job_name} not found in database')
        job.execute(f'INSERT INTO Job (name, ActivityId) VALUES ("{job_name}", {activity_id})')
        job.commit()
        print(f'Job {job_name} added to database')
        job_id = job.query(f'SELECT id FROM Job WHERE name = "{job_name}" AND ActivityId = {activity_id} LIMIT 1')
    else:
        job_id = job_id[0][0]
    return job_id


def handle_time(schedule_json, i, j):
    start = schedule_json[i][j]['start_time']
    end = schedule_json[i][j]['end_time']
    start_timeblock = Tijdblok().query(f'SELECT id FROM TimeBlock WHERE NameTimeStart = "{start}" LIMIT 1')[0][0]
    end_timeblock = Tijdblok().query(f'SELECT id FROM TimeBlock WHERE NameTimeEnd = "{end}" LIMIT 1')[0][0]
    return start_timeblock, end_timeblock


def get_values(schedule_json, i, j):
    activity = Table('Activity')
    activity_name = schedule_json[i][j]['activity']
    activity_id = activity.query(f'SELECT id FROM Activity WHERE name = "{activity_name}" LIMIT 1')[0][0]
    timeblock = 1
    leader_id = Leader_Table().get_id(i)
    job_name = schedule_json[i][j]['job']
    job_id = handle_job(job_name, activity_id)
    return leader_id, job_id, timeblock


def enter_schedule(schedule_json):
    schedule = Table('Schedule')
    count = 0
    for i in schedule_json:
        current_task = None
        start_time = None
        end_time = None
        for j in schedule_json[i]:
            if current_task is None:
                current_task = schedule_json[i][j]['job']
            if start_time is None:
                start_time = schedule_json[i][j]['timeblock']
            previous_task = current_task
            current_task = schedule_json[i][j]['job']
            end_time = schedule_json[i][j]['timeblock']
            activity = schedule_json[i][j]['activity']
            if current_task != previous_task:
                activity_id = Table('Activity').query(f'SELECT id FROM Activity WHERE name = "{activity}" LIMIT 1')[0][0]
                job_id = handle_job(previous_task, activity_id)
                with contextlib.suppress(Exception):
                    job_id = job_id[0][0]
                leader_id = Leader_Table().get_id(i)
                query = f'INSERT INTO Schedule (LeaderId, JobId, StartTimeBlockId, EndTimeBlockId) VALUES ({leader_id}, {job_id}, {start_time}, {end_time})'
                schedule.execute(query)
                schedule.commit()
                start_time = None
        print(f'Leader {i} added to database')



schedule = import_schedule(False)
print('Schedule imported')
schedule_json = schedule_to_json(schedule)
print('Schedule converted to json')
enter_schedule(schedule_json)

default_server.close()

print('=' * 50)
print('Done')
