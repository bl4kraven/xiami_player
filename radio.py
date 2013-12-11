#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import sys
import os
from core import *
from player import Player

class radio():
    def __init__(self, _player):
        self.player = _player

    def play(self):
        pass

    def forward(self):
        self.player.forward()

    def backward(self):
        self.player.backward()

    def volume_dec(self):
        self.player.volume_dec()

    def volume_inc(self):
        self.player.volume_inc()

    def pause(self):
        self.player.pause()

    def next_list(self):
        pass

class online_radio(radio):
    def __init__(self, _player, channel_txt):
        radio.__init__(self, _player)
        self.channel_txt = channel_txt

    def play(self):
        print "open online radio channel list"
        self.player.set_callback(None)
        self.player.open_list(self.channel_txt)

class xiami_player(radio):
    def __init__(self, _player, list_id_txt):
        radio.__init__(self, _player)
        # load list_id from list_id_txt
        self.list_ids = [ [ int(i) for i in j.split()] for j in open(list_id_txt).readlines()]
        self.list_counts  = len(self.list_ids)
        # bind player
        logger.debug("%s"%self.list_ids)

        self._list = None
        self.index = 0

    def play(self):
        self.player.set_callback(self)

        try:
            if self.list_counts > 0:
                if self._list and self.index >= self._list.size():
                    # end of album or classic jump to next
                    self.list_ids.append(self.list_ids.pop(0))
                    self._list = None
                    logger.debug("%s"%self.list_ids)

                if not self._list:
                    self.index = 0
                    cur_id = self.list_ids[0]
                    if (cur_id[0] == 1):
                        # album
                        self._list = album_list(cur_id[1])
                    elif (cur_id[0] == 3):
                        # classic
                        self._list = classic_list(cur_id[1])
                    self._list.load_songs()

                if self._list.size() > 0:
                    url = self._list.songs[self.index].url
                    self.index += 1
                    logger.info("play %s"%url)
                    self.player.open(url)
            else:
                logger.debug("list id is empty");
        except:
            logger.error("load song fail")

    def forward(self):
        self.play()

    def backward(self):
        if self.index-1 > 0:
            self.index -= 2
            self.play()

    def next_list(self):
        if self._list:
            self.index = self._list.size()
        self.play()

    def pause(self):
        # stop thread callback
        if self.player.get_callback():
            self.player.set_callback(None)
        else:
            self.player.set_callback(self)
        self.player.pause()

def usage(name):
    print "Usage:"
    print "    %s -c channel_file -l list_id_file"%name

if __name__ == "__main__":

    channel_file = None
    list_id_file = None 
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:l:")
    except getopt.GetoptError as err:
        print err
        usage(sys.argv[0])
        sys.exit(1)
    
    for o, a in opts:
        if o == "-c":
            channel_file = a
        elif o == "-l":
            list_id_file = a
        else:
            assert False, "unhandled option"

    if not channel_file or not list_id_file:
        print "not specific channel file or list id file"
        usage(sys.argv[0])
        sys.exit(1)

    if not os.path.isfile(channel_file) or not os.path.isfile(list_id_file):
        print "file not exist"
        usage(sys.argv[0])
        sys.exit(1)

    myplayer = Player()
    myplayer.player_start()

    radios = [online_radio(myplayer, channel_file), xiami_player(myplayer, list_id_file)]
    my_radio = radios[0]
    my_radio.play()

    try:
        while True:
            input_char = raw_input("")
            if input_char == "q":
                break
            elif input_char == "p":
                my_radio.pause()
            elif input_char == ">":
                my_radio.forward()
            elif input_char == "<":
                my_radio.backward()
            elif input_char == "z":
                my_radio.next_list()
            elif input_char == "9":
                my_radio.volume_dec()
            elif input_char == "0":
                my_radio.volume_inc()
            elif input_char == "x":
                # must restart player, player may be stuck on radio mode
                myplayer.player_restart()
                radios.append(radios.pop(0))
                my_radio = radios[0]
                my_radio.play()
    except KeyboardInterrupt:
        pass

    myplayer.player_close()
    myplayer.destroy()
