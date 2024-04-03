import copy
import hashlib
import json
import threading
import time

import bittensor as bt
import mysql.connector
import mysql.connector.pooling

import index_data
from detection.validator.data_augmentation import DataAugmentator

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="jackie_pool",
    pool_size=32,
    pool_reset_session=True,
    host='localhost',
    port='8888',
    database='ai_generated_text',
    user='jackie',
    password='jackie_password'
)


def get_db_connection():
    return connection_pool.get_connection()


def exist(db_connection, db, hash_value):
    cursor = db_connection.cursor()
    sql = "select * from table_{} where hash = (%s)".format(str(db))

    cursor.execute(sql, tuple(hash_value))
    count_result = cursor.fetchone()[0]

    cursor.close()
    return count_result > 0


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
    print(cursor.rowcount, "record inserted.")


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


def create_all_table(num_db):
    for i in range(num_db):
        create_table(get_db_connection(), i)


def truncate_all_table(num_db):
    for i in range(num_db):
        truncate_table(get_db_connection(), i)


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


def load_record(list_data, thread_name):
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

        bt.logging.info("===> upload line to redis success: thread_name: " + thread_name + " : " + str(len(token_list)))
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
                    db = hash_value % 10_000
                    key = sha256_hex[:8]
                    re = exist(get_db_connection(), db, [key])
                    list_result.append(re)
                if list_result.count(False) == 2:
                    bt.logging.info("indexing<==>fail: " + text)
                else:
                    bt.logging.info("indexing success")


if __name__ == '__main__':
    start_time = time.time_ns()
    # file_path = "/root/c4_dataset/c4/extracted_file/c4-train.00001-of-01024.json"
    # file_path = "/root/c4_dataset/c4/extracted_file/head-1000-00001.json"
    file_path = "/root/c4_dataset/c4/extracted_file/tail-2000-00001.json"
    # load(file_path)
    # create_all_table(10_000)
    # truncate_all_table(10_000)
    verify_data(file_path)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time)}nanosecond")
