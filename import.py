import contextlib
import tkinter.filedialog as fd
from Tables import *
import pandas as pd
import time


def import_schedule(dialog=True):
    if dialog:
        file = fd.askopenfilename()
    else:
        file = r"C:\Users\dstra\Downloads\Planning Groka_voor csv.csv"
    with open(file, 'r', encoding='utf8') as f:
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
        job.execute(f'INSERT INTO Job (name, ActivityId) VALUES ("{job_name}", {activity_id})', commit=True)
        time.sleep(0.1)
        print(f'Job {job_name} added to database')
        job_id = job.query(f'SELECT id FROM Job WHERE name = "{job_name}" AND ActivityId = {activity_id} LIMIT 1')
    while type(job_id) is not int:
        job_id = job_id[0]
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


def job_bundle(schedule_json):
    output = {}
    try:
        for user in schedule_json:
            output[user] = {}
            for job in schedule_json[user]:
                name = schedule_json[user][job]['job']
                activity = schedule_json[user][job]['activity']
                key = f'{name}${activity}'
                if key not in output[user]:
                    output[user][key] = {
                        'activity': activity,
                        'timeblock': [],
                    }
                output[user][key]['timeblock'].append(schedule_json[user][job]['timeblock'])
            for job in output[user]:
                output[user][job]['timeblock'] = sorted(output[user][job]['timeblock'])
                output[user][job]['start_time'] = output[user][job]['timeblock'][0]
                output[user][job]['end_time'] = output[user][job]['timeblock'][-1]
        return output
    except Exception as e:
        print(e)
        return output


def enter_schedule_from_bundle(schedule_bundle, debug=False, silent=False):
    error_log = []
    for user in schedule_bundle:

        leader_id = Leader_Table().get_id(user)
        for job in schedule_bundle[user]:
            activity = schedule_bundle[user][job]['activity']
            try:
                activity_id = Table('Activity').query(f'SELECT id FROM Activity WHERE name = "{activity}" LIMIT 1')[0][
                    0]
            except IndexError:
                print(f'Activity {activity} not found in database')
                error_log.append(f'Activity {activity} not found in database')
                continue
            job_name = job.split('$')[0]
            job_id = handle_job(job_name, activity_id)
            start_time = schedule_bundle[user][job]['start_time']
            end_time = schedule_bundle[user][job]['end_time']
            query = f'INSERT INTO Schedule (LeaderId, JobId, StartTimeBlockId, EndTimeBlockId) ' \
                    f'VALUES ({leader_id}, {job_id}, {start_time}, {end_time})'
            if debug and not silent:
                print(query)
            else:
                try:
                    Table('Schedule').execute(query, commit=True)
                    time.sleep(0.1)
                except Exception as e:
                    print(e)
                    error_log.append(query)
                    print(f'Error in query: {query}')
        print(f'User {user} done')
    return error_log


schedule = import_schedule(True)
print('Schedule imported')
schedule_json = schedule_to_json(schedule)
print('Schedule converted to json')
bundle = job_bundle(schedule_json)
error_log = enter_schedule_from_bundle(bundle, debug=False, silent=False)

print('=' * 50)
print('Done')
