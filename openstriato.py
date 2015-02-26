#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" script to use openstriato commands
"""

import sys, getopt, os, time
from subprocess import Popen, PIPE

def main(argv):
    """ Main for using the command line
    """
    config = ''
    try:
        opts, args = getopt.getopt(argv, "hc:d:a:r:", ["config=", "doaction=", \
        "addaction=", "run="])
    except getopt.GetoptError:
        print 'openstriato.py -c <config> -d <doaction> -a <addaction> -r <run>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'openstriato.py -c <config> -d <doaction> -a <addaction> -r <run>'
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg
            print 'Settings is "'+config+'"'
        elif opt in ("-d", "--doaction"):
            doaction(arg)
        elif opt in ("-a", "--addaction"):
            print 'Action is "'+arg+'"'
        elif opt in ("-r", "--run"):
            if arg == 'start':
                print 'Run polling...'
                runpolling()

def doaction(uid):
    """ Do an action from the list of actions available
    """
    actionlist = ["echo 'This UID doesn t exist in the database'", \
    "echo 'bonjour'", "omxplayer -o hdmi /home/pi/video/peppa.mp4", \
    "echo 'merci'", "omxplayer -o hdmi /home/pi/video/ouioui.mp4"]
    if uid == int('0x8D73F44C', 0):
        sendcommand(actionlist[1])
    elif uid == int('0x04FB40915B2380', 0):
        sendcommand(actionlist[2])
    elif uid == int('0xDDD9F34C', 0):
        sendcommand(actionlist[3])
    elif uid == int('0xAA8847DF', 0):
        sendcommand(actionlist[4])
    else:
        sendcommand(actionlist[0])

def sendcommand(cmd):
    """ Runs the command in cmd
    """
    res = os.popen(cmd+"&").read()
    print "result: "+res

def runpolling():
    """ Runs the polling for RFID
    """
    res = Popen("sudo ./card_polling", shell=True, stdin=PIPE, stdout=PIPE)
    typeuid = 0
    while 1:
        line = res.stdout.readline()
        if line == '':
            print "no line"
        else:
            tokens = line.split(" ")
            if len(tokens) <= 2:
                print 'line too short'
            elif tokens[1] == 'Classic':
                typeuid = 1
                print tokens[0]
            elif tokens[1] == 'Ultralight':
                typeuid = 2
            elif tokens[0] == 'UID:':
                if typeuid == 1:
                    uid = tokens[1]+tokens[2]+tokens[3]+tokens[4]
                    print 'uid found:', uid
                    doaction(int('0x'+uid, 0))
                elif typeuid == 2:
                    uid = tokens[1]+tokens[2]+tokens[3]+tokens[4]+\
                    tokens[5]+tokens[6]+tokens[7]+tokens[8]
                    print 'uid found:', uid
                    doaction(int('0x'+uid, 0))
                else:
                    print 'uid type unknown'
                typeuid = 0
        time.sleep(.100)

if __name__ == "__main__":
    main(sys.argv[1:])

