'''
Created on 27/10/2014

@author: aurelio
'''
import logging
import multiprocessing as mp
import sys

def worker():
    print ('Doing some work')
    sys.stdout.flush()

if __name__ == '__main__':
    mp.log_to_stderr(logging.DEBUG) #does not work
    p = mp.Process(target=worker)
    p.start()
    p.join()
    