#!/usr/bin/python

import sys
import socket
import string

connected = 0

def reply (msg):
    sys.stdout.write (msg)
    sys.stdout.flush ()


def log (msg):
    sys.stderr.write (msg.strip () + '\n')

stdin = socket.fromfd (sys.stdin.fileno (), socket.AF_INET, socket.SOCK_STREAM)

while 1:
#    v = sys.stdin.readline ()
    vs = stdin.recv (4096)
    ls = vs.split ('\n.\n')
    if len (ls) > 1:
        ls[0] = ls[0] + '\n.\n'

    for v in ls:
        if len (v.strip ()) == 0:
            continue   
        log ('cmd: ' + v)
        if not connected:
            arr = v.split (' ')
            if arr[0] == 'CONNECT':
                t = arr[1].split (':')
                server = t[0]
                port = int (t[1])
                s = socket.socket (socket.AF_INET, socket.SOCK_STREAM)
                s.connect ((server, port))
                reply ('HTTP/1.0 200 Connection established\r\n\r\n')
                connected = 1
                log ('Connected to %s:%d' % (server, port))
                data = s.recv (4096)
                if data:
                    reply (data)
        elif v.strip () == 'LIST':
            res = 'AVAZ AB FOREX Autovaz 2\r\n.\r\n'
            log ('own: '+res)
            reply (res)
        else:
            s.send (v + '\n')
            data = s.recv (4096)
            log ('put: ' + data)
            if not data:
                break
            reply (data)
s.close ()
