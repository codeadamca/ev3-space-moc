#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait
# from pybricks.robotics import DriveBase
# from pybricks.media.ev3dev import SoundFile, ImageFile

import struct, sys

import threading


'''
Define custom functions
'''


# A helper function for converting stick values (0 to 255) to more usable
# numbers (-100 to 100)
def scale(val, src, dst):

    result = (float(val - src[0]) / (src[1] - src[0]))
    result = result * (dst[1] - dst[0]) + dst[0]
    return result


def saySomething(say, voice=False):

    global ev3

    if isinstance(voice, int):

        setVoice(voice)

    ev3.speaker.say(say)
    # threading.Thread(target=saySomethingThread, args=(say,)).start()


'''
def saySomethingThread(say):

    global ev3

    ev3.speaker.say(say)
'''


def setVoice(id):

    global ev3

    if id == 1:
        ev3.speaker.set_speech_options(None, 'f5', 180, 500)
    elif id == 2:
        ev3.speaker.set_speech_options(None, 'm7', 180, 100)


'''
def flashLights(sequence):

    threading.Thread(target=flashLightsThread, args=(sequence,)).start()


def flashLightsThread(sequence):

    global ev3

    for element in sequence:

        if element == "R":
            ev3.light.on(Color.RED)
        elif element == "O":
            ev3.light.on(Color.ORANGE)
        elif element == "Y":
            ev3.light.on(Color.YELLOW)
        elif element == "G":
            ev3.light.on(Color.GREEN)
        else:
            ev3.light.off()

        wait(1000)

    ev3.light.off()

    return True
'''


'''
Define array to store PS4 button statuses
'''


buttons = {}
# buttons["x"] = False
# buttons["square"] = False
# buttons["triangle"] = False
# buttons["circle"] = False

buttons["up"] = False
buttons["down"] = False
# buttons["left"] = False
# buttons["right"] = False

buttons["ps"] = False


'''
Initialize EV3 brick
'''


ev3 = EV3Brick()

# Initialize light
ev3.light.off()

# Initialize speaker
ev3.speaker.set_volume(100)
ev3.speaker.beep()

# Initialize motors
motorA = Motor(Port.A)
motorB = Motor(Port.B)

# Initialize sensors
touchSensor1 = TouchSensor(Port.S1)
colortouchSensor2 = ColorSensor(Port.S2)

# This color sensor is being used as a light
# ambient() is Blue
# reflection() is Red
# rgb() and color() uses all three lights
colortouchSensor2.color()


'''
Base initialization
'''


# Set up the garage
ev3.light.on(Color.RED)

while touchSensor1.pressed() is False:

    motorA.dc(-20)
    motorB.dc(-20)

motorA.dc(0)
motorB.dc(0)

motorA.reset_angle(0)
motorB.reset_angle(0)

setVoice(1)
# ev3.speaker.say("Garage initilized")
saySomething("Garage initilized")

ev3.light.off()

'''
Define threaded function to react to PS4 controller events
'''


def eventLoop():

    # Set global variables
    global buttons

    # Initialize PS4 controller

    # Locate the event file you want to react to, on my setup the PS4
    # controller button events are located in /dev/input/event4
    infile_path = "/dev/input/event4"
    in_file = open(infile_path, "rb")

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

            # print("BUTTON")

            # If the PS button is pressed
            if code == 316 and value == 1:
                buttons["ps"] = True
            elif code == 316 and value == 0:
                buttons["ps"] = False

        # If a directional button was pressed
        elif ev_type == 3:

            # print("DIRECTION")

            # If the down button was pressed
            if code == 17 and value == -1:
                buttons["up"] = True
            elif code == 17 and value == 1:
                buttons["down"] = True
            elif code == 17 and value == 0:
                buttons["down"] = False
                buttons["up"] = False

        # Read the next event
        event = in_file.read(EVENT_SIZE)


'''
Initialize threads
'''


threading.Thread(target=eventLoop).start()


'''
Create main loop
'''


while True:

    # print(buttons)

    # Move garage based on up and down button
    if buttons["up"] is True and motorA.angle() < 500:

        ev3.light.on(Color.GREEN)

        motorA.dc(20)
        motorB.dc(20)

    elif buttons["up"] is True and motorA.angle() > 500:

        ev3.light.on(Color.RED)

        motorA.dc(0)
        motorB.dc(0)

        saySomething("Garage opened", 1)

    elif buttons["down"] is True and motorA.angle() > 0:

        ev3.light.on(Color.GREEN)

        motorA.dc(-20)
        motorB.dc(-20)

    elif buttons["down"] is True and motorA.angle() < 0:

        ev3.light.on(Color.RED)

        motorA.dc(0)
        motorB.dc(0)

        saySomething("Garage closed", 1)

    else:

        motorA.dc(0)
        motorB.dc(0)

    # Stop script when PS button is pressed
    if buttons["ps"] is True:

        # Closing sequence
        ev3.light.on(Color.RED)

        saySomething("Program complete", 2)

        ev3.light.off()

        # Kill script
        break

    if all(value is False for value in buttons.values()):

        ev3.light.off()

    # Wait to prevent script from running too fast
    wait(50)
