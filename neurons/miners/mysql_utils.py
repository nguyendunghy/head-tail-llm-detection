import copy
import hashlib
import json
import threading
import bittensor as bt
import mysql.connector
import mysql.connector.pooling

import index_data

connection_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="jackie_pool",
    pool_size=20,
    pool_reset_session=True,
    host='localhost',
    port='8888',
    database='ai_generated_text',
    user='jackie',
    password='jackie_password'
)


def get_db_connection():
    return connection_pool.get_connection()


def insert(db_connection, db, hash_value):
    cursor = db_connection.cursor()

    table_name = 'table_' + str(db)
    sql = "INSERT INTO " + table_name + " (hash) VALUES (%s)"
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
        db_connection.close()
        bt.logging.info("create table_{} success".format(str(db)))
    except Exception as e:
        bt.logging.error(e)
    finally:
        if 'db_connection' in locals() and db_connection.is_connected():
            db_connection.close()

def create_all_table(num_db):
    for i in range(num_db):
        create_table(get_db_connection(), i)


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
                                                 args=(get_db_connection(), tmp_list_data, thread_name))
                    my_thread.start()
                    thread_count += 1
                except Exception as e:
                    bt.logging.error(e)
                list_data = []

            count += 1
            bt.logging.info("---> upload line count: " + str(count))

        if len(list_data) > 0:
            try:
                load_record(get_db_connection(), list_data, "thread-main")
            except Exception as e:
                bt.logging.error(e)


def load_record(conn, list_data, thread_name):
    for data in list_data:
        token_list = index_data.index_data(data)
        for token in token_list:
            try:
                m = hashlib.sha256(token.encode('UTF-8'))
                sha256_hex = m.hexdigest()
                hash_value = hash_code(sha256_hex)
                db = hash_value % 10_000

                bt.logging.info(
                    "upload success thread_name: " + thread_name + " key: " + sha256_hex[:8] + " : " + str(db))
            except Exception as e:
                bt.logging.error(e)
        bt.logging.info("===> upload line to redis success: thread_name: " + thread_name + " : " + str(len(token_list)))


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


if __name__ == '__main__':
    create_all_table(10_000)
