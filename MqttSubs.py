import machine
import network
import ubinascii
from umqttsimple import MQTTClient
from utime import sleep
 
# Wi-Fi credentials
ssid = 'DCETLocalVOIP'
password = ''
 
def wifi_connect():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    while not station.isconnected():
        print('Connecting to Wi-Fi...')
        sleep(1)
    print('Wi-Fi Connection Successful :)')
 
def sub_cb(topic, msg):
    print((topic, msg))
 
def connect_and_subscribe():
    client = MQTTClient(client_id, mqtt_server)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client
 
def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    sleep(10)
    machine.reset()
 
wifi_connect()
mqtt_server = '192.168.1.200'
client_id = ubinascii.hexlify(machine.unique_id())
topic_sub = b'IMU'
 
while True:
    print('Connecting to MQTT Broker...')
    try:
        client = connect_and_subscribe()
        print('\nMQTT Connection Successful :)\n')
        break
    except OSError as e:
        print('Failed to connect to MQTT broker. Retrying...')
        sleep(1)
        continue
 
while True:
    try:
        client.check_msg()
    except OSError as e:
        restart_and_reconnect()