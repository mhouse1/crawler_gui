"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/10/2019

@details         serial coms

                 note: on the raspberry pi you must access the serial port via /dev/serial0
                 also serial port must be enabled in via "sudo raspi-config" interfacting options
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

    com_handle = serial.Serial(port = r'/dev/serial0',baudrate = 115200)
    print('serial initialized',com_handle)

def read():
    global com_handle
    # line = []
    # print('reading')
    # for c in com_handle.read():
    #     line.append(c)
    #     if c == '\n':
    #         print("Line: " + ''.join(line))
    #         line = []  

    data = com_handle.read(com_handle.inWaiting())
    if data == '':
        pass
    else:
        print(data)
    #return 

def write(message):
    global com_handle
    com_handle.write(message)

if __name__ == '__main__':
    initialize_serial()
    #print(read())
    while True:
        msg = input('enter your text to transmit:')
        write(msg.encode())
        print('read',read())

