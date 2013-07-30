xiami_player
============

用Python在mini2440做了个虾米音乐播放程序，可以播放专辑和一些网络电台音乐，所有操作通过无线鼠标控制（mouse_data_capture转鼠标数据为字符)。

运行：

    ./mouse_capture | ./radio.py -c channel.txt -l list_ids.txt

本程序用到了[mouse_capture](https://github.com/lbzhung/mouse_data_capture)。
