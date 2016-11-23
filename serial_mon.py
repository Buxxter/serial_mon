#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import serial
import time
import paho.mqtt.client as mqtt

import logging.config

logging.config.fileConfig('log.conf')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False


def handle_data(data):

    if data in trash:
        # logger.debug('trash .{0}.'.format(data))
        return
    elif '0b' in data:
        mqttc.publish(topic='/devices/room/light/state', payload=data.replace('0b', ''))
    elif 'btn_' in data:
        logger.debug(data)
        btn_params = data.split(',', 3)
        logger.debug(btn_params)
        mqttc.publish(topic='/devices/room/buttons/{}'.format(btn_params[0].replace('btn_', '')),
                      payload='{},{}'.format(btn_params[1], btn_params[2]))
        mqttc.publish(topic=TOPIC_TX, payload='light bin')
    else:
        mqttc.publish(topic='/serial{}/log'.format(serial_port.port), payload=data)

    logger.debug(data)
    # mqttc.publish(topic='/devices/room/buttons')


def read_from_port(ser):
    global connected
    while not connected:
        connected = True

        while True:
            try:
                data = ser.readline().decode()
            except serial.SerialException() as ex:
                ser.open()
                mqttc.publish(topic='/serial{}/errors'.format(serial_port.port), payload=ex)

            if data is not None and len(data.strip()) > 0:
                handle_data(data=data.strip())


def bt_override(state):
    # serial_port.write(bytearray('bt_override on\r\n', 'ascii'))
    mqttc.publish(topic=TOPIC_TX, payload='bt_override {}'.format(state))


def on_connect(client, userdata, rc):
    logger.debug('Connected with status code' + str(rc))
    client.subscribe(topic=topic_device + '/#')


def on_message(client, userdata, msg):
    logger.debug('{}: {}'.format(msg.topic, msg.payload))
    if TOPIC_TX in msg.topic:
        serial_port.write(msg.payload + b'\r\n')
    elif TOPIC_BTN_OVERRIDE in msg.topic:
        global bt_override_state
        bt_override_state = 'on' if (b'1' in msg.payload) else 'off'
        bt_override(bt_override_state)


connected = False

port = '/dev/ttyUSB0'
baud = 115200

serial_port = serial.Serial(port=port, baudrate=baud, timeout=20)
serial_port.flushInput()
serial_port.flushOutput()
serial_port.write(b'echo off\n')
bt_override_state = 'off'


trash = ['ok', 'err']
topic_device = '/serial{}'.format(serial_port.port)
TOPIC_TX = topic_device + '/tx_buffer'
TOPIC_BTN_OVERRIDE = topic_device + '/bt_override'


mqttc = mqtt.Client(client_id="pythonpub")
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect('localhost')
mqttc.loop_start()

# mqttc.publish(topic='/devices/debug', payload='Hello world!')


thread = threading.Thread(target=read_from_port, name='read_from_port', args=(serial_port,))
thread.daemon = True
thread.start()

try:
    while True:
        mqttc.publish(topic=TOPIC_BTN_OVERRIDE, payload=(1 if 'on' == bt_override_state else 0))
        time.sleep(7)
except KeyboardInterrupt:
    mqttc.loop_stop()
    thread.join(timeout=0.1)
    # raise


