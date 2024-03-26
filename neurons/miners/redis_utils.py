import copy
import json
import threading
import time
import redis
import hashlib
import bittensor as bt
import json
import math
import index_data

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)


def hash_code_java(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    h = (h + 2 ** 31) % 2 ** 32 - 2 ** 31
    return -h if h < 0 else h


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


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


def load_record(conn, list_data):
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
                bt.logging.info("upload success key: " + sha256_hex[:8] + " : " + str(db))
            except Exception as e:
                bt.logging.error(e)
        bt.logging.info("===> upload line to redis success: token_list: " + str(len(token_list)))


def load(file_path):
    with open(file_path, 'r') as file:
        count = 0
        list_data = []
        for line in file:
            data = json.loads(line)
            list_data.append(data)
            if count % 1000 == 0:
                try:
                    tmp_list_data = copy.deepcopy(list_data)
                    threading.Thread(target=load_record, args=(get_conn(), tmp_list_data))
                except Exception as e:
                    bt.logging.error(e)
                list_data = []

            count += 1
            bt.logging.info("---> upload line count: " + str(count))

        if len(list_data) > 0:
            try:
                load_record(get_conn(), list_data)
            except Exception as e:
                bt.logging.error(e)


if __name__ == "__main__":
    start_time = time.time_ns()
    file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
    load(file_path)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")

    # thread1 = threading.Thread(target=test_thread('thread_1'), daemon=False)
    # thread2 = threading.Thread(target=test_thread('thread_2'), daemon=False)
    #
    # thread1.start()
    # thread2.start()
    #
    # bt.logging.info("end main thread")
