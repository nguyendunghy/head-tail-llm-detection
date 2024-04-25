import copy
import hashlib
import json
import random
import sys
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
import bittensor as bt
from pathlib import Path

from neurons.miners import index_data
from neurons.miners.utils import hash_code, db_to_str

NUM_DB = 10_000
MAX_RECORD_C4_FILE = 360_000
ALL_TOKEN = [[] for i in range(NUM_DB)]
DIR_PATH = ''
FILE_PATH = ''
PROCESS_NUMBER = 20
HASH_LENGTH = 8


def save(db, token):
    if 0 > db >= NUM_DB:
        bt.logging.error("invalid db value {}".format(str(db)))
        return False
    else:
        token_list = ALL_TOKEN[db]
        token_list.append(token)
        if len(token_list) >= 10000:
            save_by_thread(db, token_list)
            token_list.clear()
        return True


def flush(all_token, arg):
    file_name = 'flush_' + str(arg) + '_' + str(time.time_ns()) + '_' + str(random.randint(1000, 9999)) + '.txt'
    file_path = DIR_PATH + file_name
    with open(file_path, 'w') as file:
        for i in range(len(all_token)):
            if len(all_token[i]) > 0:
                data = ','.join(all_token[i])
                print(data, file=file)
            else:
                print('', file=file)
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


def load_record(list_data, thread_name, line_count=None):
    for data in list_data:
        token_list = index_data.index_data(data)
        for token in token_list:
            try:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % NUM_DB
                save(db, sha256_hex[:HASH_LENGTH])
                bt.logging.info(
                    "upload success thread_name: " + thread_name + " key: " + sha256_hex[:HASH_LENGTH] + " : " + str(
                        db))
            except Exception as e:
                bt.logging.error(e)
                traceback.print_exc()
        bt.logging.info(
            "===> upload line {} to mysql success: thread_name: {} token list: {}".format(str(line_count), thread_name,
                                                                                          str(len(token_list))))


def load_range_one_thread(file_path, start_line, end_line):
    process_name = 'process-' + str(start_line // (MAX_RECORD_C4_FILE // PROCESS_NUMBER))
    with open(file_path, 'r') as file:
        count = 0
        for line in file:
            if start_line <= count < end_line:
                data = json.loads(line.strip())
                load_record([data], process_name, count + 1)
            count += 1


def load_range_process(arg):
    num_record_per_process = MAX_RECORD_C4_FILE // PROCESS_NUMBER
    load_range_one_thread(FILE_PATH, arg * num_record_per_process,
                          arg * num_record_per_process + num_record_per_process)
    flush(ALL_TOKEN, arg)


def load_range_multi_process():
    bt.logging.info('Starting task...')
    with ProcessPoolExecutor(PROCESS_NUMBER) as exe:
        exe.map(load_range_process, range(0, PROCESS_NUMBER))
    bt.logging.info('Done.')


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]
    start_time = time.time_ns()

    if arg1 == 'index_file':
        FILE_PATH = '/home/ubuntu/c4-dataset/c4/en/c4-train.00000-of-01024.json'
        DIR_PATH = '/home/ubuntu/c4-dataset/indexed_data/'
        PROCESS_NUMBER = 4
        ...
    elif arg1 == 'index_multy_process':
        file_path_template = "/mnt/vol_b/c4-dataset/extracted/c4-train.{}-of-01024.json"
        dir_path_template = "/mnt/vol_b/c4-dataset/indexed_data/{}/"
        for i in range(int(arg2), int(arg3)):
            FILE_PATH = file_path_template.format(str(db_to_str(i)))
            DIR_PATH = dir_path_template.format(db_to_str(i))
            directory_path = Path(DIR_PATH)
            if not directory_path.exists():
                directory_path.mkdir(parents=True, exist_ok=True)
                bt.logging.info(f"Directory created: {directory_path}")

            load_range_multi_process()

    bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
