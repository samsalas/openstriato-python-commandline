#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" script to use openstriato commands
"""

OPENSTRIATOFILE = "/home/pi/openstriato/openstriato.xml"

import sys, getopt, os, time
import xml.etree.ElementTree as ET

from subprocess import Popen, PIPE

def main(argv):
    """ Main for using the command line
    """
    config = ''
    uidcmd = ''
    uidmodif = ''
    try:
        opts, args = getopt.getopt(argv, "hd:r:u:m:y:", ["doaction=", \
        "run=", "uid=", "modifaction=", "youtube="])
    except getopt.GetoptError:
        print 'openstriato.py -d <doaction> -r <run> -u <uid> -m <modifaction> -y <youtube>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'openstriato.py'
            print '-d or --doaction=UID		Do an action with the uid'
            print '-r or --run=TEXT		If TEXT = "start" Run the pooling'
            print '-u or --uid=UID			Display an action with the uid'
            print '-m or --modifaction=TEXT	Must be combined with -u to modify the action in relation with the uid'
            print '-y or --youtube=TEXT		Download the video as a mp4 file in /home/pi/video, TEXT must be the hashtag from youtube'
            sys.exit()
        elif opt in ("-d", "--doaction"):
            doaction(arg)
        elif opt in ("-r", "--run"):
            if arg == 'start':
                print 'Run polling...'
                runpolling()
        elif opt in ("-u", "--uid"):
            if uidmodif != '':
                print modifyaction(arg, uidmodif)
            else:
                print displayaction(arg)
                uidcmd = arg
        elif opt in ("-m", "--modifaction"):
            if uidcmd != '':
                print modifyaction(uidcmd, arg)
            else:
			   uidmodif = arg
        elif opt in ("-y", "--youtube"):
            youtube(arg)

def doaction(uid):
    """ Do an action from the list of actions available
    """
    cmd = getactionfromuid(uid)
    res = os.popen(cmd+"&").read()
    print "result: "+res

def youtube(ytid):
    """ Download the video as a mp4 file in /home/pi/video
    """
    cmd = "youtube-dl -o \"/home/pi/video/%(id)s-%(title)s.%(ext)s\" " + ytid
    res = os.popen(cmd+"&").read()
    print "result: "+res

def displayaction(uid):
    """ Display the command from the xml file
    """
    tree = ET.parse(OPENSTRIATOFILE)
    root = tree.getroot()
    textaction = root.findall("./action[@uid='"+uid+"']")
    if len(textaction) == 0:
        return "This UID does not exist!"
    else:
        return "UID %s action: %s" % (uid, textaction[0].text)

def modifyaction(uid, cmd):
    """ Modify the command in the xml file
    """
    tree = ET.parse(OPENSTRIATOFILE)
    root = tree.getroot()
    textaction = root.findall("./action[@uid='"+uid+"']")
    if len(textaction) == 0:
        return "This UID does not exist!"
    else:
        textaction[0].text = cmd
        tree.write(OPENSTRIATOFILE)
        return "UID %s new action: %s" % (uid, cmd)

def getactionfromuid(uid):
    """ Get the command from the xml file
    """
    tree = ET.parse(OPENSTRIATOFILE)
    root = tree.getroot()
    textaction = root.findall("./action[@uid='"+uid+"']")
    if len(textaction) == 0:
        #add uid if new uid in setting file
        defaulttext = "echo 'This UID didn t exist so it has been automatically added'"
        tag = ET.SubElement(root, 'action')
        tag.text = "echo 'This UID has been automatically added'"
        tag.attrib['uid'] = uid
        tree.write(OPENSTRIATOFILE)
        return defaulttext
    else:
        return textaction[0].text

def runpolling():
    """ Run the polling for RFID
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
            elif tokens[1] == 'Plus': #MIFARE Plus
                typeuid = 3
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
                elif typeuid == 3: #MIFARE Plus
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

