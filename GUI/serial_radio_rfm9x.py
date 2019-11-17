"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/01/2019

@details         Long Range Communication via LoRa rfm9x chips
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

    # Configure LoRa Radio
    CS = DigitalInOut(board.CE1)
    RESET = DigitalInOut(board.D25)
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, 915.0)
    rfm9x.tx_power = 23
    prev_packet = None

    enable_transmission_test = False
    enable_transmitting_crawler_data = True
    
    print('starting Terrafirma Technology LoRa')
    while True:
        packet = None
        # draw a box to clear the image
        display.fill(0)
        display.text('v0.2', 0, 0, 1)

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
            except Exception as e:
                packet_text = 'failed to decode'+str(e)
                print('error detected:' ,e,)

            Communications_crawler_side.transmit_to_crawler(packet_text)
            display.text(packet_text, 0, 0, 1)
            display.show()


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

        if enable_transmitting_crawler_data:
            from_fpga =  Communications_crawler_side.data_frame['raw_data_from_fpga']
            Communications_crawler_side.data_frame['raw_data_from_fpga'] = 'no new data'
            rfm9x.send(bytes(str(from_fpga),"utf-8"))
            msg = "{}".format(from_fpga)
            #where text(string,x,y,column)
            display.text(msg[:15], 0, 10, 1)
            display.text(msg[15:], 0, 20,1)

        display.show()

        time.sleep(0.1)

if __name__ == '__main__':
    #Communications.consumer_portname =  Communications.show_serial_ports()[0]
    Communications_crawler_side.consumer_portname =  r'/dev/serial0'

    #serial thread for reading
    serial_thread_read = threading.Thread(target = Communications_crawler_side.set_reader)
    serial_thread_read.daemon = True #terminate when program ends
    print("starting data simulation")
    serial_thread_read.start()

    #serial thread for writing
    serial_thread_write = threading.Thread(target = Communications_crawler_side.set_writer)
    serial_thread_write.daemon = True #terminate when program ends
    print("starting data simulation")
    serial_thread_write.start()


    startLongRangeTransceiver()