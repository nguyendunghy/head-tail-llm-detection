# SuperFastPython.com
# example of a program that does not use all cpu cores
import math
import time
from concurrent.futures import ProcessPoolExecutor


# define a cpu-intensive task
def task(arg):
    return sum([math.sqrt(i) for i in range(1, arg)])


# protect the entry point
def one_cpu():
    start = time.time_ns()
    # report a message
    print('Starting task...')
    # perform calculations
    results = [task(i) for i in range(1, 50000)]
    # report a message
    print(results)
    print('Done.')
    end = time.time_ns()
    print("time processing: {}".format(str((end - start) // 1000_000)))


def multi_cpu():
    # report a message
    print('Starting task...')
    # create the process pool
    with ProcessPoolExecutor(8) as exe:
        # perform calculations
        results = exe.map(task, range(1, 50000))
    # report a message
    print('Done.')


if __name__ == '__main__':
    start = time.time_ns()
    multi_cpu()
    end = time.time_ns()
    print('time processing {}'.format(str((end-start)/1000_000)))
