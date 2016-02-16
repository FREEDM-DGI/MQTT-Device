import os
import sys
import re
from freedmqtt.log import log, datalog, DEBUG, EVENT, WARNING, ERROR, RX, TX
from freedmqtt.MQTTClient import MQTTClient_Process
import time
import signal


class server(object):

    def __init__(self, p_type=1):
        self.ip = '127.0.0.1'
        self.port = 1883
        self.curr_device = ''
        self.process_index = int(0)
        self.clients = []
        self.devices = dict()
        self.all_devices = list()
        self.dev_topic = ''
        self.p_type = p_type
        self.controlled_devices = []

    def usage(self):
        print('Usage: MQTT -d <device> [options]')
        print(
            '-d  --device  <device>              The name of the Device You are Running this Client on')
        print('Options:')
        print(
            '-b  --broker  <brokerip[127.0.0.1]> The IP that the MQTT Broker is Running on')
        print(
            '-p  --port    <port[1883]>          The Port the Broker is running on')
        print('-h  --help                          Print this Usage table')

    def parse_args(self, arg_opts):
        try:
            temp = list(arg_opts)
            temp.pop()
            for o in temp[0]:
                if o[0] in ('-h', '--help'):
                    self.usage()
                    sys.exit()
                elif o[0] in ('-d', '--device'):
                    self.curr_device = o[1]
                elif o[0] in ('-p', '--port'):
                    self.port = int(o[1])
                elif o[0] in ('-b', '--broker'):
                    self.ip = o[1]
            if(self.curr_device == ''):
                print("Error Current Device Name Not Entered")
                self.usage()
                sys.exit(2)
            else:
                temp = re.split('_', self.curr_device)
                self.dev_topic = str(temp[0]) + '/' + str(temp[1])
        except:
            self.usage()
            sys.exit(2)

    def remove_files(self):
        tempdir = 'json/'
        files = os.listdir(tempdir)
        for f in files:
            if f.endswith(".json"):
                os.remove(os.path.join(tempdir, f))
        tempdir = 'log/'
        files = os.listdir(tempdir)
        for f in files:
            if f.endswith(".log"):
                os.remove(os.path.join(tempdir, f))
        tempdir = 'conf/profile/'
        files = os.listdir(tempdir)
        for f in files:
            if f != str(self.curr_device) + '.xlsx':
                os.remove(os.path.join(tempdir, f))

    def add_process(self, device_name, proc):
        self.devices[device_name] = self.process_index
        self.process_index = self.process_index + 1
        self.clients.append(proc)

    def start_client(self, msg):
        sp_topic = re.split('/', msg.topic)
        device_name = str(sp_topic[1]) + '_' + str(sp_topic[2])
        if device_name not in self.devices:
            #signal.signal(signal.SIGINT, signal.SIG_IGN)
            process = MQTTClient_Process(
                device=device_name, ip=self.ip, port=self.port, p_type=self.p_type)
            self.add_process(device_name, process)
            process.start()
            #signal.signal(signal.SIGINT, signal_handler)
        else:
            print('Warning: Device with same name ignored!!')

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0:
            print("Connected")
            print("rc: " + str(rc))
            mqttc.subscribe('join/#')
            print("Sub join")
            mqttc.subscribe('leave/#')
            print("Sub leave")
        else:
            print("Error")

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, mqttc, obj, msg):
        #print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        split_topic = re.split('/', msg.topic)
        publishing_device = str(split_topic[1]) + '_' + str(split_topic[2])
        if(split_topic[0] == 'join'):
            try:
                if(publishing_device not in self.all_devices):
                    mqttc.publish('join/' + str(self.dev_topic), 'Connect')
                    self.all_devices.append(publishing_device)
            except IndexError:
                print("Dev_Topic IndexError")
            if(publishing_device in self.controlled_devices):
                self.start_client(msg)
        elif(split_topic[0] == 'leave'):
            print("Recieved a Leave")
            if(publishing_device in self.devices):
                print("Closing device")
                os.kill(
                    self.clients[self.devices[publishing_device]].pid, signal.SIGINT)
                del self.devices[publishing_device]
            if(publishing_device in self.all_devices):
                del self.all_devices[self.all_devices.index(publishing_device)]

    def on_log(self, mqttc, obj, level, string):
        print(string)
