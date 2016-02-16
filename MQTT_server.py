#!/usr/bin/env python
import sys
import getopt
from freedmqtt.server import server
from freedmqtt.MQTTClient import MQTTClient_Process
import time
import paho.mqtt.client as mqtt
import signal


if __name__ == '__main__':
    mqttc = mqtt.Client(
        client_id="", clean_session=True, userdata=None, protocol=3)
    serveri = server()
    exit_flag = 0

    def signal_handler(signal, frame):
        print("Stopping MQTT")
        try:
            mqttc.publish(
                'leave/' + str(serveri.dev_topic), "Disconnect")
        except:
            print("Error with Dev_Topic")
        for device in serveri.clients:
            try:
                #time.sleep(1)
                device.join()
            except:
                pass
        sys.exit()

    signal.signal(signal.SIGINT, signal_handler)
    try:
        opts = getopt.getopt(
            sys.argv[1:], "hd:b:p:", ["help", "broker=", "port=", "device="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print('Error in Arguments passed')
        serveri.usage()
        sys.exit(2)
    serveri.parse_args(opts)
    serveri.remove_files()
    serveri.controlled_devices = []
    try:
        with open('conf/' + str(serveri.curr_device) + '.conf') as f:
            for line in f:
                serveri.controlled_devices.append(line.strip())
        f.close()
    except ValueError as e:
        print(str(e))
    except:
        print("No Configuration File Found")
    process = MQTTClient_Process(device=serveri.curr_device, ip=serveri.ip,
                                 port=serveri.port, p_type=0)

    serveri.add_process(serveri.curr_device, process)
    try:
        mqttc.will_set('leave/' + str(serveri.dev_topic), "Disconnect")
    except IndexError:
        print("Will not set")

    mqttc.on_connect = serveri.on_connect
    mqttc.on_publish = serveri.on_publish
    mqttc.on_subscribe = serveri.on_subscribe
    mqttc.on_message = serveri.on_message
    # Uncomment to enable debug messages
    mqttc.on_log = serveri.on_log
    mqttc.connect(serveri.ip, serveri.port)
    process.start()
    serveri.all_devices.append(serveri.curr_device)
    mqttc.loop_start()
    while True:
        time.sleep(1)
        try:
            pass
        except KeyboardInterrupt:
            signal_handler()
            raise signal.SIGINT
            break
