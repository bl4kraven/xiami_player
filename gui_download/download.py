#!/usr/bin/env python
# -*- coding: utf-8 -*-
import core
import urllib
import sys
from os import path
from os import makedirs
import eyed3
import progressbar

# user-agent
class MyURLopener(urllib.FancyURLopener):
    version = "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:21.0) Gecko/20100101 Firefox/21.0"
urllib._urlopener = MyURLopener()

def _add_ID3(file, artist, album, title, track_num):
    try:
        mp3 = eyed3.load(file)
        mp3.initTag()
        mp3.tag.artist = artist
        mp3.tag.album = album
        mp3.tag.title = title
        mp3.tag.track_num = track_num
        mp3.tag.save()
    except IOError:
        print "写入mp3 ID3信息失败", file

progress = progressbar.ProgressBar(maxval=100)
def _report_hook(cur_block, byte_per_block, total_size):
    global progress
    if total_size > 0:
        if cur_block == 0:
            progress.start()
        elif cur_block == -1:
            progress.finish()
            return
        now = 100.0 * cur_block * byte_per_block / total_size
        if now >= 100.0:
            now = 100.0
        progress.update(now)

def download_album(album_id, download_dir, report_hook):
    album = core.album_list(album_id)
    songs = album.load_songs()
    if songs:
        try:
            album_name = songs[0].album_name.encode("utf8")
            album_artist = songs[0].artist .encode("utf8")
            album_path = path.join(download_dir, album_artist+"-"+album_name)
            album_pic_url = songs[0].pic
            album_pic_path = path.join(album_path, "cover.jpg")
            if not path.exists(album_path):
                makedirs(album_path, 0755)
            if not path.exists(album_pic_path):
                urllib.urlretrieve(album_pic_url, album_pic_path)

            index = 1
            for song in songs:
                song_name = song.title.encode("utf8")
                print "下载:", song_name
                song_lrc_path = path.join(album_path, song_name+".lrc")
                if not path.exists(song_lrc_path):
                    urllib.urlretrieve(song.lyric, song_lrc_path)

                song_path = path.join(album_path, song_name+".mp3")
                if not path.exists(song_path):
                    urllib.urlretrieve(song.url, song_path, reporthook=report_hook)
                    # tell hook download over
                    report_hook(-1, 0, 1)
                # add mp3 ID3 Tag
                _add_ID3(song_path.decode("utf8"), song.artist, song.album_name, song.title, index)
                index += 1
        except IOError:
            print "下载失败"
    else:
        print "没找到相应专辑"

def main(args):
    import getopt
    try:
        opts, args = getopt.getopt(args[1:], "")
        if len(args) != 1:
            return 1

        album_id = int(args[0])
        download_album(album_id, path.expanduser("~/音乐"), _report_hook)
        return 0
    except ValueError:
        return 1
    except getopt.GetoptError as err:
        print str(err)
        return 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
