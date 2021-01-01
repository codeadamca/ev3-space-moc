#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxClient, TextMailbox

import threading
from random import random

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
        ev3.speaker.set_speech_options(None, 'f5', 250, 500)
    elif id == 2:
        ev3.speaker.set_speech_options(None, 'm1', 250, 100)
    elif id == 3:
        ev3.speaker.set_speech_options(None, 'whisper', 250, 100)


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

buttons["leftHorizontal"] = 128
buttons["leftVertical"] = 128
buttons["rightHorizontal"] = 128
buttons["rightVertical"] = 128

buttons["ps"] = False


'''
Initialize EV3 brick
'''


# Initialize the EV3 Brick
ev3 = EV3Brick()

# Initialize speaker
ev3.speaker.set_volume(100)
ev3.speaker.beep()

# Trun off lights
ev3.light.off()

# The server must be started before the client!
saySomething('Waiting for server', 2)

client = BluetoothMailboxClient()
client.connect('mike')

client1 = TextMailbox('client1', client)

# Initialize EV3 touch sensor and motors
motorA = Motor(Port.A)


''' 
Define threaded function to save button value updates
'''


# Initialize a loop that waits for instructions from the server
def eventLoop(): 
        
    while True:

        client1.wait()
        newMessage = client1.read()

        newMessage = newMessage.split(':')

        if newMessage[1] == 'True':
            newMessage[1] = True
        elif newMessage[1] == 'False':
            newMessage[1] = False
        else:
            newMessage[1] = int(newMessage[1])

        buttons[newMessage[0]] = newMessage[1]


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
        motorA.dc(100)

    elif buttons["down"] and lightStatus == True:

        lightStatus = False
        motorA.dc(0)

    # Stop script when PS button is pressed
    if buttons["ps"] is True:

        wait(2000)

        # Closing sequence
        ev3.light.on(Color.RED)

        saySomething("Client one shut down", 2)

        ev3.light.off()

        # Kill script
        break

    # Wait to prevent script from running too fast
    wait(50)


# Use the speech tool to signify the program has finished
# saySomething("Program complete", 2)
