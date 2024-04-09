import sys


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def create_one_column_file(source_path, dest_path):
    count = 0
    with open(source_path, 'r') as source_file:
        with open(dest_path, 'w') as dest_file:
            for line in source_file:
                data = line.split(',')
                if count == 0:
                    converted_data = '\n'.join(data)
                else:
                    converted_data = '\n' + '\n'.join(data)
                dest_file.write(converted_data)
                count += 1


if __name__ == '__main__':
    arg1 = sys.argv[1]
    arg2 = sys.argv[2]
    create_one_column_file(source_path=arg1,dest_path=arg2)
