import hashlib
import sys
import time
from pathlib import Path

import bittensor as bt

LAYER_NAME = ['A', 'B', 'C', 'D', 'E', 'F', 'G',
              'H', 'I', 'J', "K", 'L', 'M', 'N',
              'O', 'P', 'Q', 'R', 'S', 'T', 'U',
              'V', 'W', 'X', 'Y', 'Z']
NUM_DB = 10_000
HASH_LEN = 8


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def hash_code_java(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    h = (h + 2 ** 31) % 2 ** 32 - 2 ** 31
    return -h if h < 0 else h


def gen_hash_and_db(token):
    m = hashlib.sha256(token.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    db = hash_code(sha256_hex) % NUM_DB
    hash_value = sha256_hex[:HASH_LEN]
    return hash_value, db


def create_one_column_file(source_path, dest_path):
    count = 1
    is_first_not_empty_line = True
    with open(source_path, 'r') as source_file:
        with open(dest_path, 'w') as dest_file:
            for line in source_file:
                temp_data = line.strip().split(',')
                data = [ele for ele in temp_data if len(ele.strip()) > 0]
                if len(data) > 0:
                    if is_first_not_empty_line:
                        converted_data = '\n'.join(data)
                        is_first_not_empty_line = False
                    else:
                        converted_data = '\n' + '\n'.join(data)
                    dest_file.write(converted_data)
                bt.logging.info("data at line {} converted".format(str(count)))
                count += 1


def create_10000_file_from_merge_all(source_path, dest_dir_path):
    db = 0
    with open(source_path, 'r') as source_file:
        for line in source_file:
            data = line.strip().split(',')
            converted_data = '\n'.join(data)
            file_name = 'table_{}.csv'.format(str(db))
            file_path = dest_dir_path + '/group-' + str(db // 1000) + '/' + file_name
            with open(file_path, 'w') as des_file:
                des_file.write(converted_data)
            bt.logging.info("data at line {} converted".format(str(db)))
            db += 1


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


def create_directory(dir_path):
    directory_path = Path(dir_path)
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)
        bt.logging.info(f"Directory created: {directory_path}")


def gen_dir_path(layer, base_path, name):
    m = hashlib.sha256(name.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    hash_value = hash_code(sha256_hex)
    dir_path = base_path
    for i in range(layer):
        dir_path += '/' + str(hash_value % 100)
        hash_value = hash_value // 100
    dir_path += '/' + name
    return dir_path


def create_hashing_directory(layer, base_path, name):
    dir_path = gen_dir_path(layer, base_path, name)
    create_directory(dir_path)


def check_dir_exists(layer, base_path, name):
    dir_path = gen_dir_path(layer, base_path, name)
    directory_path = Path(dir_path)
    return directory_path.exists()


if __name__ == '__main__':
    start_time = time.time_ns()

    create_hashing_directory(10, '/Users/nannan/IdeaProjects/bittensor/head-tail-llm-detection', 'adf32fs')
    print(check_dir_exists(10, '/Users/nannan/IdeaProjects/bittensor/head-tail-llm-detection', 'adf32f'))
    # arg1 = sys.argv[1]
    # arg2 = sys.argv[2]
    # create_10000_file_from_merge_all(source_path=arg1, dest_dir_path=arg2)
    # for i in range(32):
    # print("nohup python3 redis_utils.py load_dir {} {} > redis{}.log &".format(str(i), str(i + 1), str(i)))
    bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
