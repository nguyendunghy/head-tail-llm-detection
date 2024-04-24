import copy
import hashlib
import json
import random
import shutil
import sys
import threading
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import requests
import json
import bittensor as bt
import redis

import index_data
from detection.validator.data_augmentation import DataAugmentator
from neurons.miners.utils import hash_code, db_to_str, create_directory, gen_hash_and_db, count_lines

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)
PARENT_DIR_PATH = '/home/ubuntu/c4-dataset/c4-index-v1'
DESTINATION_FOLDER = '/home/ubuntu/c4-dataset/processed'
PROCESS_NUMBER = 4
NUM_FILE = 512
NUM_DB = 10_000


def get_conn():
    conn = redis.Redis(connection_pool=redis_pool)
    return conn


def exists(token) -> bool:
    hash_value, db = gen_hash_and_db(token=token)
    return exists_on_redis(hash_value=hash_value, db=db)


def exists_on_redis(hash_value, db):
    try:
        key = 'set-' + str(db)
        conn = get_conn()
        conn.select(db)
        return conn.sismember(key, hash_value) == 1
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


def verify_raw_exists(texts, url):
    bt.logging.info("start verify_raw_exists url: " + url)
    payload = json.dumps({
        "texts": texts
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        data = response.json()
        results = data['result']
        verify_result = []
        for result in results:
            verify_result.append(result)
        return verify_result
    else:
        print('Failed to post data:', response.status_code, response.content)
        return ['fail'] * len(texts)


def verify_list_lines(raw_texts, raw_line_numbers, augmentator, urls):
    texts = []
    line_numbers = []
    for i in range(len(raw_texts)):
        line = raw_texts[i]
        el = json.loads(line)
        augs = augmentator(el['text'])
        text = augs['text']
        if len(text) <= 250:
            bt.logging.info("human written text - too short character:" + text + ":" + str(raw_line_numbers[i]))
        else:
            texts.append(text)
            line_numbers.append(raw_line_numbers[i])

    for url in urls:
        processed_index = []
        result = verify_raw_exists(texts, url)
        for i in range(len(texts)):
            if result[i] == 'success':
                bt.logging.info("indexing success " + str(line_numbers[i]))
                processed_index.append(i)
            elif result[i] == 'short':
                bt.logging.info("text too short:" + str(line_numbers[i]) + ":" + texts[i])
                processed_index.append(i)
        left_texts = []
        left_numbers = []
        for j in range(len(texts)):
            if j not in processed_index:
                left_texts.append(texts[j])
                left_numbers.append(line_numbers[j])
        texts = left_texts
        line_numbers = left_numbers

    for i in range(len(texts)):
        bt.logging.info("indexing fail: " + str(line_numbers[i]) + " :" + texts[i])


def verify_line(line, augmentator, line_number, urls=None):
    el = json.loads(line)
    augs = augmentator(el['text'])
    text = augs['text']
    if len(text) <= 250:
        bt.logging.info("human written text - too short character")
        return True

    sentences = augmentator.get_all_sentences(text)
    count_word = 0
    for sentence in sentences:
        words = sentence.split(' ')
        count_word += len(words)
    if count_word // len(sentences) < 3:
        bt.logging.info("human written text - too short words ")
        return True
    if urls is not None:
        for url in urls:
            result = verify_raw_exists([text], url)
            if result[0] == 'success':
                bt.logging.info("indexing success " + str(line_number))
                return True
            elif result[0] == 'short':
                bt.logging.info("text too short:" + text)
                return True
        bt.logging.info("indexing fail: " + str(line_number) + " :" + text)
        return False

    list_token = index_data.cut_head_tail(text)
    if len(list_token) == 1:
        bt.logging.info("text too short:" + text)
        return True
    else:
        list_result = []
        try:
            for token in list_token:
                re = exists(token)
                list_result.append(re)
            if list_result.count(False) == 2:
                bt.logging.info("indexing fail: " + str(line_number) + " :" + text)
                return False
            else:
                bt.logging.info("indexing success " + str(line_number))
                return True
        except Exception as e:
            bt.logging.error(e)


def verify_line_no_words(line, augmentator, line_number):
    el = json.loads(line)
    augs = augmentator(el['text'])
    text = augs['text']
    if len(text) <= 250:
        bt.logging.info("human written text - too short character")
        return True

    sample_sentence = augmentator.subsample_sentences(text)
    list_token = index_data.cut_head_tail(sample_sentence)
    if len(list_token) == 1:
        bt.logging.info("text too short:" + sample_sentence)
        return True
    else:
        list_result = []
        try:
            for token in list_token:
                re = exists(token)
                list_result.append(re)
            if list_result.count(False) == 2:
                bt.logging.info("indexing fail: " + str(line_number) + " :" + text)
                return False
            else:
                bt.logging.info("indexing success " + str(line_number))
                return True
        except Exception as e:
            bt.logging.error(e)


def verify_data(file_path):
    augmentator = DataAugmentator()
    line_number = 1
    with open(file_path, 'r') as file:
        for line in file:
            verify_line_no_words(line, augmentator, line_number)
            line_number += 1


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


def verify_token(file_path, fixed_db=None):
    with open(file_path, 'r') as file:
        count = 1
        conn = get_conn()
        for line in file:
            if count in [1, 2500, 5_000, 7500, 10_000]:
                db = count - 1 if fixed_db is None else fixed_db
                conn.select(db)
                list_data = line.strip().split(',')
                key = 'set-' + str(db)
                for data in list_data[1:]:
                    if conn.sismember(key, data) == 0:
                        bt.logging.info(
                            "---> file {} has token {} at db {} not exit".format(str(file_path), data, str(db)))
                        return False
            count += 1
        return True


def verify_index_directory(parent_path, start, end, dest_path):
    for i in range(start, end):
        dir_path = parent_path + '/' + db_to_str(i)
        directory = Path(dir_path)
        file_names = [file.name for file in directory.iterdir() if file.is_file()]
        for f_name in file_names:
            file_path = dir_path + "/" + f_name
            if 'merge' in f_name:
                if not verify_token(file_path):
                    dest_file_path = dest_path + '/' + db_to_str(i)
                    # create_directory(dest_file_path)
                    # shutil.move(file_path, dest_file_path)
            else:
                arr = f_name.split('_')
                db = int(arr[0])
                verify_token(file_path, db)


def verify_all_c4(c4_dir, start, end, num_random_line=300, urls=None):
    """For each raw file, we will get randomly 300 rows to call to our service to verify. If the fail rate is high. we
    have to verify the accuracy of our indexed data"""
    augmentator = DataAugmentator()
    for i in range(start, end):
        file_path = c4_dir + '/' + 'c4-train.{}-of-01024.json'.format(db_to_str(i))
        bt.logging.info("file_path: " + file_path)
        num_line = count_lines(file_path)
        random_line_index = [random.randint(1, num_line + 1) for i in range(num_random_line)]
        with open(file_path, 'r') as file:
            line_number = 1
            texts = []
            for line in file:
                if line_number in random_line_index:
                    texts.append(line)
                line_number += 1
            verify_list_lines(texts, random_line_index, augmentator, urls)


def load_index_to_db(file_path, db, file_name):
    with open(file_path, 'r') as file:
        count = 1
        conn = get_conn()
        conn.select(db)
        for line in file:
            list_data = line.strip().split(',')
            key = 'set-' + str(db)
            conn.sadd(key, *list_data)
            count += 1
            bt.logging.info("---> upload line {} of file {} to db {}: ".format(str(count), file_name, str(db)))


def load_file_to_redis(file_path, file_name):
    with open(file_path, 'r') as file:
        db = 0
        conn = get_conn()
        for line in file:
            list_data = line.strip().split(',')
            conn.select(db)
            key = 'set-' + str(db)
            conn.sadd(key, *list_data)
            db += 1
            bt.logging.info("---> upload line {} of file {} to db {}".format(str(db), file_name, str(db - 1)))


def load_index_directory(parent_path, start, end, dest_path):
    for i in range(start, end):
        dir_path = parent_path + '/' + db_to_str(i)
        directory = Path(dir_path)
        file_names = [file.name for file in directory.iterdir() if file.is_file()]
        for f_name in file_names:
            file_path = dir_path + "/" + f_name
            if 'merged' in f_name:
                load_file_to_redis(file_path, file_path)
            else:
                arr = f_name.split('_')
                db = int(arr[0])
                load_index_to_db(file_path, db, file_path)
            dest_file_path = dest_path + '/' + db_to_str(i)
            create_directory(dest_file_path)
            shutil.move(file_path, dest_file_path)
        time.sleep(10)


def load_range_multi_process():
    bt.logging.info('Starting task...')
    with ProcessPoolExecutor(PROCESS_NUMBER) as exe:
        exe.map(load_range_process, range(0, PROCESS_NUMBER))
    bt.logging.info('Done.')


def load_range_process(arg):
    try:
        bt.logging.info("start load_range_process " + str(arg))
        bt.logging.info("NUM_FILE: " + str(NUM_FILE))
        bt.logging.info("PROCESS_NUMBER: " + str(PROCESS_NUMBER))

        num_folder = NUM_FILE // PROCESS_NUMBER
        load_index_directory(PARENT_DIR_PATH, arg * num_folder, arg * num_folder + num_folder, DESTINATION_FOLDER)
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


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
        parent_path = "/home/ubuntu/c4-dataset/indexed_data"
        des_path = '/home/ubuntu/c4-dataset/processed'
        load_index_directory(parent_path, int(arg2), int(arg3), des_path)
    elif arg1 == 'verify_raw':
        verify_data(str(arg2))
    elif arg1 == 'verify_index_directory':
        parent_path = "/home/ubuntu/c4-dataset/processed"
        des_path = '/home/ubuntu/c4-dataset/processed'
        verify_index_directory(parent_path, int(arg2), int(arg3), des_path)
    elif arg1 == 'multi_process':
        NUM_FILE = int(arg2)
        load_range_multi_process()
    elif arg1 == 'load_index_to_db':
        load_index_to_db('/home/ubuntu/c4-dataset/processed/00000/merge_00000.txt', 0, 'main-thread')
    elif arg1 == 'load_file':
        load_file_to_redis(file_path=str(arg2), file_name=str(arg3))
    elif arg1 == 'exists':
        start_time = time.time_ns()
        ex = exists_on_redis(str(arg2), int(arg3))
        bt.logging.info("exists: " + str(ex))
    elif arg1 == 'verify_c4':
        c4_dir = '/home/ubuntu/c4-dataset/c4/en'
        # urls = ['http://177.54.149.35:8888/verify-data', 'http://189.1.168.180:8888/verify-data',
        #         'http://189.1.168.181:8888/verify-data','http://177.54.152.68:8888/verify-data']
        urls = ['http://177.54.149.35:8888/verify-data', 'http://69.67.150.87:8888/verify-data']
        verify_all_c4(c4_dir=c4_dir, start=int(arg2), end=int(arg3), urls=urls)
    # verify_data(file_path)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
    # check_db_size(0, 1)
