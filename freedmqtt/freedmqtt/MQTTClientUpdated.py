import os
import sys
import json
from freedmqtt.log import log, datalog, DEBUG, EVENT, WARNING, ERROR, RX, TX
from freedmqtt.DeviceProfile import DeviceProfile
import re
import jsonpickle
import datetime
import time
import paho.mqtt.client as mqtt
import multiprocessing
import threading
# from freedmqtt.jsonhandler import jsonhandler
# from watchdog.observers import Observer
TIME_CONSTANT = 0.1


class MQTTClient_Process(multiprocessing.Process):

    def __init__(self, device, ip, port, p_type=1):
        super(MQTTClient_Process, self).__init__()
        self.ip = str(ip)
        self.init_event = multiprocessing.Event()
        self.update_event = multiprocessing.Event()
        self.init_event.clear()
        self.p_type = p_type
        self.port = port
        self.missed_msg = 0
        self.daemon = True
        self.json_lock = threading.RLock()
        self.init = 0
        self.device_name = str(device)
        self.device = DeviceProfile(device, "MQTT")
        self.profile = ''
        self.dev_topic = ''
        self.start_time = datetime.datetime.now()
        # self.event_handler = JsonHandler(self.update_event)
        # self.observer = Observer()
        if(self.p_type == 0):
            self.profile = jsonpickle.encode(self.device)
            self.dev_topic = str(self.device.read_object(
                'Dev_Name')) + '/' + str(int(self.device.read_object('Dev_HW_Ver')))
        elif(self.p_type == 1 or self.p_type == 2):
            temp_topic = re.split('_', str(device))
            self.dev_topic = str(temp_topic[0] + '/' + temp_topic[1])
        if(sys.platform == 'win32'):
            print("Running on Windows")

    def on_connect(self, mqttc, obj, flags, rc):
        if rc == 0:
            print("Connected")
            print("rc: " + str(rc))
            if(self.p_type == 0):  # Current Device's Datapoint Publisher
                self.mqttc.subscribe(str(self.dev_topic) + '/AIN/#')
                print("Sub AIN")
                self.mqttc.subscribe(str(self.dev_topic) + '/DIN/#')
                print("Sub DIN")
                self.mqttc.subscribe(str(self.dev_topic) + '/ACK')
                print("Sub ACK")
                if(self.init == 0):
                    self.mqttc.publish(
                        'join/' + str(self.dev_topic), 'Connect')
                    print("Pub Join")
            elif(self.p_type == 1):
                self.mqttc.subscribe(str(self.dev_topic) + '/AOUT/#')
                print("Sub AOUT")
                self.mqttc.subscribe(str(self.dev_topic) + '/DOUT/#')
                print("Sub DOUT")
                self.mqttc.publish(str(self.dev_topic) + '/ACK', 'ACK')
                print("Pub ACK")
                self.mqttc.subscribe(str(self.dev_topic) + '/JSON/#')
                print("Sub JSON")
            elif(self.p_type == 2):
                self.mqttc.subscribe(str(self.dev_topic) + '/AIN/#')
                self.mqttc.subscribe(str(self.dev_topic) + '/DIN/#')
                self.mqttc.subscribe(str(self.dev_topic) + '/DOUT/#')
                self.mqttc.subscribe(str(self.dev_topic) + '/AOUT/#')
                print("Sub to ALL")
                self.mqttc.publish(str(self.dev_topic) + '/ACK', 'ACK')
                print("Pub ACK")
                self.mqttc.subscribe(str(self.dev_topic) + '/JSON/#')
                print("Sub JSON")
        else:
            print("Error in connect")

    def on_publish(self, mqttc, obj, mid):
        print("mid: " + str(mid))

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def on_message(self, mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        split_topic = re.split('/', msg.topic)
        if(self.p_type == 0):
            if(split_topic[2] == 'ACK'):
                if(msg.payload == 'ACK'):
                    self.mqttc.publish(
                        str(self.dev_topic) + '/JSON', str(self.profile))
                    self.mqttc.publish(
                        str(self.dev_topic) + '/JSON-DGI', str(jsonpickle.encode(self.device, unpicklable=False)))
                    if not (self.init_event.is_set()):
                        self.init_event.set()
                        self.init = 1
            else:
                self.read_command(msg)
        elif(self.p_type == 1 or self.p_type == 2 ):
            if(split_topic[2] == 'JSON'):
                file_name = str(split_topic[0]) + \
                    '_' + str(split_topic[1]) + '.json'
                file_name = 'json/' + str(file_name)
                f = open(file_name, 'a')
                f.seek(0)
                f.truncate()
                f.write(msg.payload)
                f.close()
                if not (self.init_event.is_set()):
                    self.init_event.set()
                    self.init = 1
            else:
                self.read_command(msg)

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def send_commands(self):
        while True:
            obj_topic = self.device.Delete_Change()
            log("Object to be sent " + str(obj_topic), DEBUG)
            if(obj_topic == 'Error'):
                return
            sp_topic = re.split('/', obj_topic)
            try:
                msg = self.device.read(sp_topic[0], int(sp_topic[1]))
            except ValueError as e:
                print(e)
            print(msg)
            datalog(msg,obj_topic,self.device_name,TX,(datetime.datetime.now()-self.start_time))
            self.mqttc.publish(str(self.dev_topic) + '/' + obj_topic, msg)

    def read_command(self, msg):
        self.rx_msg = msg
        log("Trying to Acquire JSON file", DEBUG,(datetime.datetime.now()-self.start_time))
        #self.json_lock.acquire()
        sp_msg = re.split('/', self.rx_msg.topic)
        try:
            log("Write " + str(sp_msg[2]) +
                str(sp_msg[3]) + "to JSON File", DEBUG,(datetime.datetime.now()-self.start_time))
            datalog(self.rx_msg.payload,str(sp_msg[2])+ '/' + str(sp_msg[3]),self.device_name,RX,(datetime.datetime.now()-self.start_time))
            self.device.write(self.rx_msg.payload, sp_msg[2], int(sp_msg[3]))
        except ValueError as e:
            print(e)
        #self.json_lock.release()

    def run(self):
        self.mqttc = mqtt.Client(
            client_id="", clean_session=True, userdata=None, protocol=3)
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_publish = self.on_publish
        self.mqttc.on_subscribe = self.on_subscribe
        self.mqttc.on_message = self.on_message
        # Uncomment to enable debug messages
        self.mqttc.on_log = self.on_log
        self.mqttc.connect(self.ip, self.port)
        # mqttc.connect('ts7800-15.ece.ncsu.edu',8883)
        self.mqttc.loop_start()
        self.init_event.wait()
        self.currtime = time.time()
        # self.observer.schedule(event_handler, 'json/' , recursive=True)
        # self.observer.start()
        while True:
            time.sleep(1)
            try:
                # self.update_event.wait()
                if((time.time() - self.currtime) > TIME_CONSTANT):
                    log("Trying to Acquire JSON file", DEBUG,(datetime.datetime.now()-self.start_time))
                    #self.json_lock.acquire()
                    try:
                        log("Check JSON for Update", DEBUG, (datetime.datetime.now()-self.start_time))
                        self.device.update_object()
                    except ValueError as e:
                        print(e)
                        continue
                    if(self.device.updated()):
                        log("Sending Commands", EVENT, (datetime.datetime.now()-self.start_time))
                        self.send_commands()
                    self.currtime = time.time()
                    #self.json_lock.release()
                # self.update_event.clear()
            except KeyboardInterrupt:
                self.mqttc.loop_stop()
                self.mqttc.disconnect()
                print("Exited Process")
                break
