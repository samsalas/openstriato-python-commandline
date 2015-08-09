#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" script to use openstriato commands
"""

from subprocess import Popen, PIPE
import sys, getopt, os, time, psutil, datetime
import xml.etree.ElementTree as ET

POSIX = os.name == 'posix'
OPENSTRIATOFILE = "/home/pi/openstriato/openstriato.xml"
OSPROCESS = 0
UIDINPROCESS = ''

def main(argv):
    """ Main for using the command line
    """
    uidcmd = ''
    uidmodif = ''
    notemodif = ''
    try:
        opts, args = getopt.getopt(argv, "hsd:r:u:m:n:y:", ["doaction=", \
        "run=", "uid=", "modifaction=", "modifnote=", "youtube="])
    except getopt.GetoptError:
        print 'openstriato.py -h <help> -s <stop> -d <doaction> -r <run> -u <uid> -m <modifaction> -n <modifnote> -y <youtube>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'openstriato.py'
            print '-d or --doaction=UID		Do an action with the uid'
            print '-s				Stop the pooling'
            print '-r or --run=TEXT		If TEXT = "start" Run the pooling'
            print '-u or --uid=UID			Display an action with the uid'
            print '-m or --modifaction=TEXT	Must be combined with -u to modify the action in relation with the uid'
            print '-n or --modifnote=TEXT	Must be combined with -u to modify the note in relation with the uid'
            print '-y or --youtube=TEXT		Download the video as a mp4 file in /home/pi/video, TEXT must be the hashtag from youtube'
            sys.exit()
        elif opt in ("-s", "--stop"):
            stopaction()
        elif opt in ("-d", "--doaction"):
            doaction(arg)
        elif opt in ("-r", "--run"):
            if arg == 'start':
                print 'Run polling...'
                runpolling()
        elif opt in ("-u", "--uid"):
            if uidmodif != '':
                print modifyaction(arg, uidmodif)
            elif notemodif != '':
                print modifynote(arg, notemodif)
            else:
                print displayaction(arg)
                uidcmd = arg
        elif opt in ("-m", "--modifaction"):
            if uidcmd != '':
                print modifyaction(uidcmd, arg)
            else:
                uidmodif = arg
        elif opt in ("-n", "--modifnote"):
            if uidcmd != '':
                print modifynote(uidcmd, arg)
            else:
                notemodif = arg
        elif opt in ("-y", "--youtube"):
            youtube(arg)

def stopaction():
    """ Stop the openstriato process (we suppose only one is running)
    """
    idos = idfromexe('python2.7')
    if idos != 0:
        program = psutil.Process(idos)
        program.terminate()
        print 'openstriato PID %d terminated' % idos
    else:
        print 'openstriato not running'

def doaction(uid):
    """ Do an action from the list of actions available
    """
    print "Stop previous process"
    global OSPROCESS
    global UIDINPROCESS
    if UIDINPROCESS != uid:
        UIDINPROCESS = uid
        if OSPROCESS != 0:
            program = psutil.Process(OSPROCESS)
            program.terminate()
            print 'Process %d terminated' % OSPROCESS
        print "start new process"
        cmd = getactionfromuid(uid)
        tokencmd = cmd.split(" ")
        print tokencmd
        OSPROCESS = Popen(tokencmd).pid
        print "Process: %d" % OSPROCESS

def processdetailinfo(pid):
    """ Give detailed process information
    """
    val = []
    listpid = psutil.pids()
    for procid in listpid:
        if pid == procid or pid == 'all':
            val += [returnprocessinfo(procid)]
    return val

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
        tree.write(OPENSTRIATOFILE, encoding='utf-8', xml_declaration=True)
        return "UID %s new action: %s" % (uid, cmd)

def modifynote(uid, cmd):
    """ Modify the note in the xml file
    """
    tree = ET.parse(OPENSTRIATOFILE)
    root = tree.getroot()
    textaction = root.findall("./action[@uid='"+uid+"']")
    if len(textaction) == 0:
        return "This UID does not exist!"
    else:
        textaction[0].attrib['note'] = cmd
        tree.write(OPENSTRIATOFILE, encoding='utf-8', xml_declaration=True)
        return "UID %s new note: %s" % (uid, cmd)

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
        tree.write(OPENSTRIATOFILE, encoding='utf-8', xml_declaration=True)
        return defaulttext
    else:
        return textaction[0].text

def bytes2human(num):
    """ Convert numbers in string readable by humans
    """
    # http://code.activestate.com/recipes/578019
    # >>> bytes2human(10000)
    # '9.8K'
    # >>> bytes2human(100001221)
    # '95.4M'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, symb in enumerate(symbols):
        prefix[symb] = 1 << (i + 1) * 10
    for symb in reversed(symbols):
        if num >= prefix[symb]:
            value = float(num) / prefix[symb]
            return '%.1f%s' % (value, symb)
    return "%sB" % num

def returnprocessinfo(pid):
    """ Return the detailed information for the process ID
    """
    accessdenied = ''
    val = ''
    try:
        proc = psutil.Process(pid)
        pinfo = proc.as_dict(ad_value=accessdenied)
    except psutil.NoSuchProcess as err:
        sys.exit(str(err))

    try:
        parent = proc.parent()
        if parent:
            parent = '(%s)' % parent.name()
        else:
            parent = ''
    except psutil.Error:
        parent = ''
    if pinfo['create_time'] != accessdenied:
        started = datetime.datetime.fromtimestamp(
            pinfo['create_time']).strftime('%Y-%m-%d %H:%M')
    else:
        started = accessdenied
    #inout = pinfo.get('io_counters', accessdenied)
    if pinfo['memory_info'] != accessdenied:
        mem = '%s%% (resident=%s, virtual=%s) ' % (
            round(pinfo['memory_percent'], 1),
            bytes2human(pinfo['memory_info'].rss),
            bytes2human(pinfo['memory_info'].vms))
    else:
        mem = accessdenied
    #children = proc.children()

    val += 'pid %s' % pinfo['pid']
    val += ' - name %s' % pinfo['name']
    val += ' - exe %s' % pinfo['exe']
    #print_('parent', '%s %s' % (pinfo['ppid'], parent))
    #print_('cmdline', ' '.join(pinfo['cmdline']))
    #print_('started', started)
    val += ' - username %s' % pinfo['username']
    if POSIX and pinfo['uids'] and pinfo['gids']:
        val += ' - uids %s' % 'real=%s, effective=%s, saved=%s' % pinfo['uids']
    if POSIX and pinfo['gids']:
        val += ' - gids %s' % 'real=%s, effective=%s, saved=%s' % pinfo['gids']
    if POSIX:
        val += ' - terminal %s' % pinfo['terminal'] or ''
    #print_('cwd', pinfo['cwd'])
    val += ' - memory %s' % mem
    val += ' - cpu %s' % ('%s%% (user=%s, system=%s)' % (
        pinfo['cpu_percent'],
        getattr(pinfo['cpu_times'], 'user', '?'),
        getattr(pinfo['cpu_times'], 'system', '?')))
    val += ' - status %s' % pinfo['status']
    #print_('niceness', pinfo['nice'])
    val += ' - num threads %s' % pinfo['num_threads']
    #if io != accessdenied:
    #    print_('I/O', 'bytes-read=%s, bytes-written=%s' % (
    #        bytes2human(io.read_bytes),
    #        bytes2human(io.write_bytes)))
    #if children:
    #    print_('children', '')
    #    for child in children:
    #        print_('', 'pid=%s name=%s' % (child.pid, child.name()))

    #if pinfo['open_files'] != accessdenied:
    #    print_('open files', '')
    #    for file in pinfo['open_files']:
    #        print_('', 'fd=%s %s ' % (file.fd, file.path))
    #if pinfo['threads']:
    #    print_('running threads', '')
    #    for thread in pinfo['threads']:
    #        print_('', 'id=%s, user-time=%s, sys-time=%s' % (
    #            thread.id, thread.user_time, thread.system_time))
    #if pinfo['connections'] not in (ACCESS_DENIED, []):
    #    print_('open connections', '')
    #    for conn in pinfo['connections']:
    #        if conn.type == socket.SOCK_STREAM:
    #            type = 'TCP'
    #        elif conn.type == socket.SOCK_DGRAM:
    #            type = 'UDP'
    #        else:
    #            type = 'UNIX'
    #        lip, lport = conn.laddr
    #        if not conn.raddr:
    #            rip, rport = '*', '*'
    #        else:
    #            rip, rport = conn.raddr
    #        print_('', '%s:%s -> %s:%s type=%s status=%s' % (
    #            lip, lport, rip, rport, type, conn.status))
    return val

def idfromexe(exename):
    """ Give the status information of a proces
    """
    listpid = psutil.pids()
    for procid in listpid:
        accessdenied = ''
        try:
            proc = psutil.Process(procid)
            pinfo = proc.as_dict(ad_value=accessdenied)
        except psutil.NoSuchProcess as err:
            sys.exit(str(err))
        try:
            parent = proc.parent()
            if parent:
                parent = '(%s)' % parent.name()
            else:
                parent = ''
        except psutil.Error:
            parent = ''
        if pinfo['name'] == exename:
            return pinfo['pid']
    return 0

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

