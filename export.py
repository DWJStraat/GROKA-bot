"""This file is used to export the schedule to a json file"""

from Tables import *
import pandas as pd
import json


def export_person(name):
    """
    This function exports the schedule of a person to a json file
    :param name: The name of the person
    :return: A json file with the schedule of the person
    """
    leader_id = Leader().get_id(name)
    query = f'SELECT * FROM Schedule WHERE LeaderId = {leader_id}'
    schedule = Table('Schedule').query(query)
    schedule_dict = schedule_dict_builder(schedule)
    return schedule_builder(schedule_dict)


def schedule_dict_builder(schedule):
    """
    This function builds a dictionary with the schedule of a person
    :param schedule: The schedule of a person
    :return: A dictionary with the schedule of a person
    """
    schedule_dict = {}
    for entry in schedule:
        job_id = entry[0]
        job_name = Table('Job').query(f'SELECT name FROM Job WHERE id = {entry[2]}')[0][0]
        activity_id = Table('Job').query(f'SELECT ActivityId FROM Job WHERE id = {entry[2]}')[0][0]
        activity_name = Table('Activity').query(f'SELECT name FROM Activity WHERE id = {activity_id}')[0][0]
        start_time_block = entry[3]
        end_time_block = entry[4]
        schedule_dict[job_id] = [job_name, start_time_block, end_time_block, activity_name]
    return schedule_dict


def schedule_builder(schedule_dict):
    """
    This function builds a json file with the schedule of a person
    :param schedule_dict: A dictionary with the schedule of a person
    :return: A json file with the schedule of a person
    """
    schedule_json = json_builder()
    for i in Tijdblok().get_day():
        start_time = i[2]
        end_time = i[3]
        schedule_json[i[1]] = {'start_time': start_time, 'end_time': end_time, 'job': None, 'leader': None,
                               'activity': None}
        for j in schedule_dict:
            if schedule_dict[j][1] <= i[0] <= schedule_dict[j][2]:
                schedule_json[i[1]]['job'] = schedule_dict[j][0]
                schedule_json[i[1]]['activity'] = schedule_dict[j][3]
    return schedule_json


def single_export(name, json_file):
    """
    This function exports the schedule of a person to a json file
    :param name: The name of the person
    :param json_file: The json file to export to, containing all timeblocks
    :return: A json file with the schedule of the person
    """
    i = name
    schedule = export_person(i)
    # availability = handle_availability(availability, schedule)
    for j in json_file:
        # if str(j).startswith('x'):
        #     json_file[j][i] = 'x'
        # else:
        job = schedule[j]['job']
        activity = schedule[j]['activity']
        json_file[j][i] = None if job is None else f'{activity}${job}'
    # for j in availability:
    #     json_file[j][i] = 'x'
    return json_file


def mass_export():
    """
    This function exports the schedule of all people to a json file
    :return: A json file with the schedule of all people
    """
    json_file = time_json_builder()
    name_list = Leader().get_name()
    name_list.sort()
    for i in name_list:
        print(i)
        single_export(i, json_file)
    return json_file


def mass_export_csv(file_path='test.csv'):
    """
    This function exports the schedule of all people to a csv file
    :param file_path: The path to the csv file. Default is 'test.csv'
    """
    json_file = mass_export()
    df = pd.DataFrame.from_dict(json_file, orient='index')
    df.to_csv(file_path)


def time_json_builder():
    """
    This function builds a json file with all timeblocks
    :return: A json file with all timeblocks
    """
    json_file = json_builder()
    for i in Tijdblok().get_day():
        start_time = i[2]
        end_time = i[3]
        json_file[i[1]] = {'start_time': start_time, 'end_time': end_time}
    return json_file


def json_builder():
    """
    This function builds an empty json file
    :return: An empty json file
    """
    return json.loads('{}')


mass_export_csv()
print('=' * 50)
print('done')
default_server.close()
