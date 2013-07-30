#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom as minidom
import logging
from logging.handlers import SysLogHandler
import urllib
import urllib2

def get_logger(log_name):
    format = "%(asctime)s %(levelname)s %(message)s"
    level = logging.DEBUG
    logging.basicConfig(format=format, level=level)
    logger = logging.getLogger(log_name)
    #handler = SysLogHandler(address="/dev/log")
    #logger.addHandler(handler)
    return logger

logger = get_logger("radio")

class MyObject():

    def __init__(self):
        pass

    def parse_node(self, node):
        '''解析xml节点添加实例属性'''

        for childNode in node.childNodes:
            name = childNode.nodeName
            if childNode.hasChildNodes():
                value = childNode.childNodes[0].data
            else:
                value = ""
            setattr(self, name, value)


class Song(MyObject):

    def __init__(self):
        MyObject.__init__(self)
        self.url = None

    def load_streaming(self):
        addr = self.location
        count = (int)(addr[0])
        addr = addr[1:]
        addr_length = len(addr)
        avarge_len = addr_length / count
        rest = addr_length % count

        logger.debug(("%d %d %s")%(addr_length, rest, addr))

        # take rest char
        result_rest = ""
        while rest > 0:
            pos = (avarge_len+1)*rest-1
            result_rest = addr[pos] + result_rest
            addr = addr[:pos] + addr[pos+1:]
            rest -= 1
        
        result = ""
        for x in range(avarge_len):
            for y in range(count):
                result += addr[x + avarge_len*y]

        result += result_rest
        result = urllib.unquote(result)
        result = result.replace("^", "0")
        logger.debug(result)
        self.url = result

    def show(self):
        logger.info("song_id:%s"%self.song_id)
        logger.info("location:%s"%self.location)

class Songlist(MyObject):

    def __init__(self, tag_name):
        MyObject.__init__(self)
        self.songs = []
        self.tag_name = tag_name

    def load_songs(self):
        pass

    def parse_xml(self, xml):
        self.songs = []
        dom = minidom.parseString(xml)
        for childNode in dom.getElementsByTagName(self.tag_name)[0].childNodes:
            if (childNode.nodeType == childNode.ELEMENT_NODE):
                song = Song()
                song.parse_node(childNode)
                self.songs.append(song)
        return self.songs
                
    def show(self):
        for song in self.songs:
            song.show()
            logger.info("")

    def size(self):
        return len(self.songs)

class play_list(Songlist):

    def __init__(self, id, url):
        Songlist.__init__(self, "trackList")
        self.id = id
        self.url = url

    def load_songs(self):
        logger.info("load radio songs id:%d ..."%self.id)

        headers = { "User-Agent":"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0"}
        request = urllib2.Request(self.url, headers=headers)
        urlopener = urllib2.urlopen(request)
        xml = urlopener.read()
        self.parse_xml(xml)
        for song in self.songs:
            song.load_streaming()
        return self.songs

class radio_list(play_list):

    def __init__(self, id):
        play_list.__init__(self, id, "http://www.xiami.com/radio/xml/type/5/id/%d"%id)

class album_list(play_list):

    def __init__(self, id):
        play_list.__init__(self, id, "http://www.xiami.com/song/playlist/id/%d/type/1"%id)

class classic_list(play_list):

    def __init__(self, id):
        play_list.__init__(self, id, "http://www.xiami.com/song/playlist/id/%d/type/3"%id)

if __name__ == "__main__":
    radio_test = album_list(8375097)
    radio_test.load_songs()
    radio_test.show()
