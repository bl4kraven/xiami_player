#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import thread
import subprocess
import time
import os
from select import select

class Player(threading.Thread):

    """ mplayer -slave mode, cmd will find by mplayer -input cmdlist"""

    def __init__(self):
        threading.Thread.__init__(self)
        # thread running
        self.running = True
        self.callback = None
        # player running
        self.player_running = None
        # start thread
        self.start()

    def run(self):
        # thread never quit
        while self.running:
            if self.player_running:
                # wait for song end 4 seconds
                read_sets,_,_ = select([self.popen.stdout], [], [], 4)
                if read_sets:
                    # \r is newline end
                    line = self.popen.stdout.readline()
                    #print line
                    #line.startswith("A:"):
                else:
                    print "call callback"
                    if (self.callback):
                        self.callback.play()
            else:
                time.sleep(1)

    def destroy(self):
        self.running = False
        # wait for thread
        if self.isAlive():
            self.join()
            print "close thread"

    def set_callback(self, callback):
        self.callback = callback

    def get_callback(self):
        return self.callback

    def player_start(self):
        cmd = "mplayer -idle -slave -nolirc -nomouseinput -msglevel all=-1:statusline=5 -cache 100 -volstep 5 -softvol -softvol-max 300 -prefer-ipv4".split()
        # universal_newlines will let \r as newline end
        self.popen = subprocess.Popen(cmd, universal_newlines=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.player_running = True

    def player_close(self):
        self.player_running = False
        if self.popen.poll() == None:
            # wait for process
            self.quit()

            # because wait can't timeout on python 2.7 , so dirty hack-_-!!! 
            def kill_proc(self):
                self.kill()
            timer=threading.Timer(2, kill_proc, [self])
            timer.start()
            self.popen.wait()
            timer.cancel()
            print "close process"

    def player_restart(self):
        self.player_close()
        self.player_start()

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

    def kill(self):
        self.popen.kill()

    def forward(self):
        self.request("pt_step 1\n")

    def backward(self):
        self.request("pt_step -1\n")

    def volume_inc(self):
        #self.request("volume 1\n")
        os.system("amixer sset PCM 1dB+ >/dev/null")

    def volume_dec(self):
        #self.request("volume -1\n")
        os.system("amixer sset PCM 1dB- >/dev/null")

    def get_pos(self):
        self.request("get_percent_pos\n")

    def request(self, text):
        self.popen.stdin.write(text)

if __name__ == "__main__":
    myplayer = Player()

    i=0
    while i<2:
        i+=1
        myplayer.player_start()
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

    myplayer.destroy()
