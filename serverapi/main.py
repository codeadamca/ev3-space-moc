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

import urequests as requests
import json


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


'''
Manage Audio
'''

audioQueue = []
audioCount = 0

def manageAudio():

    global audioQueue, audioCount

    while True:

        if audioCount < len(audioQueue):

            if audioQueue[audioCount][0] == "say":

                saySomething(audioQueue[audioCount][1])

            elif audioQueue[audioCount][0] == "play":

                ev3.speaker.play_file(audioQueue[audioCount][1])

            # print(audioQueue)
            # print(len(audioQueue))
            # print(audioQueue[audioCount])

            audioCount += 1

        wait(1000)

# Run the P#4 event loop as a thread
threading.Thread(target=manageAudio).start()

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
Set base variables
'''


flickerStatus = False
steadyStatus = False
cloningStatus = False


'''
Create main loop
'''

counter = 0

while True:
    
    if counter > 100:

        res = requests.get(url='http://base.codeadam.ca/current.php')
        settings = json.loads(res.text)

        # Flicker lights
        if settings["flicker"] == "On" and flickerStatus == False:

            flickerStatus = True
            # ev3.speaker.play_file(SoundFile.CONFIRM)
            audioQueue.append(["play",SoundFile.CONFIRM])

        elif settings["flicker"] == "Off" and flickerStatus == True:

            flickerStatus = False
            # ev3.speaker.play_file(SoundFile.GENERAL_ALERT)
            audioQueue.append(["play",SoundFile.GENERAL_ALERT])

        # Steady lights
        if settings["steady"] == "On" and steadyStatus == False:

            steadyStatus = True
            # ev3.speaker.play_file(SoundFile.CONFIRM)
            audioQueue.append(["play",SoundFile.CONFIRM])
            motorC.dc(50)

        elif settings["steady"] == "Off" and steadyStatus == True:

            steadyStatus = False
            # ev3.speaker.play_file(SoundFile.GENERAL_ALERT)
            audioQueue.append(["play",SoundFile.GENERAL_ALERT])
            motorC.dc(0)

        # Cloning
        # Steady lights
        if settings["cloning"] == "On" and cloningStatus == False:

            cloningStatus = True
            motorA.dc(30)

        elif settings["cloning"] == "Off" and cloningStatus == True:

            cloningStatus = False
            motorA.dc(0)


        counter = 0

    counter += 1

    if flickerStatus == True:

        motorD.dc(round(40 + random.random() * 30, 0))

    else:

        motorD.dc(0)

    if cloningStatus == True and audioCount == len(audioQueue):

        # ev3.speaker.play_file(SoundFile.AIRBRAKE)
        # audioQueue.append(["play",SoundFile.AIRBRAKE])
        audioQueue.append(["say","Cloning"])



    # Wait to prevent script from running too fast
    wait(100)
