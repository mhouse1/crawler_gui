"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/10/2019

@details         serial coms
"""
import serial
from Communications import *

com_handle = None

def list_serial_ports():
    return show_serial_ports()

def initialize_serial():
    global com_handle
    ports = list_serial_ports()
    print('available ports:',ports)

    com_handle = serial.Serial(port = ports[0],baudrate = 115200)

def read():
    global com_handle
    return com_handle.read()

def write(message):
    global com_handle
    com_handle.write(message)
if __name__ == '__main__':
    initialize_serial()
    print(read())


