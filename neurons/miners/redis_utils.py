import sys
import time
import traceback
import bittensor as bt
import redis

redis_pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)


def get_conn():
    conn = redis.Redis(connection_pool=redis_pool)
    return conn


def get_request_pred(hash_key):
    try:
        conn = get_conn()
        conn.select(0)
        value = conn.get(hash_key)
        result = []
        if value is not None:
            temp = value.decode().strip().split(',')
            result = [v == 'True' for v in temp]
            return result

        bt.logging.info("set to redis success key {}, value{}".format(hash_key, value))
        return result
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


def set_request_pred(hash_key, result):
    try:
        value = ','.join(result)
        conn = get_conn()
        conn.select(0)
        conn.setex(hash_key, 3600, value)
        bt.logging.info("set to redis success key {}, value{}".format(hash_key, value))
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


def exists_on_redis(hash_value, db):
    try:
        key = 'set-' + str(db)
        conn = get_conn()
        conn.select(db)
        return conn.sismember(key, hash_value) == 1
    except Exception as e:
        bt.logging.error(e)
        traceback.print_exc()


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
