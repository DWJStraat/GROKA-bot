from Tables import *
import pandas as pd
import json


def export(name, day):
    leader_id = Leader().get_id(name)
    day = Tijdblok().get_day(day)
    timeblocks = [i[0] for i in day]
    print(timeblocks)
    start_time = timeblocks[0]
    end_time = timeblocks[-1]
    query = f'SELECT * FROM Schedule WHERE LeaderId = {leader_id} ' \
            f'AND StartTimeBlockId BETWEEN {start_time} AND {end_time}'
    a = Table('Schedule').query(query)
    print(a)


def export_person(name):
    job_id = Leader().get_id(name)
    query = f'SELECT * FROM Schedule WHERE LeaderId = {job_id}'
    schedule = Table('Schedule').query(query)
    schedule_dict = {}
    for entry in schedule:
        job_id = entry[0]
        job_name = Table('Job').query(f'SELECT name FROM Job WHERE id = {entry[2]}')[0][0]
        activity_id = Table('Job').query(f'SELECT ActivityId FROM Job WHERE id = {entry[2]}')[0][0]
        activity_name = Table('Activity').query(f'SELECT name FROM Activity WHERE id = {activity_id}')[0][0]
        start_time_block = entry[3]
        end_time_block = entry[4]
        schedule_dict[job_id] = [job_name, start_time_block, end_time_block, activity_name]
    schedule_json = '{}'
    schedule_json = json.loads(schedule_json)
    for i in Tijdblok().get_day():
        start_time = i[2]
        end_time = i[3]
        schedule_json[i[1]] = {'start_time': start_time, 'end_time': end_time, 'job': None, 'leader': None, 'activity': None}
        for j in schedule_dict:
            if schedule_dict[j][1] <= i[0] <= schedule_dict[j][2]:
                schedule_json[i[1]]['job'] = schedule_dict[j][0]
                schedule_json[i[1]]['activity'] = schedule_dict[j][3]

    return schedule_json


def mass_export():
    json_file = '{}'
    json_file = json.loads(json_file)
    for i in Tijdblok().get_day():
        start_time = i[2]
        end_time = i[3]
        json_file[i[1]] = {'start_time': start_time, 'end_time': end_time}
    name_list = Leader().get_name()
    name_list.sort()
    for i in name_list:
        print(i)
        a = export_person(i)
        for j in json_file:
            job = a[j]['job']
            activity = a[j]['activity']
            json_file[j][i] = f'{activity}${job}' if job is not None else None
    return json_file


def mass_export_csv():
    json_file = mass_export()
    df = pd.DataFrame.from_dict(json_file, orient='index')
    df.to_csv('test.csv')


mass_export_csv()
print('done')
