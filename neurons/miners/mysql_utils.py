import copy
import hashlib
import json
import sys
import threading
import time

import bittensor as bt
import mysql.connector
import mysql.connector.pooling

from detection.validator.data_augmentation import DataAugmentator
from neurons.miners import index_data

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="jackie_pool",
    pool_size=32,
    pool_reset_session=True,
    host='localhost',
    port='3306',
    database='ai_generated_text',
    user='jackie',
    password='jackie_password'
)


def get_db_connection():
    return connection_pool.get_connection()


def exist(db_connection, db, hash_value):
    cursor = db_connection.cursor()
    sql = "select count(*) from table_{} where hash = (%s)".format(str(db))

    cursor.execute(sql, tuple(hash_value))
    count_result = cursor.fetchone()[0]
    print(count_result)
    cursor.close()
    return int(count_result) > 0


def insert(db_connection, db, hash_value):
    cursor = db_connection.cursor()

    sql = "INSERT INTO table_{} (hash) VALUES (%s)".format(str(db))
    val = tuple(hash_value)

    # Execute the query
    cursor.execute(sql, val)

    # Commit to the database
    db_connection.commit()

    # Close the cursor and connection
    cursor.close()
    # db_connection.close()
    # print(cursor.rowcount, "record inserted.")


def create_table(db_connection, db):
    try:
        bt.logging.info("start create table_{}".format(str(db)))
        cursor = db_connection.cursor()
        sql = "create table table_{}(hash varchar(100),INDEX index_table_{} (hash))".format(str(db), str(db))
        cursor.execute(sql)
        db_connection.commit()
        cursor.close()
        bt.logging.info("create table_{} success".format(str(db)))
    except Exception as e:
        bt.logging.error(e)
    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            db_connection.close()


def truncate_table(db_connection, db):
    try:
        bt.logging.info("start truncate table_{}".format(str(db)))
        cursor = db_connection.cursor()
        sql = "truncate table table_{}".format(str(db))
        cursor.execute(sql)
        db_connection.commit()
        cursor.close()
        bt.logging.info("truncate table_{} success".format(str(db)))
    except Exception as e:
        bt.logging.error(e)
    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            db_connection.close()


def drop_table(db_connection, db):
    try:
        bt.logging.info("start drop table_{}".format(str(db)))
        cursor = db_connection.cursor()
        sql = "drop table table_{}".format(str(db))
        cursor.execute(sql)
        db_connection.commit()
        cursor.close()
        bt.logging.info("drop table_{} success".format(str(db)))
    except Exception as e:
        bt.logging.error(e)
    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            db_connection.close()


def create_all_table(num_db):
    for i in range(num_db):
        create_table(get_db_connection(), i)


def truncate_all_table(num_db):
    for i in range(num_db):
        truncate_table(get_db_connection(), i)


def drop_all_table(num_db):
    for i in range(num_db):
        drop_table(get_db_connection(), i)


def load(file_path):
    with open(file_path, 'r') as file:
        count = 0
        thread_count = 0
        list_data = []
        for line in file:
            data = json.loads(line)
            list_data.append(data)
            if count % 100 == 99:
                try:
                    thread_name = "thread-" + str(thread_count)
                    tmp_list_data = copy.deepcopy(list_data)
                    my_thread = threading.Thread(target=load_record,
                                                 args=(tmp_list_data, thread_name))
                    my_thread.start()
                    thread_count += 1
                except Exception as e:
                    bt.logging.error(e)
                list_data = []

            count += 1
            bt.logging.info("---> upload line count: " + str(count))

        if len(list_data) > 0:
            try:
                load_record(list_data, "thread-main")
            except Exception as e:
                bt.logging.error(e)


def load_range_thread(file_path, start_line, end_line):
    with open(file_path, 'r') as file:
        count = 0
        thread_count = 0
        list_data = []
        for line in file:
            if start_line <= count < end_line:
                data = json.loads(line)
                list_data.append(data)
                if count % 500 == 499:
                    try:
                        thread_name = "thread-" + str(thread_count)
                        tmp_list_data = copy.deepcopy(list_data)
                        my_thread = threading.Thread(target=load_record,
                                                     args=(tmp_list_data, thread_name))
                        my_thread.start()
                        thread_count += 1
                    except Exception as e:
                        bt.logging.error(e)
                    list_data = []

                bt.logging.info("---> upload line count: " + str(count))
            count += 1

    if len(list_data) > 0:
        try:
            load_record(list_data, "thread-main")
        except Exception as e:
            bt.logging.error(e)


def load_range_one_thread(file_path, start_line, end_line):
    with open(file_path, 'r') as file:
        count = 0
        for line in file:
            if start_line <= count < end_line:
                data = json.loads(line)
                load_record([data], 'thread-main', count+1)
            count += 1


def load_record(list_data, thread_name, line_count=None):
    my_conn = get_db_connection()
    for data in list_data:
        token_list = index_data.index_data(data)
        for token in token_list:
            try:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 10_000
                insert(my_conn, db, [sha256_hex[:8]])
                bt.logging.info(
                    "upload success thread_name: " + thread_name + " key: " + sha256_hex[:8] + " : " + str(db))
            except Exception as e:
                bt.logging.error(e)
                bt.logging.error(e.with_traceback())
        bt.logging.info(
            "===> upload line {} to mysql success: thread_name: {} token list: {}".format(str(line_count), thread_name,str(len(token_list))))
    if 'my_conn' in locals() and my_conn.is_connected():
        my_conn.close()


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def verify_data(file_path):
    # human_dataset = HumanDataset()
    augmentator = DataAugmentator()
    db_conn = get_db_connection()
    count = 1
    with open(file_path, 'r') as file:
        for line in file:
            el = json.loads(line)
            augs = augmentator(el['text'])
            text = augs['text']
            if len(text) <= 250:
                print("human written text")
                continue
            list_token = index_data.cut_head_tail(text)
            if len(list_token) == 1:
                bt.logging.info("text too short" + text)
            else:
                list_result = []
                try:
                    for token in list_token:
                        m = hashlib.sha256(token.encode('UTF-8'))
                        sha256_hex = m.hexdigest()
                        hash_value = hash_code(sha256_hex)
                        db = hash_value % 10_000
                        key = sha256_hex[:8]
                        re = exist(db_conn, db, [key])
                        list_result.append(re)
                    if list_result.count(False) == 2:
                        bt.logging.info("indexing fail: " + str(count) + " :" + text)
                    else:
                        bt.logging.info("indexing success " + str(count))
                except Exception as e:
                    bt.logging.error(e)
            count += 1

    if 'db_conn' in locals() and db_conn.is_connected():
        db_conn.close()


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    arg3 = sys.argv[3]

    start_time = time.time_ns()
    # file_path = "/root/c4_dataset/c4-train.00001-of-01024.json"
    # file_path = "/root/c4_dataset/head-1000-00001.json"
    file_path = "/root/c4_dataset/head-10000-00001.json"
    if arg1 == 'load':
        load_range_one_thread(file_path, int(arg2), int(arg3))
    elif arg1 == 'verify':
        verify_data(file_path)
    elif arg1 == 'create_all':
        create_all_table(10_000)
    elif arg1 == 'truncate_all':
        truncate_all_table(10_000)
    elif arg1 == 'drop_all':
        drop_all_table(10_000)

    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")
