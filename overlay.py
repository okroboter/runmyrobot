import time
import subprocess
import argparse
import requests
from multiprocessing import Process

import zmq

parser = argparse.ArgumentParser(description='Overlay controls')
parser.add_argument('--wifi', dest='wifi')
parser.set_defaults(wifi=None)

commandArgs = parser.parse_args()

wifiLevels = [-90, -80, -70, -50, 0]
wifiOverlays = [8, 9, 10, 11, 12]
currentWifiLevel = 0

bindAddress = "tcp://localhost:5555"

context = zmq.Context()
requester = context.socket(zmq.REQ)
requester.connect(bindAddress)

def clearSignals():

    for level in wifiOverlays:
        requester.send("Parsed_overlay_%d enable 0" % wifiOverlays[level])

def processSignals():

    global currentWifiLevel

    while True:

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
                    wifiStrength = -100

            for level, dbStrength in enumerate(wifiLevels):
                if wifiStrength <= dbStrength and currentWifiLevel != level:
                    clearSignals()
                    currentWifiLevel = level
                    requester.send("Parsed_overlay_%d enable 1" % wifiOverlays[level])
                    # copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")
                    break
                elif dbStrength == 0 and currentWifiLevel != len(wifiLevels) - 1:
                    currentWifiLevel = level
                    requester.send("Parsed_overlay_% enable 1" % wifiOverlays[len(wifiOverlays) - 1])
                    # copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")

            print "Wifi level: %d dBm" % wifiStrength

        time.sleep(1)

process = Process(target=processSignals)
process.start()


