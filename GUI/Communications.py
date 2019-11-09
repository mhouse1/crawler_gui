'''
Created on Aug 9, 2014

@author: Mike

@brief    contains serial communication functionality
            Supported features: ability to list serial ports available, set active serial port,
                                buffer messages to be sent into a queue and send using a parallel process
'''
import os, sys, glob

import serial
from serial.tools import list_ports
import time
import multiprocessing

#linux
import queue as Queue

import threading
#import Queue #python2

#active_serial = None
serial_activated = False
consumer_portname = None
com_handle = None
fast_queue = Queue.Queue()
slow_queue = Queue.Queue()

data_frame = {#'incline':3, 'encoder1':3,
              'raw_data_from_fpga':'empty'
              }
stop_sending = False


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
    default_file_name = 'bytestream'
    default_file_ext = '.txt'
    default_file_index = 0
    file_name = default_file_name+str(default_file_index)+default_file_ext
#     while os.path.isfile(file_name):
#         default_file_index += 1
#         file_name = default_file_name+str(default_file_index)+default_file_ext
    with open(file_name, "a") as myfile:
        for char in message:
            myfile.write(str(ord(char))+' ')
            #myfile.write(char)
        #myfile.write(message[:-1])
    
    if transmit_speed == 0:
        #print 'putFast',message
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
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    print('checking ports:')
    limit = 20
    count = 0
    for port in ports:
        count += 1
        #typically we'd find what we're looking for within 20 loops
        #any more is just probably wasting time
        if count == limit:
            return result
        try:
            #print('.', end='')
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
          
    return result

def list_serial_ports():
    return show_serial_ports()
##def list_serial_ports():
##    '''
##    deprecated, use show_serial_ports() instead
##    '''
##    # Windows
##    if os.name == 'nt':
##        #return []
##        # Scan for available ports.
##        available = []
##        for i in range(256):
##            try:
##                s = serial.Serial(i)
##                
##                available.append('COM'+str(i + 1))
##                s.close()
##            except serial.SerialException:
##                pass
##        return available
##    else:
##        # Mac / Linux
##        return [port[0] for port in list_ports.comports()]
##        #['/dev/cu.Michael-SerialServer-1', '/dev/cu.MikeHousesiPod-Wireless', '/dev/cu.Bluetooth-Modem', '/dev/cu.Bluetooth-Incoming-Port', '/dev/cu.MikeHousesiPhone-Wirele']
##
##        #['/dev/cu.Michael-SerialServer-1', '/dev/cu.MikeHousesiPod-Wireless', '/dev/cu.Bluetooth-Modem', '/dev/cu.Bluetooth-Incoming-Port', '/dev/cu.MikeHousesiPhone-Wirele', '/dev/cu.SLAB_USBtoUART']

def set_writer(baud_rate = 115200, bytesize = 8, timeout = 1, ):
    '''
        this function will be called once when the GUI first initializes
        it then waits until the user sets an active serial chanel.
        Then goes into the loop that writes messages to queues that will
        be pushed to firmware via the active serial channel.
    '''
    global com_handle
    global stop_sending
    
    print ('waiting for serial selection')
    while consumer_portname is None:
        time.sleep(1)
        print ('.',)
    com_handle = serial.Serial(port = consumer_portname,baudrate = baud_rate)

    print ('serial activated')
    
    #if fast queue is not empty then send messages in the fast queue
    #until queue is empty. The slow queue will only send messages
    #if the fast queue is not empty and stop_sending is not active.
    
    while True:
        #print 'consumer active'
        while not fast_queue.empty():
            message_to_send = fast_queue.get()
            #print "OutF: {}".format(message_to_send)
            com_handle.write(message_to_send)
        time.sleep(0.5) 
        #print 'stopsend = {}'.format(stop_sending)
        while not slow_queue.empty() and fast_queue.empty() and not stop_sending:
            message_to_send = slow_queue.get()
            #print "OutS: {}".format(message_to_send)
            com_handle.write(message_to_send)
            #put a little delay so firwmare receiver buffer does not overflow before
            #it can set stop_sending, not the delay must be long enough so the buffer
            #does not overflow, and short enough so firmware does not run out of data to consume
            time.sleep(0.01)
            #set a delay for slow transfer queue
            #break out of delay early if detected fast_queue not empty
#             for i in xrange(2):
#                 if not fast_queue.empty():
#                     break
#                 time.sleep(0.1)#interval to check fast_queue is not empty
        #stop_sending = False
        

def set_reader():
    '''sets the active serial channel
    
        this function will be called once when the GUI first initializes
    '''
    print ('waiting for serial selection')
    global stop_sending
    global data_frame
    while com_handle is None:
        time.sleep(1)
        #print '=',
    print ('starting reader')
    line = []
    while True:
        time.sleep(0.3)
        # received = com_handle.readline()
        # if received == '1':
        #     print('stop it!')
        #     stop_sending = True
        # elif received == '2':
        #     #print 'send it'
        #     stop_sending = False
        # print('read {}'.format(received))
        data = com_handle.read(com_handle.inWaiting())
        msg = data.decode('utf-8')
        if len(msg) > 0:

            print('read:',msg)
            #convert "read: Awake:c=0, r=0" into "parsed: ['c', '0, r', '0']"
            try:
                data_frame['raw_data_from_fpga'] = msg
                # msg.strip('\r\n')
                # data = [x.split('=')[1].strip('\r\n') for x in msg.split(':')[1].split(',')]
                # print('parsed:',data)

                # data_frame['encoder1'] = data[0]
                # data_frame['incline'] = data[1]
                # print('degree incline:',data_frame['incline'])
                # print('encoder :',data_frame['encoder1'])
            except Exception:
                print('failed to parse')
                print(str(Exception))
                        

    
if __name__ == "__main__":
    #print (show_serial_ports())
    #transmit('hello world')
    consumer_portname =  r'/dev/serial0'

    #serial thread for reading
    serial_thread_read = threading.Thread(target = set_reader)
    serial_thread_read.daemon = True #terminate when program ends
    print("starting reader")
    serial_thread_read.start()

    #serial thread for writing
    serial_thread_write = threading.Thread(target = set_writer)
    serial_thread_write.daemon = True #terminate when program ends
    print("starting data writer")
    serial_thread_write.start()


    while True:
        time.sleep(1)
    