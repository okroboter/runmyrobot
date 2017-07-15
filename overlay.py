import time
import subprocess
import argparse
import requests
from multiprocessing import Process
from shutil import copyfile

parser = argparse.ArgumentParser(description='Overlay controls')
parser.add_argument('--wifi', dest='wifi')
parser.set_defaults(wifi=None)
parser.add_argument('--image', dest='image')
parser.set_defaults(image=None)

commandArgs = parser.parse_args()

DIR_SRC = "/home/pi/runmyrobot/overlay/"
DIR_DST = "/dev/shm/"
wifiLevels = [-90, -80, -70, -50, 0]
currentWifiLevel = 0

def processSignals():

    global currentWifiLevel

    while True:

        if commandArgs.wifi is not None:

            wifiStrength, perr = subprocess.Popen('/sbin/iwconfig %s | grep Signal|cut -d"=" -f3|cut -d" " -f1' % commandArgs.wifi,
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
                    currentWifiLevel = level
                    copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")
                    break
                elif dbStrength == 0 and currentWifiLevel != len(wifiLevels) - 1:
                    currentWifiLevel = level
                    copyfile(DIR_SRC + "wifi_%d.png" % level, DIR_DST + "wifi.png")

            print "Wifi level: %d dBm" % wifiStrength

        time.sleep(1)

process = Process(target=processSignals)
process.start()


