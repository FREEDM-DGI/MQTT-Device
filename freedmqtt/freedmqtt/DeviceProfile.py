import os
import sys
import time
from freedmqtt.switch import switch
from freedmqtt.log import log, DEBUG, WARNING, EVENT, ERROR
import json
import jsonpickle
import datetime
import re
import pdb
import xlrd
import inspect
if(sys.platform == 'win32'):
    import portalocker
    from portalocker import lock, unlock, LOCK_EX
else:
    import fcntl
    from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_NB

UNLOCK = 0
LOCK = 1


class aout(object):

    def __init__(self, name, index, minimum, maximum, value):
        self.name = name
        self.index = index
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

    def write(self, value):
        if (float(value) >= self.minimum and float(value) <= self.maximum):
            self.value = float(value)
        else:
            log('AOUT/' + str(self.index) + ': Write Out of Bounds', WARNING)

    def read(self):
        return self.value


class ain(object):

    def __init__(self, name, index, minimum, maximum, value):
        self.name = name
        self.index = index
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

    def write(self, value):
        if (float(value) >= self.minimum and float(value) <= self.maximum):
            self.value = float(value)
        else:
            log('AIN/' + str(self.index) + ': Write Out of Bounds', WARNING)

    def read(self):
        return self.value


class din(object):

    def __init__(self, name, index, minimum, maximum, value):
        self.name = name
        self.index = index
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

    def write(self, value):
        if (int(value) >= self.minimum and int(value) <= self.maximum):
            self.value = int(value)
        else:
            log('DIN/' + str(self.index) + ': Write Out of Bounds', WARNING)

    def read(self):
        return self.value


class dout(object):

    def __init__(self, name, index, minimum, maximum, value):
        self.name = name
        self.index = index
        self.minimum = minimum
        self.maximum = maximum
        self.value = value

    def write(self, value):
        if (int(value) >= self.minimum and int(value) <= self.maximum):
            self.value = int(value)
        else:
            log('DOUT/' + str(self.index) + ': Write Out of Bounds', WARNING)

    def read(self):
        return self.value


class dev_char(object):

    def __init__(self, name, index, value):
        self.name = name
        self.index = index
        self.value = value

    def write(self, value):
        self.value = value

    def read(self):
        return self.value


class DeviceProfile(object):

    def __init__(self, i_file_1, app_name=''):
        self.native = 0
        self.AOUT = []
        self.AIN = []
        self.DOUT = []
        self.DIN = []
        self.DEV_CHAR = []
        self.Name_Hash = {}
        self.Topic_Hash = {}
        self.change = ['Error']
        self.file_1 = 'json/' + str(i_file_1) + '.json'
        self.flag = 0
        self.write_time = 0
        self.initialized = 0
        self.start_time = (datetime.datetime.now())
        try:
            book = xlrd.open_workbook(
                str('conf/profile/' + i_file_1) + '.xlsx')
            self.native = 1
            sh = book.sheet_by_index(1)
            # print sh.name, sh.nrows, sh.ncols
            self.xlx_parser(sh)
            self.file_1 = 'json/' + str(self.read_object(
                'Dev_Name')) + '_' + str(int(self.read_object('Dev_HW_Ver'))) + '.json'
            self.set_initialized()
            if(not os.path.exists(self.file_1)):
                f = open(self.file_1, 'w')
                self.file_lock(f, LOCK)
                self.write_time = datetime.datetime.now()
                f.write(jsonpickle.encode(self))
                if(sys.platform != 'win32'):
                    self.file_lock(f, UNLOCK)
                f.close()
                log("Created JSON File", EVENT)
        except IOError:
            log("Not Native Process", DEBUG)
            self.native = 0
        self.app_name = str(app_name)
        log("Initialized bit:" + str(self.initialized), DEBUG)

    def xlx_parser(self, sh):
        for rx in range(sh.nrows):
            dtype = sh.cell(rx, 0).value
            name = sh.cell(rx, 1).value
            index = int(sh.cell(rx, 2).value)
            if(re.match(r'(.*)IN', str(dtype))):
                self.Name_Hash[
                    str(name) + 'IN'] = str(dtype) + '/' + str(index)
            elif(re.match(r'(.*)OUT', str(dtype))):
                self.Name_Hash[
                    str(name) + 'OUT'] = str(dtype) + '/' + str(index)
            else:
                self.Name_Hash[str(name)] = str(dtype) + '/' + str(index)
            self.Topic_Hash[str(dtype) + '/' + str(index)] = str(name)
            minimum = float(sh.cell(rx, 3).value)
            maximum = float(sh.cell(rx, 4).value)
            if (dtype == 'DEV_CHAR'):
                value = (sh.cell(rx, 5).value)
            else:
                value = float(sh.cell(rx, 5).value)
            self.add_element(dtype, name, index, minimum, maximum, value)

    def add_element(self, dtype, name, index, minimum, maximum, value):
        if(dtype == 'AOUT'):
            self.AOUT.append(aout(name, index, minimum, maximum, value))
        elif (dtype == 'AIN'):
            self.AIN.append(ain(name, index, minimum, maximum, value))
        elif (dtype == 'DIN'):
            self.DIN.append(din(name, index, minimum, maximum, value))
        elif (dtype == 'DOUT'):
            self.DOUT.append(dout(name, index, minimum, maximum, value))
        elif (dtype == 'DEV_CHAR'):
            self.DEV_CHAR.append(dev_char(name, index, value))
        else:
            log("Invalid Entry in Excel sheet", ERROR)

    def file_lock(self, fd, ltype):
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

    def try_initialize(self):
        try:
            f = open(self.file_1, 'r')
        except IOError:
            log("JSON file doesnt exist/Cant Read", DEBUG)
            return 0
        self.file_lock(f, LOCK)
        f.seek(0, 0)
        line = f.readline()
        Temp = jsonpickle.decode(line)
        if(sys.platform != 'win32'):
            self.file_lock(f, UNLOCK)
        f.close()
        self.AOUT = Temp.AOUT
        self.AIN = Temp.AIN
        self.DOUT = Temp.DOUT
        self.DIN = Temp.DIN
        self.DEV_CHAR = Temp.DEV_CHAR
        self.Name_Hash = Temp.Name_Hash
        self.Topic_Hash = Temp.Topic_Hash
        self.change = Temp.change
        self.file_1 = self.file_1
        self.set_initialized(Temp.flag, Temp.write_time)
        log("Listening Object Initialized", EVENT)
        return 1

    def Record_Change(self, type_1):
        log("Recording change " + str(self.initialized), DEBUG)
        if(self.initialized == 1):
            temp = set(self.change)
            if type_1 not in temp:
                self.flag = self.flag + 1
                log("Flag: " + str(self.flag), DEBUG)
                self.change.append(type_1)

    def Delete_Change(self):
        log("Poping change", DEBUG)
        if(self.flag != 0):
            self.flag = self.flag - 1
            log("Flag: " + str(self.flag), DEBUG)
            return self.change.pop()
        else:
            return 'Error'

    def Delete_All_Changes(self):
        while True:
            temp = self.Delete_Change()
            if(temp == 'Error'):
                return

    def update_object(self):
        if(self.initialized):
            try:
                f = open(self.file_1, 'r+')
            except IOError:
                log("JSON File doesnt exist/Cant Read", DEBUG)
                raise ValueError('JSON File Read Error')
                return
            self.file_lock(f, LOCK)
            f.seek(0, 0)
            line = f.readline()
            Temp = jsonpickle.decode(line)
            if(self.write_time != Temp.write_time):
                log("Updated Object", EVENT)
                self.addchanges(Temp)
                self.write_time = Temp.write_time
            else:
                log("Object not Updated", EVENT)
                if(sys.platform != 'win32'):
                    self.file_lock(f, UNLOCK)
                f.close()
                return
            f.seek(0, 0)
            f.write(jsonpickle.encode(Temp))
            log("update_object: Wrote Temp to File", EVENT)
            f.truncate()
            if(sys.platform != 'win32'):
                self.file_lock(f, UNLOCK)
            f.close()
        else:
            self.try_initialize()

    def write_file(self, value, datatype, index):
        try:
            f = open(self.file_1, 'r+')
        except IOError:
            log("JSON File Doesn't Exist", ERROR)
            f = open(self.file_1, 'w')
            self.file_lock(f, LOCK)
            self.write_time = datetime.datetime.now()
            f.write(jsonpickle.encode(self))
            self.file_lock(f, UNLOCK)
            f.close()
            self.Delete_All_Changes()
            log("Created JSON file", EVENT)
            return
        self.file_lock(f, LOCK)
        line = f.readline()
        Temp = jsonpickle.decode(line)
        for case in switch(datatype):
            if case('DIN'):
                Temp.DIN[index].write(value)
                if(self.app_name != "MQTT"):
                    Temp.Record_Change('DIN/' + str(index))
                break
            if case('AOUT'):
                Temp.AOUT[index].write(value)
                if(self.app_name != "MQTT"):
                    Temp.Record_Change('AOUT/' + str(index))
                break
            if case('AIN'):
                Temp.AIN[index].write(value)
                if(self.app_name != "MQTT"):
                    Temp.Record_Change('AIN/' + str(index))
                break
            if case('DOUT'):
                Temp.DOUT[index].write(value)
                if(self.app_name != "MQTT"):
                    Temp.Record_Change('DOUT/' + str(index))
                break
            if case('DEV_CHAR'):
                Temp.DEV_CHAR[index].write(value)
                if(self.app_name != "MQTT"):
                    Temp.Record_Change('DEV_CHAR/' + str(index))
                break
            if case():
                log('Error in DataType', ERROR)
                break
        self.write_time = datetime.datetime.now()
        Temp.write_time = self.write_time
        f.seek(0, 0)
        f.write(jsonpickle.encode(Temp))
        log("wrote " + str(value) + " to " + str(datatype) + str(index), DEBUG, (datetime.datetime.now()-self.start_time))
        f.truncate()
        if(sys.platform != 'win32'):
            self.file_lock(f, UNLOCK)
        f.close()
        # self.Delete_All_Changes()
        return

    def addchanges(self, from_prf):
        log("Adding changes", DEBUG)
        while(True):
            temp = from_prf.Delete_Change()
            if (temp == 'Error'):
                return
            sp_temp = re.split('/', temp)
            self.move(from_prf, sp_temp[0], int(sp_temp[1]))

    def updated(self):
        log("Flag: " + str(self.flag), DEBUG)
        if(self.flag > 0):
            return True
        #self.log("updated: No Recorded Changes")
        return False

    def set_initialized(self, flag=0, write_time=0):
        self.flag = flag
        self.write_time = write_time
        self.initialized = 1
        log("Initialized " + str(self.initialized), DEBUG)

    def read(self, attribute, index=-1):
        if(self.initialized == 1):
            if(index == -1):
                try:
                    temp_type = self.Name_Hash[attribute]
                except KeyError:
                    if(self.native):
                        attribute = str(attribute) + 'IN'
                    else:
                        attribute = str(attribute) + 'OUT'
                    try:
                        temp_type = self.Name_Hash[attribute]
                    except KeyError:
                        log("KeyError Exception in read", ERROR)
                        raise ValueError('Bad Attribute')
                        return
                sp_temp = re.split('/', temp_type)
                datatype = sp_temp[0]
                index = int(sp_temp[1])
            else:
                datatype = attribute
                log("Bypass READ Access", EVENT)
            return self.read_file(datatype, int(index))
        else:
            if(self.try_initialize()):
                return self.read(attribute, int(index))
            else:
                log("JSON File Does not exist to Create Object", WARNING)
                log("Unable to Read from " +
                    str(attribute) + "/" + str(index), DEBUG)
                raise ValueError('No Device')

    def write(self, value, attribute, index=-1):
        if(self.initialized == 1):
            if(index == -1):
                try:
                    temp_type = self.Name_Hash[attribute]
                except KeyError:
                    if(self.native):
                        attribute = str(attribute) + 'OUT'
                    else:
                        attribute = str(attribute) + 'IN'
                    try:
                        temp_type = self.Name_Hash[attribute]
                    except KeyError:
                        log("KeyError in write", ERROR)
                        raise ValueError('Bad Attribute')
                        return
                sp_temp = re.split('/', temp_type)
                datatype = sp_temp[0]
                index = int(sp_temp[1])
            else:
                datatype = attribute
                log("Bypass WRITE Access", EVENT)
            # self.Delete_All_Changes()
            self.write_file(value, datatype, int(index))
            return 1
        else:
            if(self.try_initialize()):
                self.write(value, attribute, int(index))
            else:
                log("JSON File Does not Exist to Create Object", WARNING)
                log("Value: " + str(value) + " Not Written to " +
                    str(attribute) + "/" + str(index), DEBUG)
                raise ValueError('No Device')

    def move(self, new_profile, datatype, index):
        for case in switch(datatype):
            if case('DIN'):
                self.DIN[index] = new_profile.DIN[index]
                self.Record_Change('DIN/' + str(index))
                break
            if case('AOUT'):
                self.AOUT[index] = new_profile.AOUT[index]
                self.Record_Change('AOUT/' + str(index))
                break
            if case('AIN'):
                self.AIN[index] = new_profile.AIN[index]
                self.Record_Change('AIN/' + str(index))
                break
            if case('DOUT'):
                self.DOUT[index] = new_profile.DOUT[index]
                self.Record_Change('DOUT/' + str(index))
                break
            if case('DEV_CHAR'):
                self.DEV_CHAR[index] = new_profile.DEV_CHAR[index]
                self.Record_Change('DEV_CHAR/' + str(index))
                break
        log("updated " + str(datatype) + str(index), DEBUG)

    def read_object(self, attribute, index=-1):
        if(index == -1):
            try:
                temp_type = self.Name_Hash[attribute]
            except KeyError:
                log("Error in attribute", ERROR)
                return
            sp_temp = re.split('/', temp_type)
            datatype = sp_temp[0]
            index = int(sp_temp[1])
        else:
            datatype = attribute
        for case in switch(datatype):
            if case('DIN'):
                return self.DIN[index].read()
                break
            if case('AOUT'):
                return self.AOUT[index].read()
                break
            if case('AIN'):
                return self.AIN[index].read()
                break
            if case('DOUT'):
                return self.DOUT[index].read()
                break
            if case('DEV_CHAR'):
                return self.DEV_CHAR[index].read()
                break

    def read_file(self, datatype, index):
        try:
            f = open(self.file_1, 'r')
            self.file_lock(f, LOCK)
            f.seek(0, 0)
            line = f.readline()
        except IOError:
            log("JSON file doesnt exist/Cant Read", ERROR)
            log("Trying Direct Object Read", WARNING)
            return self.read_object(datatype, index)
        Temp = jsonpickle.decode(line)
        for case in switch(datatype):
            if case('DIN'):
                data = Temp.DIN[index].read()
                break
            if case('AOUT'):
                data = Temp.AOUT[index].read()
                break
            if case('AIN'):
                data = Temp.AIN[index].read()
                break
            if case('DOUT'):
                data = Temp.DOUT[index].read()
                break
            if case('DEV_CHAR'):
                data = Temp.DEV_CHAR[index].read()
                break
        if(sys.platform != 'win32'):
            self.file_lock(f, UNLOCK)
        f.close()
        log("Read " + str(data) + " from " + str(datatype) + str(index), DEBUG,(datetime.datetime.now()-self.start_time))
        return data
