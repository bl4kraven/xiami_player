#!/usr/bin/env python
# -*- coding: utf-8 -*-

import getopt
import sys
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
        self.callback = None
        logger.debug("%s"%self.list_ids)

    def _play(self, list_id):
        self.callback = xiami_list_callback(list_id)
        self.player.set_callback(self.callback)
        # just play
        self.callback(self.player)

    def play(self):
        self.backward()

    def forward(self):
        if callable(self.callback):
            self.callback(self.player)

    def backward(self):
        if self.list_counts > 0:
            id = self.list_ids.pop(0)
            self._play(id)
            self.list_ids.append(id)
            logger.debug("%s"%self.list_ids)

    def pause(self):
        # stop thread callback
        if self.player.get_callback():
            self.player.set_callback(None)
        else:
            self.player.set_callback(self.callback)
        self.player.pause()

class xiami_list_callback():
    def __init__(self, list_id):
        self.list_id = list_id
        self._list = None
        self.index = 0

    def __call__(self, _player):
        try:
            if not self._list:
                self.update()

            if self._list.size() > 0:
                if self.index >= self._list.size():
                    self.index = 0

                url = self._list.songs[self.index].url
                self.index += 1
                logger.info("play %s"%url)
                _player.open(url)
        except:
            logger.error("load song fail, list_id=%d"%self.list_id)

    def update(self):
        self.index = 0
        if (self.list_id[0] == 1):
            # album
            self._list = album_list(self.list_id[1])
        else:
            # classic
            self._list = classic_list(self.list_id[1])
        self._list.load_songs()

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

    myplayer = Player()
    myplayer.start()

    my_online_radio = online_radio(myplayer, channel_file)
    my_xiami_list = xiami_player(myplayer, list_id_file)

    # default online radio
    is_xiami = False
    my_radio = my_online_radio
    my_radio.play()

    while True:
        input_char = raw_input("")
        print is_xiami
        if input_char == "q":
            break
        elif input_char == "p":
            my_radio.pause()
        elif input_char == ">":
            my_radio.forward()
        elif input_char == "<":
            my_radio.backward()
        elif input_char == "9":
            my_radio.volume_dec()
        elif input_char == "0":
            my_radio.volume_inc()
        elif input_char == "x":
            is_xiami = not is_xiami
            if is_xiami:
                print "change xiami list player"
                my_radio = my_xiami_list
                my_radio.play()
            else:
                print "change online radio"
                my_radio = my_online_radio
                my_radio.play()

    myplayer.player_close()
