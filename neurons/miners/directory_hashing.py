import hashlib
import time

from neurons.miners.utils import create_hashing_directory
import bittensor as bt

NUM_LAYER = 7
BASE_PATH = ''


def load_range_one_thread(file_path, start_line, end_line):
    with open(file_path, 'r') as file:
        count = 1
        for line in file:
            if start_line <= count < end_line:
                list_hash = line.strip().split(',')
                for hash in list_hash:
                    create_hashing_directory(NUM_LAYER, BASE_PATH, hash)
            count += 1
            bt.logging.info(
                "===> indexing line {} to director success".format(str(count)))


if __name__ == '__main__':
    start_time = time.time_ns()
    BASE_PATH = '/home/ubuntu/directory_indexing'
    file = '/home/ubuntu/c4-dataset/indexed_data/c4-index-v1/00000/merge_00000.txt'
    load_range_one_thread(file, 0, 10000)
    bt.logging.info(f"time loading {int(time.time_ns() - start_time):,} nanosecond")
