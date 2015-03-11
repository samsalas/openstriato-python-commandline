#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" script to use openstriato commands
"""

import sys, getopt, os, time
import xml.etree.ElementTree as ET

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
    cmd = getactionfromuid(uid)
    res = os.popen(cmd+"&").read()
    print "result: "+res

def getactionfromuid(uid):
    """ get the command from the xml file
    """
    tree = ET.parse('openstriato.xml')
    root = tree.getroot()
    textaction = root.findall("./action[@uid='"+uid+"']")
    if len(textaction) == 0:
        #add uid if new uid in setting file
        defaulttext = "echo 'This UID didn t exist so it has been automatically added'"
        tag = ET.SubElement(root, 'action')
        tag.text = "echo 'This UID has been automatically added'"
        tag.attrib['uid'] = uid
        tree.write('openstriato.xml')
        return defaulttext
    else:
        return textaction[0].text

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
            elif tokens[1] == 'Classic': #MIFARE Classic
                typeuid = 1
                print tokens[0]
            elif tokens[1] == 'Ultralight': #MIFARE Ultralight
                typeuid = 2
            elif tokens[0] == 'UID:':
                if typeuid == 1: #MIFARE Classic
                    uid = tokens[1]+tokens[2]+tokens[3]+tokens[4]
                    print 'uid found:', uid
                    doaction(uid)
                elif typeuid == 2: #MIFARE Ultralight
                    uid = tokens[1]+tokens[2]+tokens[3]+\
                    tokens[4]+tokens[5]+tokens[6]+tokens[7]
                    print 'uid found:', uid
                    doaction(uid)
                else:
                    print 'uid type unknown'
                typeuid = 0
        time.sleep(.100)

if __name__ == "__main__":
    main(sys.argv[1:])

