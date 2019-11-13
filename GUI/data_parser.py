'''
Created on Nov. 12, 2019

@author: Mike

@brief    parse data strings and return a dictionary of robot values
'''
data_frame = None

def check_valid(data):
    '''
    just a simple valid check for now
    '''
    if 'Awake:' in data:
        return True

def interpret_data(data = None):
    '''
    where raw data = 'Awake:c=(0,0,0,44), r=0'
    '''
    global data_frame
    print 'interpreting', data
    if check_valid(data):
        #char stripping
        for ch in ['(',')',]:
            data = data.replace(ch, '')

        data = data.split(', ')
        data =[ x.split('=')[1] for x in data]

        #convert into format: [['0', '0', '0', '44', ''], ['0']]
        data =[ x.split(',') for x in data]

        data_frame = {
                        'encoder1': data[0][0],
                        'encoder2':  data[0][1],
                        'encoder3':  data[0][2],
                        'encoder4':  data[0][3],
                        'roll':  data[1][0],
                        'pitch':  data[1][0],
                    }

        for key in data_frame:
            data_frame[key] = int(data_frame[key])

         
    return data
if __name__ == "__main__":
    print interpret_data('Awake:c=(0,0,0,44), r=0')
    print data_frame

    print interpret_data('Awake:c=(0,0,0,44), r=-10')
    print data_frame
