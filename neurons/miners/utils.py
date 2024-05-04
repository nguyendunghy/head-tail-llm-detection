import json
import time


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def write(data, dir_path):
    data_dict = {'data': data}
    file_path = dir_path + '/' + str(time.time_ns()) + '.json'
    with open(file_path, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)
