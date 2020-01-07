"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/01/2019

@details         This script is meant for use on crawler side radio
                Long Range Communication via LoRa rfm9x chips
                includes serial thread
"""
# Import Python System Libraries
import time, datetime, random, string, threading
import queue

# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x

import Communications_crawler_side

#anything that gets put into this queue will be sent
transmit_queue = queue.Queue()
#data received
receive_queue = queue.Queue()

# Configure LoRa Radio
CS = DigitalInOut(board.CE1)
RESET = DigitalInOut(board.D25)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
rfm9x.tx_power = 23

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def startLongRangeTransceiver():
    '''transmit and receive'''
    # Button A
    btnA = DigitalInOut(board.D5)
    btnA.direction = Direction.INPUT
    btnA.pull = Pull.UP

    # Button B
    btnB = DigitalInOut(board.D6)
    btnB.direction = Direction.INPUT
    btnB.pull = Pull.UP

    # Button C
    btnC = DigitalInOut(board.D12)
    btnC.direction = Direction.INPUT
    btnC.pull = Pull.UP

    # Create the I2C interface.
    i2c = busio.I2C(board.SCL, board.SDA)

    # 128x32 OLED Display
    display = adafruit_ssd1306.SSD1306_I2C(128, 32, i2c, addr=0x3c)
    # Clear the display.
    display.fill(0)
    display.show()
    width = display.width
    height = display.height


    prev_packet = None

    enable_transmission_test = False
    enable_transmitting_crawler_data = True
    crawler_side_radio_fw_version = 'A0.4'
    print('Crawler LoRa '+crawler_side_radio_fw_version)
    while True:
        packet = None
        # draw a box to clear the image
        display.fill(0)
        display.text(crawler_side_radio_fw_version, 0, 0, 1)

        # check for packet rx
        packet = rfm9x.receive()
        if packet is None:
            
            display.show()
            if enable_transmission_test:
                display.text('-Nothing Received-', 15, 10, 1)
            else:
                pass
                #display.text('- Waiting for PKT -', 15, 20, 1)
        else:
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
            try:
                print('received:',str(packet),'\n')
                packet_text = str(prev_packet, "utf-8")
                Communications_crawler_side.transmit_to_crawler(packet_text)

            except Exception as e:
                packet_text = 'failed to decode'+str(e)
                print('error detected:' ,e,)

            # display.text(packet_text, 0, 0, 1)
            # display.show()


        if not btnA.value:
            #toggle transmission
            enable_transmitting_crawler_data = False if enable_transmitting_crawler_data else True
            # Send Button A
            display.fill(0)
            #button_a_data = bytes(msg,"utf-8")
            display.text('toggled', 0, 10, 1)
            display.text('', 0, 20, 1)
        elif not btnB.value:
            # Send Button B
            enable_transmission_test = True
            display.fill(0)
            #send random string value
            string_data = randomString(10)
            msg = "Btn B!{}\r\n".format(string_data)
            #button_b_data = bytes(msg,"utf-8")
            transmit_queue.put(msg)
            display.text(msg, 0, 15, 1)
        elif not btnC.value:
            enable_transmission_test = False
            # Send Button C
            display.fill(0)
            button_c_data = bytes("Button C!\r\n","utf-8")
            #rfm9x.send(button_c_data)
            display.text('Stopped Test', 25, 20, 1)
        elif enable_transmission_test:
            string_data = randomString(10)
            msg = "{}".format(string_data)
            transmit_queue.put(msg)
            display.text(msg, 0, 20, 1)
        if not transmit_queue.empty():
            message_to_send = transmit_queue.get()
            #print('dequeued:{}'.format(message_to_send))
            rfm9x.send(bytes(message_to_send,"utf-8"))

        # if enable_transmitting_crawler_data and (Communications_crawler_side.data_frame['raw_data_from_fpga'] != 'no new data'):
        #     #in case raw_data_from_fpga receives two status in one string, example: 'Awake:c=(0,0,0,0), r=-6/rAwake:c=(0,0,0,0), r=-4/r'
        #     #we split on the /r and use the last status for transmission
        #     from_fpga =  Communications_crawler_side.data_frame['raw_data_from_fpga'].split('Awake:')[-1]
        #     from_fpga = from_fpga.split('\r')[0]
        #     print('from fpga',from_fpga)
        #     Communications_crawler_side.data_frame['raw_data_from_fpga'] = 'no new data'
        #     from_fpga = from_fpga[:-2]+'$'+Communications_crawler_side.data_frame['processed command']#append last command processed
        #     data = bytes(str(from_fpga),"utf-8")
        #     if not len(data) >252:
        #         rfm9x.send(data)
            # msg = "{}".format(from_fpga)
            # #where text(string,x,y,column)
            # display.text(msg[:15], 0, 10, 1)
            # display.text(msg[15:], 0, 20,1)

        display.show()

        time.sleep(0.1)

# def send_raw_data_from_fpga():
#     '''
#     run this in its own thread

#     send raw data from fpga using radio to user side radio
#     '''
#     global rfm9x
#     print("starting radio_send")

#     while True:
#         if (Communications_crawler_side.data_frame['raw_data_from_fpga'] != 'no new data'):
#             #in case raw_data_from_fpga receives two status in one string, example: 'Awake:c=(0,0,0,0), r=-6/rAwake:c=(0,0,0,0), r=-4/r'
#             #we split on the /r and use the last status for transmission
#             from_fpga =  Communications_crawler_side.data_frame['raw_data_from_fpga'].split('Awake:')[-1]
#             print('from fpga',from_fpga)
#             Communications_crawler_side.data_frame['raw_data_from_fpga'] = 'no new data'
#             from_fpga = from_fpga[:-2]+'$'+Communications_crawler_side.data_frame['processed command']#append last command processed
#             rfm9x.send(bytes(str(from_fpga),"utf-8"))
#         time.sleep(1)

if __name__ == '__main__':
    #Communications.consumer_portname =  Communications.show_serial_ports()[0]
    Communications_crawler_side.consumer_portname =  r'/dev/serial0'

    #serial thread for reading
    serial_thread_read = threading.Thread(target = Communications_crawler_side.set_reader)
    serial_thread_read.daemon = True #terminate when program ends
    print("starting serial read thread")
    serial_thread_read.start()

    #serial thread for writing
    serial_thread_write = threading.Thread(target = Communications_crawler_side.set_writer)
    serial_thread_write.daemon = True #terminate when program ends
    print("starting serial write thread")
    serial_thread_write.start()

    #serial thread for writing
    thread_keep_alive = threading.Thread(target = Communications_crawler_side.keep_alive)
    thread_keep_alive.daemon = True #terminate when program ends
    print("starting keep alive thread")
    thread_keep_alive.start()

    # # thread for transmitting data using lora
    # radio_send = threading.Thread(target = send_raw_data_from_fpga)
    # radio_send.daemon = True #terminate when program ends
    # radio_send.start()

    startLongRangeTransceiver()