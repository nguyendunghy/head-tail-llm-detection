import hashlib


def hash_code(string) -> int:
    h = 0
    if len(string) > 0:
        for i in range(0, len(string)):
            h = 31 * h + ord(string[i])
    return h


def gen_hash(token):
    m = hashlib.sha256(token.encode('UTF-8'))
    sha256_hex = m.hexdigest()
    return sha256_hex


if __name__ == '__main__':
    print(gen_hash('abc'))