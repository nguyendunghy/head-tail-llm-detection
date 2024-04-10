import copy
import hashlib
import json
import shutil
import sys
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import bittensor as bt
import redis

import index_data
from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.utils import hash_code, db_to_str, create_directory

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
PARENT_DIR_PATH = '/home/ubuntu/c4-dataset/c4-index-v1'
DESTINATION_FOLDER = '/home/ubuntu/c4-dataset/processed'
PROCESS_NUMBER = 32
NUM_FILE = 512


def hash_code_java(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    h = (h + 2 ** 31) % 2 ** 32 - 2 ** 31
    return -h if h < 0 else h


def get_conn():
    conn = redis.Redis(connection_pool=redis_pool)
    return conn


def exists(key) -> bool:
    # start_time = time.time_ns()
    conn = get_conn()
    # time_connect = time.time_ns()
    # bt.logging.info("time connect redis: " + str(time_connect - start_time))

    m = hashlib.sha256(key.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    # time_hash_sha256 = time.time_ns()
    db = hash_code_java(sha256_hex) % 1000
    # bt.logging.info("time hash sha256: " + str(time_hash_sha256 - time_connect))
    bt.logging.info("sha256_hex: " + sha256_hex + " db= " + str(db))
    conn.select(db)
    ex = conn.exists(sha256_hex) == 1
    # end_time = time.time_ns()
    # bt.logging.info("time check exist: " + str(end_time - time_hash_sha256))

    return ex


def verify_data(file_path):
    # human_dataset = HumanDataset()
    augmentator = DataAugmentator()
    with open(file_path, 'r') as file:
        for line in file:
            el = json.loads(line)
            augs = augmentator(el['text'])
            text = augs['text']
            list_token = index_data.cut_head_tail(text)
            if len(list_token) == 1:
                bt.logging.info("text too short" + text)
            else:
                list_result = []
                for token in list_token:
                    m = hashlib.sha256(token.encode('UTF-8'))
                    sha256_hex = m.hexdigest()
                    hash_value = hash_code(sha256_hex)
                    db = hash_value % 100_000_000
                    key = sha256_hex[:8]
                    conn = get_conn()
                    conn.select(db)
                    re = conn.exists(key) == 1
                    list_result.append(re)
                if list_result.count(False) == 2:
                    bt.logging.info("indexing<==>fail: " + text)
                else:
                    bt.logging.info("indexing success")


def load_record(conn, list_data, thread_name):
    for data in list_data:
        token_list = index_data.index_data(data)
        for token in token_list:
            try:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 100_000_000
                conn.select(db)
                conn.set(sha256_hex[:8], "")
                bt.logging.info(
                    "upload success thread_name: " + thread_name + " key: " + sha256_hex[:8] + " : " + str(db))
            except Exception as e:
                bt.logging.error(e)
        bt.logging.info("===> upload line to redis success: thread_name: " + thread_name + " : " + str(len(token_list)))


def load(file_path):
    with open(file_path, 'r') as file:
        count = 0
        thread_count = 0
        list_data = []
        for line in file:
            data = json.loads(line)
            list_data.append(data)
            if count % 100 == 0:
                try:
                    thread_name = "thread-" + str(thread_count)
                    tmp_list_data = copy.deepcopy(list_data)
                    my_thread = threading.Thread(target=load_record, args=(get_conn(), tmp_list_data, thread_name))
                    my_thread.start()
                    thread_count += 1
                except Exception as e:
                    bt.logging.error(e)
                list_data = []

            count += 1
            bt.logging.info("---> upload line count: " + str(count))

        if len(list_data) > 0:
            try:
                load_record(get_conn(), list_data, "thread-main")
            except Exception as e:
                bt.logging.error(e)


def load_index_to_db(file_path, db, file_name):
    with open(file_path, 'r') as file:
        count = 1
        conn = get_conn()
        conn.select(db)
        for line in file:
            list_data = line.strip().split(',')
            for data in list_data:
                conn.set(data, '')
            count += 1
            bt.logging.info("---> upload line {} of file {} to db {}: ".format(str(count), file_name, str(db)))


def load_file_to_redis(file_path, file_name):
    with open(file_path, 'r') as file:
        db = 0
        conn = get_conn()
        for line in file:
            list_data = line.strip().split(',')
            conn.select(db)
            for data in list_data:
                conn.set(data, '')
            db += 1
            bt.logging.info("---> upload line {} of file {} to db {}".format(str(db + 1), file_name, str(db)))


def load_index_directory(parent_path, start, end, dest_path):
    for i in range(start, end):
        dir_path = parent_path + '/' + db_to_str(i)
        directory = Path(dir_path)
        file_names = [file.name for file in directory.iterdir() if file.is_file()]
        for f_name in file_names:
            file_path = dir_path + "/" + f_name
            if 'flush' in f_name:
                load_file_to_redis(file_path, f_name)
            else:
                arr = f_name.split('_')
                db = int(arr[0])
                load_index_to_db(file_path, db, f_name)
            dest_file_path = dest_path + '/' + db_to_str(i)
            create_directory(dest_file_path)
            shutil.move(file_path, dest_file_path)


def load_range_multi_process():
    bt.logging.info('Starting task...')
    with ProcessPoolExecutor(PROCESS_NUMBER) as exe:
        exe.map(load_range_process, range(0, PROCESS_NUMBER))
    bt.logging.info('Done.')


def load_range_process(arg):
    bt.logging.info("start load_range_process " + str(arg))
    bt.logging.info("NUM_FILE: " + str(NUM_FILE))
    bt.logging.info("PROCESS_NUMBER: " + str(PROCESS_NUMBER))

    num_folder = NUM_FILE // PROCESS_NUMBER
    load_index_directory(PARENT_DIR_PATH, arg * num_folder, arg * num_folder + num_folder, DESTINATION_FOLDER)


def check_db_size(start, end):
    conn = get_conn()
    for i in range(start, end):
        conn.select(i)
        size = conn.dbsize()
        print(str(i) + ":" + str(size))


if __name__ == "__main__":
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]

    start_time = time.time_ns()
    if arg1 == 'check_db_size':
        check_db_size(int(arg2), int(arg3))
    elif arg1 == 'load_dir':
        # file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
        # file_path = "/root/c4_dataset/c4/extracted_file/head-1000-00001.json"
        parent_path = "/home/ubuntu/c4-dataset/c4-index-v1"
        des_path = '/home/ubuntu/c4-dataset/processed'
        load_index_directory(parent_path, int(arg2), int(arg3), des_path)
    elif arg1 == 'verify':
        verify_data(str(arg2))
    elif arg1 == 'multi_process':
        NUM_FILE = int(arg2)
        load_range_multi_process()

    # verify_data(file_path)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")
    # check_db_size(0, 1)
