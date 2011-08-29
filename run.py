#!/usr/bin/python

from os import kill
from subprocess import Popen, PIPE
from time import strftime, localtime, time

import threading

port = 1337

class ServerThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(ServerThread, self).__init__()

    def run(self):
        self.proc = Popen(['python', 'server.py', str(port)])
        self.proc.communicate()

def run():
    count = 0
    while True:
        t = time()
        thread = ServerThread()
        thread.start()
        print "%d: starting server" % (count), strftime("%Y/%m/%d %H:%M:%S", localtime())
        count += 1
        while True:
            if (time() - t) > 300:
                print "restarting server", strftime("%Y/%m/%d %H:%M:%S", localtime())
                print "tried killing server PID: %d" % (thread.proc.pid)
                kill(thread.proc.pid, 9)
                break

if __name__ == '__main__':
    run()
