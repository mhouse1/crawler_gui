"""
@author          Michael House
@organisation    Terrafirma Technology, Inc.
@date            10/01/2019

@details         Long Range Communication via LoRa rfm9x chips
"""
# Import Python System Libraries
import time, datetime, random, string
import queue

# Import Blinka Libraries
import busio
from digitalio import DigitalInOut, Direction, Pull
import board
# Import the SSD1306 module.
import adafruit_ssd1306
# Import RFM9x
import adafruit_rfm9x

#anything that gets put into this queue will be sent
transmit_queue = queue.Queue()
#data received
receive_queue = queue.Queue()

data_frame = {'incline':3
    }
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
    
    print('starting Terrafirma Technology LoRa')
    while True:
        packet = None
        # draw a box to clear the image
        display.fill(0)
        display.text('Terrafirma Technology', 0, 0, 1)

        # check for packet rx
        packet = rfm9x.receive()
        if packet is None:
            
            display.show()
            if enable_transmission_test:
                display.text('-Nothing Received-', 15, 10, 1)
            else:
                display.text('- Waiting for PKT -', 15, 20, 1)
        else:
            # Display the packet text and rssi
            display.fill(0)
            prev_packet = packet
            try:
                print('received:',str(packet),'\n')
                packet_text = str(prev_packet, "utf-8")
                packet_text.split(',')
                data_frame['incline'] = int(packet_text[0])
                data_frame['encoder1'] = int(packet_text[1])
                print('received incline:',int(data_frame['incline']))
                print('received encoder:',int(data_frame['encoder1']))
            except Exception as e:
                packet_text = 'failed to decode'
                print('error detected:' ,e,)
                
            display.text('RX: ', 0, 0, 1)
            display.text(packet_text, 25, 0, 1)
            time.sleep(1)

        if not btnA.value:
            enable_transmission_test = True
            # Send Button A
            display.fill(0)
            #button_a_data = bytes(msg,"utf-8")
            display.text('Started', 0, 10, 1)
            display.text('Tranceiver Test', 0, 20, 1)
        elif not btnB.value:
            # Send Button B
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
            print('dequeued:{}'.format(message_to_send))
            rfm9x.send(bytes(message_to_send,"utf-8"))
            
        display.show()
        time.sleep(0.1)

if __name__ == '__main__':
    startLongRangeTransceiver()
