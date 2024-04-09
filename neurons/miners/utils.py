import sys
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
                line = line.strip()
                if len(line) > 0 and len(line.replace(',', '')) > 0:
                    data = line.split(',')
                    if is_first_not_empty_line:
                        converted_data = '\n'.join(data)
                        is_first_not_empty_line = False
                    else:
                        converted_data = '\n' + '\n'.join(data)
                    dest_file.write(converted_data)
                bt.logging.info("data at line {} converted".format(str(count)))
                count += 1


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    create_one_column_file(source_path=arg1, dest_path=arg2)
