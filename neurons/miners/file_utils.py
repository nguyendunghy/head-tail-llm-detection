import copy
import hashlib
import json
import random
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
import bittensor as bt
from pathlib import Path

from neurons.miners import index_data
from neurons.miners.utils import hash_code

NUM_DB = 10_000
ALL_TOKEN = [[] for i in range(NUM_DB)]
DIR_PATH = ''
FILE_PATH = ''
PROCESS_NUMBER = 40

def save(db, token):
    if 0 > db >= NUM_DB:
        bt.logging.error("invalid db value {}".format(str(db)))
        return False
    else:
        token_list = ALL_TOKEN[db]
        token_list.append(token)
        if len(token_list) >= 5000:
            save_by_thread(db, token_list)
            token_list.clear()
        return True


def flush(all_token):
    file_name = 'flush_' + str(time.time_ns()) + '_' + str(random.randint(100, 1000)) + '.txt'
    file_path = DIR_PATH + file_name
    with open(file_path, 'w') as file:
        for i in range(len(all_token)):
            if len(all_token[i]) > 0:
                data = str(i) + ',' + ','.join(all_token[i])
                print(data, file=file)
    all_token.clear()


def save_to_file(db, list_token):
    data = str(db) + ',' + ','.join(list_token)
    file_name = str(db) + '_' + str(time.time_ns()) + '_' + str(random.randint(100, 1000)) + '.txt'
    file_path = DIR_PATH + file_name
    with open(file_path, 'w') as file:
        file.write(data)


def save_by_thread(db, list_token):
    tmp_list_data = copy.deepcopy(list_token)
    my_thread = threading.Thread(target=save_to_file,
                                 args=(db, tmp_list_data))
    my_thread.start()


def read_from_file(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            print(line)
            a = line.split(',')
            print(a)


def db_to_str(db):
    length = len(str(db))
    if length == 1:
        return '0000' + str(db)
    elif length == 2:
        return '000' + str(db)
    elif length == 3:
        return '00' + str(db)
    elif length == 4:
        return '0' + str(db)
    else:
        return str(db)


def load_record(list_data, thread_name, line_count=None):
    for data in list_data:
        token_list = index_data.index_data(data)
        for token in token_list:
            try:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 10_000
                save(db, sha256_hex[:8])
                bt.logging.info(
                    "upload success thread_name: " + thread_name + " key: " + sha256_hex[:8] + " : " + str(db))
            except Exception as e:
                bt.logging.error(e)
                traceback.print_exc()
        bt.logging.info(
            "===> upload line {} to mysql success: thread_name: {} token list: {}".format(str(line_count), thread_name,
                                                                                          str(len(token_list))))


def load_range_one_thread(file_path, start_line, end_line):
    with open(file_path, 'r') as file:
        count = 0
        for line in file:
            if start_line <= count < end_line:
                data = json.loads(line)
                load_record([data], 'thread-main', count + 1)
            count += 1
    flush(ALL_TOKEN)


def load_range_process(arg):
    num_record_per_process = 360_000//PROCESS_NUMBER
    load_range_one_thread(FILE_PATH, arg * num_record_per_process, arg * num_record_per_process + num_record_per_process)


def load_range_multi_process():
    bt.logging.info('Starting task...')
    with ProcessPoolExecutor(PROCESS_NUMBER) as exe:
        exe.map(load_range_process, range(0, PROCESS_NUMBER))
    bt.logging.info('Done.')


if __name__ == '__main__':
    start_time = time.time_ns()
    file_path_template = "/home/ubuntu/c4-dataset/extracted/c4-train.0000{}-of-01024.json"
    dir_path_template = "/home/ubuntu/c4-dataset/indexed_data/{}/"
    for i in range(1):
        FILE_PATH = file_path_template.format(str(i))
        DIR_PATH = dir_path_template.format("0000" + str(i))
        directory_path = Path(DIR_PATH)
        if not directory_path.exists():
            directory_path.mkdir(parents=True, exist_ok=True)
            bt.logging.info(f"Directory created: {directory_path}")

        load_range_multi_process()

    bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
