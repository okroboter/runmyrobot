import os
import time
import serial
import random
import thread
import Robot
LEFT_TRIM   = 0
RIGHT_TRIM  = 0

# Create an instance of the robot with the specified trim values.
# Not shown are other optional parameters:
#  - addr: The I2C address of the motor HAT, default is 0x60.
#  - left_id: The ID of the left motor, default is 1.
#  - right_id: The ID of the right motor, default is 2.
robot = Robot.Robot(left_trim=LEFT_TRIM, right_trim=RIGHT_TRIM)

# initialize serial connection
serialBaud = 115200
serialDevice = '/dev/ttyACM0'
ser = serial.Serial(serialDevice, serialBaud, timeout=1)  # open serial

def speak(message, tempFilePath):

    # The AdaFruit speaker bonnet doesn't support mono files, so need to convert the mono file
    # from espeak into a stereo version that aplay can work with. NOTE: the ffmpeg path must be a full path.
    os.system('cat ' + tempFilePath + ' | espeak --stdout | /usr/local/bin/ffmpeg -i - -ar 44100 -ac 2 -ab 192k -f wav - | aplay -D plughw:0,0')

marvinLastToggleTime = 0
marvinLastQuoteTime = 0
marvinQuotes = [
        "I think you ought to know I'm feeling very depressed",
        "I'm not getting you down at all, am I?",
        "Pardon me for breathing, which I never do any way so I don't know why I bother to say it",
        "Oh God, I'm so depressed.",
        "Funny, how just when you think life can't possibly get any worse it suddenly does.",
        "Do you want me to sit in the corner and rust, or just fall apart where I'm standing?",
        "Would you like me to go and stick my head in a bucket of water?",
        "Life's bad enough as it is without wanting to invent any more of it.",
        "Wearily I sit here, pain and misery my only companions.",
        "Why stop now just when I'm hating it?",
        "Life, loathe it or ignore it, you can't like it.",
        "I won't enjoy it.",
        "Why should I want to make anything up? Life's bad enough as it is without wanting to invent anymore of it.",
        "Life! Don't talk to me about life.",
        "Here I am, brain the size of a planet, and they tell me to take you up to the bridge.",
        "Call that job satisfaction? 'Cos I don't.",
        "You think you've got problems? What are you supposed to do if you are a manically depressed robot?",
        "I'm fifty thousand times more intelligent than you and even I don't know the answer.",
        "It gives me a headache just trying to think down to your level.",
        "There's only one life-form as intelligent as me within thirty parsecs of here, and that's me.",
        "I wish you'd just tell me rather trying to engage my enthusiasm, because I haven't got one.",
        "And then of course I've got this terrible pain in all the diodes down my left side."
        ]


def handle_command(command, commandArgs, say):

    global marvinLastToggleTime
    global marvinLastQuoteTime

    proximity_alert = ""

    if command == 'L':
        robot.left(commandArgs.driving_speed, commandArgs.turn_delay)
    elif command == 'R':
        robot.right(commandArgs.driving_speed, commandArgs.turn_delay)
    elif command == 'F':
        sendSerial("!")

        while True:
            if ser.inWaiting() > 0:
                proximity_alert = ser.read(2)
                if proximity_alert != "!F":
                    robot.forward(commandArgs.driving_speed, commandArgs.straight_delay)
                else:
                    say("Proximity alert!")
                ser.flushInput()
                break
    elif command == 'B':
        robot.backward(commandArgs.driving_speed, commandArgs.straight_delay)
    elif command == 'N':
        sendSerial('U')
    elif command == 'S':
        sendSerial('D')
    elif command == 'W':
        sendSerial('L')
    elif command == 'E':
        sendSerial('R')
    elif command == 'C':
        sendSerial('C')
    elif command == 'M':
        sendSerial('M')
    elif command == 'T':
        curToggleTime = time.time()
        if marvinLastToggleTime == 0 or (curToggleTime - marvinLastToggleTime) > 1:
            sendSerial('T')
        marvinLastToggleTime = curToggleTime
    elif command.startswith('@'):
        sendSerial(command)

    curQuoteTime = time.time()
    # Wait at least 60 seconds before randomly saying anything
    if marvinLastQuoteTime == 0 or (curQuoteTime - marvinLastQuoteTime) > 90:
        # Randomly determine if we should say anything
        if (bool(random.getrandbits(1))):
            # Say something oblique
            try:
                threadArgs = (random.sample(marvinQuotes, 1)[0],)
                thread.start_new_thread(say, threadArgs)
                # say(random.sample(marvinQuotes, 1)[0])
            except Exception, err:
                print "Error: Unable to start random message thread. %s" % err

            marvinLastQuoteTime = curQuoteTime


def sendSerial(command):

    print(ser.name)         # check which port was really used
    ser.nonblocking()
    ser.write(command)     # write a string
    ser.flush()
