#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import thread
import subprocess
import time
from select import select

class Player(threading.Thread):

    """ mplayer -slave mode, cmd will find by mplayer -input cmdlist"""

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = True
        self.callback = None
        cmd = "mplayer -idle -slave -nolirc -nomouseinput -msglevel all=-1:statusline=5 -cache 100 -volstep 5 -softvol -softvol-max 300 -prefer-ipv4".split()
        # universal_newlines will let \r as newline end
        self.popen = subprocess.Popen(cmd, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

    def run(self):
        while self.running:
            # wait for song end 4 seconds
            read_sets,_,_ = select([self.popen.stdout], [], [], 4)
            if read_sets:
                # \r is newline end
                line = self.popen.stdout.readline()
                #print line
                #line.startswith("A:"):
            else:
                print "call callable"
                if (callable(self.callback)):
                    self.callback(self)


    def set_callback(self, callback):
        self.callback = callback

    def get_callback(self):
        return self.callback

    def player_close(self):
        self.running = False
        if self.popen.poll() == None:
            # wait for process
            self.quit()
            self.popen.wait()
            print "close process"

        # wait for thread
        if self.isAlive():
            self.join()
            print "close thread"

    # every url or list must end with "", so stderr will print Failed to open "". 
    # so the player known play is end and call callback object.
    def open(self, url):
        self.request("loadfile \"%s\"\n" % url)

    def open_list(self, file_path):
        self.request("loadlist \"%s\"\n" % file_path)

    def pause(self):
        self.request("pause\n")

    def stop(self):
        self.request("stop\n")

    def quit(self):
        self.request("quit\n")

    def forward(self):
        self.request("pt_step 1\n")

    def backward(self):
        self.request("pt_step -1\n")

    def volume_inc(self):
        self.request("volume 1\n")
        
    def volume_dec(self):
        self.request("volume -1\n")

    def get_pos(self):
        self.request("get_percent_pos\n")

    def request(self, text):
        self.popen.stdin.write(text)

if __name__ == "__main__":
    myplayer = Player()
    myplayer.start()
    myplayer.open("mms://live.cri.cn/oldies")

    while True:
        input_char = raw_input(">")
        if input_char == "q":
            break
        elif input_char == "n":
            myplayer.forward()
        elif input_char == "p":
            myplayer.backward()
        elif input_char == "9":
            myplayer.volume_dec()
        elif input_char == "0":
            myplayer.volume_inc()

    myplayer.player_close()
