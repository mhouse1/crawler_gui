'''
Created on Sept 16, 2019

@author: Mike

@details    simulate acceleromter output
'''
import time, random

accelerometer_x = 0.0
accelerometer_y = 0.0
movement_forward = 0.0
movement_turn = 0.0
distance_traveled = 0
battery_level = 100



def limit_random_output(data):
    '''
    random data limited to +/- 10
    '''
    data = data + random.uniform(-0.3,0.3)
    if data < -10:
       data = -10
    elif data > 10:
        data = 10

    return data

def random_trend_upward(data, limit, increment):
    '''
    data will trend upward and limited to specified limit
    '''
    data = data + random.randint(0,increment)

    if data > limit:
        data = limit

    return data

def random_trend_downward(data, limit, increment):
    '''
    data will trend downward and limited to specified limit
    '''
    data = data + random.uniform(increment,0)

    if data < limit:
        data = limit

    return data

def simulate_data():
    import data_parser
    distance_traveled = 0
    while True:
        distance_traveled = random_trend_upward(distance_traveled,10000,1) + distance_traveled
        data_parser.interpret_data('Awake:c=({},0,0,44), r=0'.format(distance_traveled))
        time.sleep(2.2)


# def simulate_data():
#     global accelerometer_x
#     global accelerometer_y
#     global movement_forward
#     global movement_turn
#     global distance_traveled
#     global battery_level
    
#     while True:
        
# ##        accelerometer_x = accelerometer_x + random.uniform(-0.3,0.3)
# ##        accelerometer_y = accelerometer_y + random.uniform(-0.3,0.3)
# ##        movement_forward = movement_forward + random.uniform(-0.3,0.3)
# ##        movement_turn = movement_turn + random.uniform(-0.3,0.3)

#         accelerometer_x = limit_random_output(accelerometer_x)
#         accelerometer_y = limit_random_output(accelerometer_y)
#         movement_forward = limit_random_output(movement_forward)
#         movement_turn = limit_random_output(movement_turn)
#         distance_traveled = random_trend_upward(distance_traveled,10000,1)
#         battery_level = float("{0:0.2f}".format(random_trend_downward(battery_level,0.0,-0.3)))
        
        
# ##        if accelerometer_x < -10:
# ##           accelerometer_x = -10
# ##        elif accelerometer_x > 10:
# ##            accelerometer_x = 10
# ##
# ##        if accelerometer_y < -10:
# ##           accelerometer_y = -10
# ##        elif accelerometer_y > 10:
# ##            accelerometer_y = 10

        
#         time.sleep(0.8)

#         # if __name__ == '__main__':
#         #     print(accelerometer_x, accelerometer_y)


if __name__ == '__main__':
    simulate_data()

