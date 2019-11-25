'''
Created on Nov 15, 2019

@author: Mike

@brief    contains serial communication functionality
            Supported features: ability to list serial ports available, set active serial port,
                                buffer messages to be sent into a queue and send using a parallel process
'''
from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import str
from builtins import range
import os, sys, glob

import serial
from serial.tools import list_ports
import time
import multiprocessing
import threading
import queue
import struct

import data_parser

#active_serial = None
serial_activated = False
consumer_portname = None
com_handle = None
logged_in_into_user_side_radio = False

fast_queue = queue.Queue()
slow_queue = queue.Queue()
stop_sending = False

data_frame = {'incline':3, 'encoder1':3
              }

def SendCommand(addr,val):
    if type(val) == bool:
        val = 1 if val else 0
    full_command = data_parser.generate_crawler_comand(addr,val)
    #print('send command',addr,val)
    #string_command = 'CMD:{},{}'.format(addr,val)
    transmit(full_command)
    # vv=struct.pack('Hh',addr,val)
    # transmit(vv)

def transmit(message, transmit_speed = 0):
    #where messages is a list of framed data
    #print 'transmitting...'
    #if not active_serial == None:
    
    #log transmitted message into a text file
    #the file can then be read by CUTE unit test to simulate
    #actual data sent over serial channel
    #//c++ usage example
    #CommSimple listener;
    #
    #std::fstream myfile("c:/bytestream0.txt", std::ios_base::in);
    #
    #int a;
    #while (myfile >> a)
    #{
    #    //printf("%d ", a);
    #    listener.input(a);
    #}

    #enable code below to capture transmitted data
    # default_file_name = 'bytestream'
    # default_file_ext = '.txt'
    # default_file_index = 0
    # file_name = default_file_name+str(default_file_index)+default_file_ext
    # with open(file_name, "a") as myfile:
    #     for char in message:
    #         myfile.write(str(ord(char))+' ')
    #         #myfile.write(char)
    #     #myfile.write(message[:-1])
    message = message+'\r'
    if transmit_speed == 0:
        #print 'putFast',message
        fast_queue.queue.clear()
        fast_queue.put(message)
        
    else:
        #print 'putSlow',message
        slow_queue.put(message)

def show_serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(16)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def list_serial_ports():
    return show_serial_ports()

# def list_serial_ports():
#    '''
#    deprecated, use show_serial_ports() instead

#    returns a list of available serial ports
#    '''
#    # Windows
#    if os.name == 'nt':
#        #return []
#        # Scan for available ports.
#        available = []
#        for i in range(256):
#            try:
#                s = serial.Serial(i)
               
#                available.append('COM'+str(i + 1))
#                s.close()
#            except serial.SerialException:
#                pass
#        return available
#    else:
#        # Mac / Linux
#        return [port[0] for port in list_ports.comports()]
#        #['/dev/cu.Michael-SerialServer-1', '/dev/cu.MikeHousesiPod-Wireless', '/dev/cu.Bluetooth-Modem', '/dev/cu.Bluetooth-Incoming-Port', '/dev/cu.MikeHousesiPhone-Wirele']

#        #['/dev/cu.Michael-SerialServer-1', '/dev/cu.MikeHousesiPod-Wireless', '/dev/cu.Bluetooth-Modem', '/dev/cu.Bluetooth-Incoming-Port', '/dev/cu.MikeHousesiPhone-Wirele', '/dev/cu.SLAB_USBtoUART']

def set_writer(baud_rate = 19200, bytesize = 8, timeout = 1, ):
    '''
        this function will be called once when the GUI first initializes
        it then waits until the user sets an active serial chanel.
        Then goes into the loop that writes messages to queues that will
        be pushed to firmware via the active serial channel.
    '''
    global com_handle
    global stop_sending
    global serial_activated

    transmit_attempts = 10
    
    # print 'waiting for serial selection'
    # while consumer_portname is None:
    #     time.sleep(1)
    #     print '.',
    # com_handle = serial.Serial(port = consumer_portname,baudrate = 19200)

    # print 'serial activated'
    
    #if fast queue is not empty then send messages in the fast queue
    #until queue is empty. The slow queue will only send messages
    #if the fast queue is not empty and stop_sending is not active.
    
    while True:
        print('+', end=' ')
        sys.stdout.flush()
        if not serial_activated:
            print('writer waiting for serial selection')

            #wait until consumer_portname is defined
            while consumer_portname is None:
                time.sleep(1)
                #print '.',
                sys.stdout.flush()
                
            com_handle = serial.Serial(port = consumer_portname,baudrate = 115200)
            # com_handle.write('pi\r')
            # com_handle.write('raspberry/r/n')
            # com_handle.write('cd /home')
            com_handle.write('ls\r')
            print(('connected to ',consumer_portname))
            sys.stdout.flush()

            #enable code below to manually enter commands
            # data = raw_input('enter a command:')
            # if data == 'exit':
            #     data = '\x03'
            # else:
            #     data = str(data) + '\r'
            # print data
            # com_handle.write(data)
            # time.sleep(2)

            serial_activated = True
            start_user_side_radio = True
        elif start_user_side_radio:
            #com_handle.write('ls\r')
            com_handle.write('cd /home/crawler_gui/GUI\r')
            com_handle.write('python3 user_side_radio_rfm9x.py\r')
            start_user_side_radio = False
            #com_handle.write('ls\r')
            #data = 'ls'

        #transmit messages to crawler
        while not fast_queue.empty() and not stop_sending and consumer_portname:
            #send commands and keep trying until timeout
            #if a command data has been updated send that instead and reset number of attemps
            tries = 0
            while tries <= transmit_attempts:
                if not fast_queue.empty():
                    
                    message_to_send = fast_queue.get()
                    print("TX: {} ENDTX".format(str(message_to_send)))
                    tries = 0
                #if no confirmation command processed send command again
                if not data_parser.last_executed_command == message_to_send:
                    com_handle.write(message_to_send)
                    print(('txd:',message_to_send))
                else:
                    print('successfully executed', message_to_send)
                    break
                tries += 1
                time.sleep(2)
            if tries >= transmit_attempts:
                print('TIMEDOUT, failed to execute:',message_to_send) 
                print('Expected confirmation command processed')
                
        time.sleep(0.5) 
        # while not slow_queue.empty() and fast_queue.empty() and not stop_sending and consumer_portname:
        #     message_to_send = slow_queue.get()
        #     #print "OutS: {}".format(message_to_send)
        #     com_handle.write(message_to_send)
        #     #put a little delay so firwmare receiver buffer does not overflow before
        #     #it can set stop_sending, not the delay must be long enough so the buffer
        #     #does not overflow, and short enough so firmware does not run out of data to consume
        #     time.sleep(0.01)


# def set_reader():
#     '''sets the active serial channel
    
#         this function will be called once when the GUI first initializes
#     '''
#     print 'waiting for serial selection'
#     global stop_sending

#     while True:
#         time.sleep(0.3)
#         print('*')
#         sys.stdout.flush()
#         if com_handle is None:
#             print('reader waiting for coms')
#             sys.stdout.flush()
#             while com_handle is None:
#                 time.sleep(1)
#                 #print '=',
#             print 'starting reader'
#         #time.sleep(0.3)
#         else:
#             #return 0
#             received = com_handle.read()
#             print received
#             print('&')
#             sys.stdout.flush()
#             if received == '1':
#                 #print 'stop it!'
#                 stop_sending = True
#             elif received == '2':
#                 #print 'send it'
#                 stop_sending = False
#             #print 'read {}'.format(received)

                        
def set_reader():
    '''sets the active serial channel
    
        this function will be called once when the GUI first initializes


        once radio_rfm9x.py is launched the expected output will be of syntax

            received: Awake:c=(0,0,0,44), r=0

            received: Awake:c=(0,0,0,44), r=0

            received: Awake:c=(0,0,0,44), r=0

            received: Awake:c=(0,0,0,44), r=0
    '''
    import data_parser

    print ('reader waiting for serial selection')
    global stop_sending
    global data_frame
    #global robot_data
    global logged_in_into_user_side_radio

    while com_handle is None:
        time.sleep(1)
        #print '=',
    print ('starting reader')
    #line = []
    while True:
        time.sleep(0.3)

        data = com_handle.read(com_handle.inWaiting())
        msg = data.decode('utf-8')
        if len(msg) > 0:

            print('rd:',msg)
            data_parser.interpret_data(msg.split('/r')[0])
            if 'Login incorrect' in msg or 'raspberrypi1 login:' in msg:
                time.sleep(1)
                com_handle.write('pi\r')
                time.sleep(0.5)
                com_handle.write('raspberry\r')
                logged_in_into_user_side_radio = True

            #convert "read: Awake:c=0, r=0" into "parsed: ['c', '0, r', '0']"
            # try:
            #     msg.strip('\r\n')
            #     data = [x.split('=')[1].strip('\r\n') for x in msg.split(':')[1].split(',')]
            #     print('parsed:',data)

            #     data_frame['encoder1'] = data[0]
            #     data_frame['incline'] = data[1]
            #     print('degree incline:',data_frame['incline'])
            #     print('encoder :',data_frame['encoder1'])
            # except Exception:
            #     print('failed to parse')
            #     print(str(Exception))
    
if __name__ == "__main__":
    #print show_serial_ports()

    print('available ports',list_serial_ports())
    #transmit('hello world')
    #start communication for reading and writing

    consumer_portname ='COM9'

    comthreadWriter = threading.Thread(target = set_writer)
    comthreadWriter.daemon = True #terminate thread when program ends
    comthreadWriter.start()

    comthreadReader = threading.Thread(target = set_reader)
    comthreadReader.daemon = True #terminate when program ends
    comthreadReader.start()

    while True:
        time.sleep(3)
        #print '#',
    
    print ('end of testing')
    eval(input('press enter to exit'))