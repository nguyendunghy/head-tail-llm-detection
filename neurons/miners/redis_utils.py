import copy
import hashlib
import json
import threading
import time

import bittensor as bt
import redis

import index_data
from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.utils import hash_code

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)


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


def load_index(file_path, db):
    with open(file_path, 'r') as file:
        count = 1
        for line in file:
            list_data = line.strip().split(',')
            conn = get_conn()
            conn.select(db)
            for data in list_data:
                conn.set(data, '')
            count += 1
            bt.logging.info("---> upload line count: " + str(count))


def check_db_size(start, end):
    conn = get_conn()
    for i in range(start, end):
        conn.select(i)
        size = conn.dbsize()
        print(str(i) + ":" + str(size))


if __name__ == "__main__":
    start_time = time.time_ns()
    # file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
    # file_path = "/root/c4_dataset/c4/extracted_file/head-1000-00001.json"
    file_path = "/home/ubuntu/c4-index-v1/00000/merge_00000.txt"
    load_index(file_path,0)

    # verify_data(file_path)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")
    check_db_size(0, 1)
