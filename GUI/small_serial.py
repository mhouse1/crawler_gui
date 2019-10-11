"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/10/2019

@details         test serial coms

                 note: on the raspberry pi you must access the serial port via /dev/serial0
                 also serial port must be enabled in via "sudo raspi-config" interfacting options
"""
import serial, os, time
from Communications import *

com_handle = None

os_type = None
if os.name == 'nt':
    os_type = 'windows'
else:
    os_type = 'unix'
print('detected os_type ==',os_type)

def list_ports():
    '''
    not very usable on windows, it takes too long and sometimes hangs
    '''
    ports = serial.tools.list_ports.comports(include_links=False)
    #print(ports)
    print('listed ports')
    for port in ports:
        print(port.device)
def list_serial_ports():
    return show_serial_ports()

def initialize_serial():
    global com_handle
    # ports = list_serial_ports()
    # print('available ports:',ports)

    if os_type == 'windows':
        #assume the last serial port is what we're looking for
        #note: it will hang on write if wrong serial port
        #com_handle = serial.Serial(port = ports[-1],baudrate = 115200)
        com_handle = serial.Serial(port = 'COM7',baudrate = 115200)
    else:
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

##    data = com_handle.read(com_handle.inWaiting())
##    if data == '':
##        pass
##    else:
##        print(data)
##    #return 

    data = com_handle.read(com_handle.inWaiting())
    msg = data.decode('utf-8')
    if len(msg) > 0:
        print('read:',msg)
        
def write(message):
    global com_handle
    com_handle.write(message.encode())
    #print(message)

if __name__ == '__main__':
    initialize_serial()
    #print(read())
    msg = None
    while True:
        msg = str(input('enter your text to transmit:'))
        write(msg)
        time.sleep(0.5)#allow write to finish
        read()

