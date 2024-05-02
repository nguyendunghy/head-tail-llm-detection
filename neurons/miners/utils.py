def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def write(data, file_path):
    with open(file_path, 'a') as file:
        file.writelines(data)
