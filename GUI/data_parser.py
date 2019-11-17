'''
Created on Nov. 12, 2019

@author: Mike

@brief    parse data strings and return a dictionary of robot values
'''
import traceback, sys
from collections import OrderedDict 
data_frame = None
last_executed_command = None

crawler_commands = OrderedDict()

def generate_crawler_comand(address, value):
    '''
    @usage
    given an command address and value, returns a string with updated command data ready to be transmited

    @details:
    data to crawler is sent as a string that includes all commands and values.
    This design reduces the number of individual commands sent, the advantage is,
    on the GUI side any time a single command is updated the data to be transmitted is immediately updated
    and replace whatever is already in the queue to be transmitted.
    '''
    crawler_commands[address] = value
    command_string = 'CMD:'#can replace this with a checksum in the future
    for key in crawler_commands:
        #print key, crawler_commands[key]
        value = crawler_commands[key]
        if not value== None:
            command_string+=','.join([str(key),str(value)])+'#'
    return command_string


def check_valid(data):
    '''
    just a simple valid check for now
    '''
    if 'Awake:' in data:
        if 'CMD:' in data:
            print 'need fix:',data,' END'
        return True
    

def interpret_data(raw_data = None):
    '''
    where raw data = 'Awake:c=(0,0,0,44), r=0'
    '''
    global data_frame
    print 'interpreting', raw_data
    data = raw_data
    copy_raw_data = raw_data
    backup_data = data_frame
    if 'Awake:' in raw_data:
        data=raw_data.split('Awake:')[1]
        data=raw_data.split('/r')[0]
        if 'CMD:' in data:
            return data
        try:
            #char stripping
            for ch in ['(',')',]:
                data = data.replace(ch, '')

            data = data.split(', ')
            data =[ x.split('=')[1] for x in data]

            #convert into format: [['0', '0', '0', '44', ''], ['0']]
            data =[ x.split(',') for x in data]

            #parse the received data from radio
            data_frame = {
                            'encoder1': data[0][0],
                            'encoder2':  data[0][1],
                            'encoder3':  data[0][2],
                            'encoder4':  data[0][3],
                            'roll':  data[1][0],
                            'pitch':  data[1][0],
                            
                        }
            
            #the last element in data received is always last_executed_command
            last_executed_command = data[-1][1]

            #convert data in data_frame into int format
            for key in data_frame:
                data_frame[key] = int(data_frame[key])

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            print 'ERROR EXCEPTION: ',str(e)
            print 'ERROR: failed to inpterpret received data:',copy_raw_data
            print 'data frame',data_frame
            data_frame = backup_data
         
    return data

def decode_crawler_command(message):
    '''
    given a string command decode into a list of address and values
    '''
    #decode into ['1,23', '2,2', '10,3']
    decoded =  [x for x in message.split(':')[1].split('#') if len(x) > 0]
    decoded = [x.split(',') for x in decoded]

    return decoded

if __name__ == "__main__":
    print interpret_data('Awake:c=(0,0,0,44), r=0')
    print data_frame

    print interpret_data('Awake:c=(0,0,0,44), r=-10')
    print data_frame

    print generate_crawler_comand(1,23)
    print generate_crawler_comand(2,2)
    print generate_crawler_comand(10,2)
    full_command =  generate_crawler_comand(10,3)
    #decode into ['1,23', '2,2', '10,3']
    parsed_data =  decode_crawler_command(full_command)
    print parsed_data[:-1]
