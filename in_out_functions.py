from Tables import Table, Leader_Table, Tijdblok
import pandas as pd
import json
import tkinter.filedialog as fd
import time


class Schedule_Class:
    def __init__(self, mode='', file_path='test.csv', sep=';'):
        if mode == "I":
            self.i = True
        elif mode == "O":
            self.i = False
        else:
            print("Mode not recognized, please use I for import or O for export")
            return
        self.sep = sep
        self.file_path = file_path
        self.get_schedule()

    def get_schedule(self, ):
        self.schedule = self.import_schedule() if self.i else self.load_schedule()

    def import_schedule(self, ):
        if self.file_path == '':
            file_path = fd.askopenfilename()

        with open(self.file_path, 'r', encoding='utf8') as f:
            schedule = pd.read_csv(f, sep=self.sep)
            schedule = schedule.set_index('Column1')
        return schedule

    def load_schedule(self):
        pass

    def to_json(self):
        if type(self.schedule) != pd.DataFrame:
            return
        schedule_json = '{}'
        schedule_json = json.loads(schedule_json)
        timeblocks = [i[0] for i in self.schedule.iterrows()]
        for i in self.schedule:
            if i not in ['Unnamed: 0', 'start_time', 'end_time']:
                schedule_dict = self.schedule[i].to_dict()
                schedule_json[i] = {}
                for j in timeblocks:
                    entry = schedule_dict[j]
                    if '$' in str(entry):
                        entry = entry.split('$')
                        activity = entry[0]
                        job = entry[1]
                        required = entry[2] if len(entry) == 3 else 0
                        schedule_json[i][j] = {'timeblock': j, 'job': job, 'activity': activity,
                                               'required': required}
        self.json = schedule_json


def load_schedule():
    """
    This function loads the schedule from the database
    :return: A json file with the schedule of all people
    """
    schedule = Table('Schedule').query('SELECT Schedule.id, LeaderId, L.name, Schedule.StartTimeBlockId, '
                                       'Schedule.EndTimeBlockId, required, Job.id, Job.name, ActivityId,'
                                       ' A.name FROM Schedule LEFT JOIN Job ON Schedule.JobID = Job.id '
                                       'LEFT JOIN Activity A on Job.ActivityId = A.id '
                                       'LEFT JOIN Leader L on Schedule.LeaderId = L.id')
    schedule_json = json.loads('{}')
    for entry in schedule:
        schedule_json[entry[0]] = {
            'leader_id': entry[1],
            'leader': entry[2],
            'start_time_block': entry[3],
            'end_time_block': entry[4],
            'required': entry[5],
            'job_id': entry[6],
            'job': entry[7],
            'activity_id': entry[8],
            'activity': entry[9],
            'timeblock': list(range(entry[3], entry[4] + 1))
        }
    return schedule_json


def bundle_by_leader(schedule):
    schedule_dict = json.loads('{}')
    for entry in schedule:
        leader = schedule[entry]['leader']
        if leader not in schedule_dict:
            schedule_dict[schedule[entry]['leader']] = {}
        for block in schedule[entry]['timeblock']:
            schedule_dict[leader][block] = f'{schedule[entry]["activity"]}$' \
                                           f'{schedule[entry]["job"]}${schedule[entry]["required"]}'
    return schedule_dict


def bundle_by_timeblock(schedule):
    schedule_dict = json.loads('{}')
    timeblocks = Table('TimeBlock').query('SELECT id, NameTimeStart, NameTimeEnd FROM TimeBlock')
    timeblock = json.loads('{}')
    for i in timeblocks:
        timeblock[i[0]] = {
            'start_time': i[1],
            'end_time': i[2]
        }
    for entry in schedule:
        entry = schedule[entry]
        for i in entry['timeblock']:
            if i not in schedule_dict:
                schedule_dict[i] = {
                    'start_time': timeblock[i]['start_time'],
                    'end_time': timeblock[i]['end_time']
                }

            schedule_dict[i][entry['leader']] = f'{entry["activity"]}${entry["job"]}${entry["required"]}'
    return schedule_dict


def panda_bundle(bundle):
    df = pd.DataFrame.from_dict(bundle, orient='index')
    df.index.name = 'Column1'
    df.sort_index(inplace=True)
    return df


def bundle_to_csv(bundle, file_name, sep=';'):
    panda_bundle(bundle).to_csv(f'{file_name}.csv', sep=sep)


def bundle_to_excel(bundle, file_name):
    panda_bundle(bundle).to_excel(f'{file_name}.xlsx')


def export(file_name, excel=False, csv=False):
    sched_dict = load_schedule()
    print('generated dict')
    bundle = bundle_by_timeblock(sched_dict)
    print('generated bundle')
    if excel:
        bundle_to_excel(bundle, file_name)
        print('generated excel')
    if csv:
        bundle_to_csv(bundle, file_name)
        print('generated csv')
    print('=' * 50)
    print('done')


def import_schedule(dialog=True, sep=';'):
    file = fd.askopenfilename() if dialog else r"test.csv"
    with open(file, 'r', encoding='utf8') as f:
        schedule = pd.read_csv(f, sep=sep)
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
                    required = entry[2] if len(entry) == 3 else 0
                    schedule_json[i][j] = {'timeblock': j, 'job': job, 'activity': activity, 'required': required}

    return schedule_json


def handle_job(job_name, activity_id):
    job = Table('Job')
    job_id = job.query(f'SELECT id FROM Job WHERE name = "{job_name}" AND ActivityId = "{activity_id}" LIMIT 1')
    if len(job_id) < 1:
        print(f'Job {job_name} not found in database')
        job.execute(f'INSERT INTO Job (name, ActivityId, description) VALUES ("{job_name}", {activity_id}, " ")',
                    commit=True)
        time.sleep(0.1)
        print(f'Job {job_name} added to database')
        job_id = job.query(f'SELECT id FROM Job WHERE name = "{job_name}" AND ActivityId = "{activity_id}" LIMIT 1')
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
    global required
    output = {}
    try:
        for user in schedule_json:
            output[user] = {}
            for job in schedule_json[user]:
                name = schedule_json[user][job]['job']
                activity = schedule_json[user][job]['activity']
                required = schedule_json[user][job]['required']
                key = f'{name}${activity}'
                if key not in output[user]:
                    output[user][key] = {
                        'activity': activity,
                        'timeblock': [],
                        'required': required
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
            required = schedule_bundle[user][job]['required']
            query = f'INSERT INTO Schedule (LeaderId, JobId, StartTimeBlockId, EndTimeBlockId, Required) ' \
                    f'VALUES ({leader_id}, {job_id}, {start_time}, {end_time}, {required})'
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


def stupid_import(debug=False, silent=False, dialog=True):
    schedule = import_schedule(dialog)
    print('Schedule imported')
    schedule_json = schedule_to_json(schedule)
    print('Schedule converted to json')
    bundle = job_bundle(schedule_json)
    error_log = enter_schedule_from_bundle(bundle, debug=debug, silent=silent)
    print('=' * 50)
    print('Done')
    return error_log


def panda_to_dict(schedule):
    schedule_dict = schedule.to_dict()
    schedule_json = {}
    for i in schedule_dict:
        if i not in ['Unnamed: 0', 'start_time', 'end_time']:
            schedule_json[i] = {}
            for j in schedule_dict[i]:
                entry = schedule_dict[i][j]
                if '$' in str(entry):
                    entry = entry.split('$')
                    activity = entry[0]
                    job = entry[1]
                    required = entry[2] if len(entry) == 3 else 0
                    schedule_json[i][j] = {'timeblock': j, 'job': job, 'activity': activity, 'required': required}
    return schedule_json

def smart_convert(schedule_json):
    output = {}
    for user in schedule_json:
        output[user] = {}
        for timeblock in schedule_json[user]:
            job = schedule_json[user][timeblock]['job']
            activity = schedule_json[user][timeblock]['activity']
            required = schedule_json[user][timeblock]['required']
            key = f'{activity}${job}${required}'
            output[user][timeblock] = key
    return output


def smart_import(debug=False, silent=False, dialog=True):
    new_schedule = import_schedule(dialog)
    old_schedule = load_schedule()
    old_schedule = bundle_by_leader(old_schedule)
    new_schedule = panda_to_dict(new_schedule)
    new_schedule = smart_convert(new_schedule)






if __name__ == '__main__':
    a, b = smart_import(dialog=False)
    # a = Schedule_Class('I')
    # b = Schedule_Class('O')
    # a.to_json()
