#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.media.ev3dev import SoundFile
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxServer, TextMailbox

from pybricks.iodevices import DCMotor

import threading
import random

import struct, sys


'''
Define custom functions
'''


# A helper function for converting stick values (0 to 255) to more usable
# numbers (-100 to 100)
def scale(val, src, dst, decimals=0):

    result = (float(val - src[0]) / (src[1] - src[0]))
    result = result * (dst[1] - dst[0]) + dst[0]

    result = round(result,decimals)
    result = int(result)

    return result

# A function to initiate the ev3 say function
def saySomething(say, voice=False):

    global ev3

    if isinstance(voice, int):

        setVoice(voice)

    ev3.speaker.say(say)
    print('-------------------')
    print(say)

# A function to set the current voice settings
def setVoice(id):

    global ev3

    if id == 1:
        ev3.speaker.set_speech_options(None, 'f5', 250, 50)
    elif id == 2:
        ev3.speaker.set_speech_options(None, 'm1', 250, 0)
    elif id == 3:
        ev3.speaker.set_speech_options(None, 'm7', 250, 99)

# A function to broadcast button updates to all clients
def update(key, value):

    global buttons, client1, client2

    # print('Current Value: '+str(buttons[key]))
    # print('New Value: '+str(value))

    if buttons[key] != value:

        '''
        try:
            # client1.send(key + ':' + str(value))
            # client2.send(key + ':' + str(value))
        except:
            print('ERROR: Could not send client controller update')
        '''

        buttons[key] = value


'''
Define array to store PS4 button statuses
'''


# Define array to store all button values
buttons = {}
buttons["x"] = False
buttons["square"] = False
buttons["triangle"] = False
buttons["circle"] = False

buttons["up"] = False
buttons["down"] = False
buttons["left"] = False
buttons["right"] = False

buttons["r1"] = False
buttons["r2"] = False
buttons["l1"] = False
buttons["l2"] = False

buttons["leftHorizontal"] = 0
buttons["leftVertical"] = 0
buttons["rightHorizontal"] = 0
buttons["rightVertical"] = 0

buttons["ps"] = False


'''
Initialize EV3 brick
'''


# Initialize the EV3 Brick
ev3 = EV3Brick()

# Initialize speaker
ev3.speaker.set_volume(50)
ev3.speaker.beep()

# Trun off lights
ev3.light.off()

# The server must be started before the client!
# saySomething('Waiting for clients', 3)

# Define phrase to speak
# sample = "The five boxing wizards jump quickly"

# Set other options
wordsPerMinute = 180
voicePitch = 50

# server = BluetoothMailboxServer()
# server.wait_for_connection(2)

# client1 = TextMailbox('client1', server)
# client2 = TextMailbox('client2', server)

# saySomething('Clients found', 3)

# Initialize motors
motorA = Motor(Port.A)
# motorB = Motor(Port.B)
motorC = DCMotor(Port.C)
motorD = DCMotor(Port.D)

motorA.dc(0)
# motorB.dc(0)
motorC.dc(0)
motorD.dc(0)

# Initialize sensors
# touchSensor1 = TouchSensor(Port.S1)
# colortouchSensor2 = ColorSensor(Port.S2)

# This color sensor is being used as a light
# ambient() is Blue
# reflection() is Red
# rgb() and color() uses all three lights
# colortouchSensor2.color()

# motorA.reset_angle(0)
# motorB.reset_angle(0)

# setVoice(1)
# ev3.speaker.say("Garage initilized")
# saySomething("Garage initilized")


'''
Define threaded function to react to PS4 controller events
'''


# Locate the event file you want to react to, on my setup the PS4
# controller button events are located in /dev/input/event4
infile_path = "/dev/input/event4"

while True:

    try: 

        in_file = open(infile_path, "rb")
        saySomething('Controller found', 3)
        break

    except:

        saySomething('Controller missing', 3)
        wait(5000)
        
def eventLoop():

    # Set global variables
    global buttons, infile_path, client1, client2

    # Initialize PS4 controller
    # Define the format the event data will be read
    # https://docs.python.org/3/library/struct.html#format-characters
    FORMAT = 'llHHi'
    EVENT_SIZE = struct.calcsize(FORMAT)
    event = in_file.read(EVENT_SIZE)

    # Create a loop to react to events
    while event:

        # Place event data into variables
        (tv_sec, tv_usec, ev_type, code, value) = struct.unpack(FORMAT, event)

        # If a button was pressed or released
        if ev_type == 1:

            # If the L1 button is psressed
            if code == 310 and value == 1:
                update('l1', True)
                
            elif code == 310 and value == 0:
                update('l1', False)

            # If the L2 button is pressed
            if code == 312 and value == 1:
                update('l2', True)
            elif code == 312 and value == 0:
                update('l2',  False)

            # If the r1 button is pressed
            if code == 311 and value == 1:
                update('r1',  True)
            elif code == 311 and value == 0:
                update('r1', False)

            # If the r2 button is pressed
            if code == 313 and value == 1:
                update('r2', True)
            elif code == 313 and value == 0:
                update('r2', False)

            # If the PS button is pressed
            if code == 316 and value == 1:
                update('ps',  True)
            elif code == 316 and value == 0:
                update('ps', False)

            # React to the X button
            if code == 304 and value == 0:
                update('x', False)
            elif code == 304 and value == 1:
                update('x', True)

            # React to the Circle button
            elif code == 305 and value == 0:
                update('circle', False)
            elif code == 305 and value == 1:
                update('circle', True)

            # React to the Triangle button
            elif code == 307 and value == 0:
                update('triangle', False)
            elif code == 307 and value == 1:
                update('triangle', True)

            # React to the Square button
            elif code == 308 and value == 0:
                update('square', False)
            elif code == 308 and value == 1:
                update('square', True)

        # If a directional button was pressed
        elif ev_type == 3:

            # Four axis values
            if code <= 5:

                value = scale(value, (0, 255), (-25, 25)) * 4

                if code == 0:
                    update('leftHorizontal', value)
                elif code == 1:
                    update('leftVertical', value)
                elif code == 3:
                    update('rightHorizontal', value)
                elif code == 4:
                    update('rightVertical', value)

            # If the up/down button was pressed
            if code == 17 and value == -1:
                update('up', True)
                update('down', False)
            elif code == 17 and value == 1:
                update('up', False)
                update('down', True)
            elif code == 17 and value == 0:
                update('up', False)
                update('down', False)

            # If the left/roght button was pressed
            if code == 16 and value == -1:
                update('left', True)
                update('right', False)
            elif code == 16 and value == 1:
                update('left', False)
                update('right', True)
            elif code == 16 and value == 0:
                update('left', False)
                update('right', False)

        # Read the next event
        event = in_file.read(EVENT_SIZE)


'''
Initialize threads
'''


# Run the P#4 event loop as a thread
threading.Thread(target=eventLoop).start()


'''
Set base variables
'''


lightStatus = False
flickerStatus = False


'''
Create main loop
'''


while True:

    # Turn light on
    if buttons["up"] and lightStatus == False:

        lightStatus = True
        motorC.dc(100)
        
        ev3.speaker.play_file(SoundFile.CONFIRM)
        
        
    elif buttons["down"] and lightStatus == True:

        lightStatus = False
        motorC.dc(0)

        ev3.speaker.play_file(SoundFile.GENERAL_ALERT)

    # Turn flickering light on
    if buttons["right"] and flickerStatus == False:

        flickerStatus = True

        ev3.speaker.play_file(SoundFile.CONFIRM)

    elif buttons["left"] and flickerStatus == True:

        flickerStatus = False
        motorD.dc(0)

        ev3.speaker.play_file(SoundFile.GENERAL_ALERT)

    if flickerStatus == True:

        motorD.dc(round(40 + random.random() * 30, 0))

    # Garage door
    if buttons["r1"]:

        motorA.dc(30)
        # motorB.dc(60)

        ev3.speaker.play_file(SoundFile.AIRBRAKE)
        
    elif buttons["r2"]:

        motorA.dc(-30)
        # motorB.dc(-40)

        ev3.speaker.play_file(SoundFile.AIR_RELEASE)
        
    else:

        motorA.dc(0)
        # motorB.dc(0)

    # Stop script when PS button is pressed
    if buttons["ps"] is True:

        wait(1000)

        # Closing sequence
        ev3.light.on(Color.RED)

        saySomething("Server shut down", 3)

        ev3.light.off()

        # Kill script
        break

    # Wait to prevent script from running too fast
    wait(50)
