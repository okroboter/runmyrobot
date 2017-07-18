import os
import time
import subprocess
import argparse
import requests
from multiprocessing import Process

import zmq

parser = argparse.ArgumentParser(description='Overlay controls')
parser.add_argument('--wifi', dest='wifi')
parser.set_defaults(wifi=None)
parser.add_argument('--lights', dest='lights', action="store_true")
parser.set_defaults(lights=False)

commandArgs = parser.parse_args()

wifiLevels = [-90, -80, -70, -60, 0]
wifiOverlays = [14, 15, 16, 17, 18]
lightOverlays = [19, 20, 21, 22, 23, 24]
currentWifiLevel = 0
currentColorLevel = -1

proximityOverlay = 25
proximityAlert = False

bindAddress = "tcp://localhost:5555"

def clearSignals(requester):

    for level in wifiOverlays:
        requester.send("Parsed_overlay_%d enable 0" % level)
        message = requester.recv()
        print 'Received reply:[%s]' % message

def clearLights(requester):

    for level in lightOverlays:
        requester.send("Parsed_overlay_%d enable 0" % level)
        message = requester.recv()
        print 'Received reply:[%s]' % message

def processSignals():

    global currentWifiLevel
    global currentColorLevel
    global proximityAlert

    context = zmq.Context()
    requester = context.socket(zmq.REQ)
    requester.connect(bindAddress)

    while True:

        # Look for restart file
        videoRestarted = False
        if os.path.isfile("/dev/shm/videorestart.txt"):
            videoRestarted = True
            os.remove("/dev/shm/videorestart.txt");

        if not proximityAlert and os.path.isfile("/dev/shm/proximityalert.txt"):
            proximityAlert = True
            requester.send("Parsed_overlay_%d enable 1" % proximityOverlay)
            message = requester.recv()
            print 'Received reply:[%s]' % message
        elif proximityAlert and not os.path.isfile("/dev/shm/proximityalert.txt"):
            proximityAlert = False

        if commandArgs.lights and os.path.isfile("/dev/shm/lights.txt"):

            # Read the color from a file
            color = 0
            with open("/dev/shm/lights.txt", "r") as f:
                try:
                    color = int(f.read(1))
                except Exception, err:
                    print "Exception reading file: %s" % err
                    color = 0

            if color <= 5 and (color != currentColorLevel or videoRestarted):

                clearLights(requester)
                currentColorLevel = color
                requester.send("Parsed_overlay_%d enable 1" % lightOverlays[color])
                message = requester.recv()
                print 'Received reply:[%s]' % message


        if commandArgs.wifi is not None:

            wifiStrength, _ = subprocess.Popen('/sbin/iwconfig %s | grep Signal|cut -d"=" -f3|cut -d" " -f1' % commandArgs.wifi,
                shell=True,
                stdout=subprocess.PIPE).communicate()

            if wifiStrength.strip() == "100/100":
                wifiStrength = 100
            else:
                try:
                    wifiStrength = int(wifiStrength)
                    print wifiStrength
                except Exception, err:
                    print "Exception %s" % err
                    wifiStrength = 100

            print "Current Level: %d\n" % currentWifiLevel

            for level, dbStrength in enumerate(wifiLevels):
                if wifiStrength <= dbStrength and (currentWifiLevel != level or videoRestarted):
                    clearSignals(requester)
                    currentWifiLevel = level
                    print "New Level: %d\n" % currentWifiLevel
                    requester.send("Parsed_overlay_%d enable 1" % wifiOverlays[level])
                    message = requester.recv()
                    print 'Received reply:[%s]' % message
                    # copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")
                    break
                elif dbStrength == 0 and (currentWifiLevel != len(wifiLevels) - 1 or videoRestarted):
                    clearSignals(requester)
                    currentWifiLevel = level
                    print "New Max Level: %d\n" % currentWifiLevel
                    requester.send("Parsed_overlay_%d enable 1" % wifiOverlays[len(wifiOverlays)-1])
                    message = requester.recv()
                    print 'Received reply:[%s]' % message
                    # copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")

            print "Wifi level: %d dBm" % wifiStrength

        time.sleep(2)

process = Process(target=processSignals)
process.start()


