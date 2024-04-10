import sys
from pathlib import Path

import bittensor as bt


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


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


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    create_10000_file_from_merge_all(source_path=arg1, dest_dir_path=arg2)
