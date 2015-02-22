#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" script to use openstriato commands
"""

import sys, getopt, os

def main(argv):
    """ Main for using the command line
    """
    config = ''
    addaction = ''
    try:
        opts, args = getopt.getopt(argv, "hcda:", ["config=", "doaction=", "addaction="])
    except getopt.GetoptError:
        print 'openstriato.py -c <config> -do <doaction> -add <addaction>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'openstriato.py -c <config> -do <doaction> -add <addaction>'
            sys.exit()
        elif opt in ("-c", "--config"):
            config = arg
            print 'Settings is "'+config
        elif opt in ("-do", "--doaction"):
            action(int(arg))
        elif opt in ("-add", "--addaction"):
            print 'Action is "'+arg

def action(actionid):
    """ Do an action from the list of actions available
    """
    actionlist = ["echo 'bonjour'", "echo 'au revoir'", "echo 'merci'", "echo 'coucou'"]
    if actionid >= 1 and actionid <= 4:
        print "action: "+actionlist[actionid]
        res = os.popen(actionlist[actionid]).read()
        print "result: "+res
    else:
        print "This action ID doesn't exist"

if __name__ == "__main__":
    main(sys.argv[1:])

