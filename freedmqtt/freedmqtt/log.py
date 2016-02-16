import os
import sys
import inspect
import time
from datetime import datetime
if(sys.platform == 'win32'):
    import portalocker
    from portalocker import lock, unlock, LOCK_EX
else:
    import fcntl
    from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_NB


ERROR = 3
DEBUG = 0
EVENT = 1
WARNING = 2
RX = 0
TX = 1 

levels = ["DEBUG", "EVENT", "WARNING", "ERROR"]

UNLOCK = 0
LOCK = 1


def file_lock(fd, ltype):
    if(sys.platform == 'win32'):
        if(ltype == LOCK):
            lock(fd, LOCK_EX)
        elif(ltype == UNLOCK):
            unlock(fd)
    else:
        if(ltype == LOCK):
            flock(fd, LOCK_EX)
        elif(ltype == UNLOCK):
            flock(fd, LOCK_UN)


def log(message, level=0, timestamp = '', log_file='debug.log'):
    "Automatically log the current function details."
    log_file = 'log/' + log_file
    func = inspect.currentframe().f_back.f_code
    f = open(log_file, 'a')
    file_lock(f, LOCK)
    f.write(str(timestamp) + ': ' + str(func.co_firstlineno) + ': ' + str(message) + ' in ' + str(func.co_name) + ' ' + str(func.co_filename) + '\n')
    if(sys.platform != 'win32'):
        file_lock(f, UNLOCK)
    f.close()
    #f.write(str(levels[level] + ": " + str(func.co_firstlineno) + ": " + str(message) + " in " +  str(func.co_name) + " "  + str(func.co_filename) + "\n")

def datalog(data,datatype,device,direction,timestamp = '',end = ''):
    "Log Data points"
    if(direction == 0):
        log_file = 'log/' + str(device) + '_RX.log'
    elif(direction == 1):
        log_file = 'log/' + str(device) + '_TX.log'
    f = open(log_file, 'a')
    file_lock(f, LOCK)
    if direction == 0:
        f.write(str(timestamp) + ","+ str(data) + ',' + str(datatype) + '\n')
    elif direction == 1:
        f.write(str(timestamp) + ","+ str(data) + ',' + str(datatype) + '\n')
    if(sys.platform != 'win32'):
        file_lock(f, UNLOCK)
    f.close()