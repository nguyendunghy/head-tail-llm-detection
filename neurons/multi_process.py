# SuperFastPython.com
# example of a program that does not use all cpu cores
import math


# define a cpu-intensive task
def task(arg):
    return sum([math.sqrt(i) for i in range(1, arg)])


# protect the entry point
if __name__ == '__main__':
    # report a message
    print('Starting task...')
    # perform calculations
    results = [task(i) for i in range(1, 50000)]
    # report a message
    print(results)
    print('Done.')
