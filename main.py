#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

import struct, sys

import threading


# Define custom functions

# A helper function for converting stick values (0 to 255) to more usable
# numbers (-100 to 100)
def scale(val, src, dst):

    result = (float(val - src[0]) / (src[1] - src[0]))
    result = result * (dst[1] - dst[0]) + dst[0]
    return result


# Define array to store PS4 button status
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

# Initialize EV3 motors and sensors
motorA = Motor(Port.A)
motorB = Motor(Port.B)

touchSensor1 = TouchSensor(Port.S1)


# Set up the garage
while touchSensor1.pressed() is False:

    motorA.dc(-20)
    motorB.dc(-20)

motorA.dc(0)
motorB.dc(0)

motorA.reset_angle(0)
motorB.reset_angle(0)


# Define function to react to PS4 controller events
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


# Initialize threads
processA = threading.Thread(target=eventLoop)
processA.start()


# Create main loop
while True:

    # print(buttons)

    # React to up and down button
    if buttons["up"] is True and motorA.angle() < 500:

        motorA.dc(20)
        motorB.dc(20)

    elif buttons["down"] is True and motorA.angle() > 0:

        motorA.dc(-20)
        motorB.dc(-20)

    else:

        motorA.dc(0)
        motorB.dc(0)

    print("Angle: ", motorA.angle())

    # React to PS button being pressed
    if buttons["ps"] is True:

        break

    wait(50)
