# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
#Smart Weather Station
 
# Import necessary libraries and modules
import machine, network
from machine import Pin, SoftI2C
import time
from time import sleep
import ubinascii
from umqttsimple import MQTTClient
 
# Function to connect to Wi-Fi
ssid = "DCETLocalVOIP"
def wifi_connect():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect("DCETLocalVOIP", "")
    while not station.isconnected():
        time.sleep(1)
        print('Connecting to Wi-Fi...')
        print('Connected to Wi-Fi')
        break
 
# Function to connect to MQTT broker
def connect(client_id, mqtt_server):
    client = MQTTClient(client_id, mqtt_server)
    client.connect()
    return client
 

# Function to handle reconnection to MQTT broker
def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    sleep(10); machine.reset()
    # Wi-Fi credentials
    ssid = 'DCETLocalVOIP'; password = ''
    # Connect to Wi-Fi
wifi_connect()
mqtt_server = '192.168.1.200'
topic_pub = b'IMU'
client_id = ubinascii.hexlify(machine.unique_id())
# MQTT broker details
while True:
    print('Connecting to MQTT Broker')
    try:
        client = connect(client_id, mqtt_server)
        print('\n MQTT Connection Successful :) \n'); break
    except OSError as e: print('sleep'); sleep(1)
 
    except OSError as e:
        restart_and_reconnect()
 
# Define the I2C bus
i2c = SoftI2C(freq=4000, scl=Pin(22), sda=Pin(23))
MPU_ADDR = 0x68  # MPU-6050 I2C address
 
# Define sensitivity constants
ACCEL_SENS = 16384.0  # 2g / (1 / 16384)
GYRO_SENS = 131.0  # 250 degrees/s / (1 / 131)
 
def read_sensor():
    """Reads accelerometer and gyroscope data from the MPU-6050 sensor."""
    # Read 14 bytes from the MPU-6050
    data = i2c.readfrom_mem(MPU_ADDR, 0x3B, 14)
 
    # Convert the data
    accel_x = (data[0] << 8 | data[1]) if (data[0] << 8 | data[1]) < 32768 else (data[0] << 8 | data[1]) - 65536
    accel_y = (data[2] << 8 | data[3]) if (data[2] << 8 | data[3]) < 32768 else (data[2] << 8 | data[3]) - 65536
    accel_z = (data[4] << 8 | data[5]) if (data[4] << 8 | data[5]) < 32768 else (data[4] << 8 | data[5]) - 65536
    temp = (data[6] << 8 | data[7]) if (data[6] << 8 | data[7]) < 32768 else (data[6] << 8 | data[7]) - 65536
    gyro_x = (data[8] << 8 | data[9]) if (data[8] << 8 | data[9]) < 32768 else (data[8] << 8 | data[9]) - 65536
    gyro_y = (data[10] << 8 | data[11]) if (data[10] << 8 | data[11]) < 32768 else (data[10] << 8 | data[11]) - 65536
    gyro_z = (data[12] << 8 | data[13]) if (data[12] << 8 | data[13]) < 32768 else (data[12] << 8 | data[13]) - 65536
 
    # Apply sensitivity conversions
    accel_x = accel_x / ACCEL_SENS
    accel_y = accel_y / ACCEL_SENS
    accel_z = accel_z / ACCEL_SENS
    gyro_x = gyro_x / GYRO_SENS
    gyro_y = gyro_y / GYRO_SENS
    gyro_z = gyro_z / GYRO_SENS
 
    # Return data as a dictionary
    return {
        "accel_x": accel_x,
        "accel_y": accel_y,
        "accel_z": accel_z,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z,
    }
 
# Wake up the MPU-6050 as it starts in sleep mode
i2c.writeto_mem(MPU_ADDR, 0x6B, b'\x00')
i=0
devic_ID='1'
while True:
    i+=1
    # Read sensor data
    data = read_sensor()
 
    # Get current timestamp
    current_time = time.time()
    local_time = time.localtime(current_time)
    # Manually format the time
    formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
        local_time[0], local_time[1], local_time[2],
        local_time[3], local_time[4], local_time[5]
    )
    # Print the data
    print("Local time:", formatted_time)
    # Print data to console
    print(f"Accelerometer: x: {data['accel_x']}, y: {data['accel_y']}, z: {data['accel_z']}")
    print(f"Gyroscope: x: {data['gyro_x']}, y: {data['gyro_y']}, z: {data['gyro_z']}")
    print("")
        # Prepare data for MQTT and CSV
    mqtt_data = (f"devic_ID: {devic_ID}",',',f"No: {i}",',',f"Timestamp: {formatted_time}",',', f"Accelerometer: x: {data['accel_x']}, y: {data['accel_y']}, z: {data['accel_z']}",',', f"Gyroscope: x: {data['gyro_x']}, y: {data['gyro_y']}, z: {data['gyro_z']}")
    # Write data to CSV file
    try:
        msg = bytes(" ".join(mqtt_data), 'utf-8')
        client.publish(topic_pub, msg)
        print('Message:', msg, 'sent to topic:', topic_pub, '\n')
 
    except OSError as e:
        # If publishing to MQTT fails, handle the exception
        print("Failed to publish message:", e)
        restart_and_reconnect()
    # Add a delay to avoid overwhelming the system with rapid publishing
    sleep(0.2)
    if i>10:break