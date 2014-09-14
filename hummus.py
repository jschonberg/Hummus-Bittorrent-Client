import datetime
import logging
from manager import Manager
from threading import Thread

if __name__ == '__main__':
    GREETING = "<--Welcome to the Hummus Bittorrent client!-->\n"
    TORRENT_PATH_MSG = "Please enter the path(s) of torrent file(s): "
    DEST_PATH_MSG = "Please enter the path of where you would " \
                    "like to save this torrent: "

    logging.info("Hummus started at " + str(datetime.datetime.now()))
    print GREETING
    torrent_paths = raw_input(TORRENT_PATH_MSG).split()
    print ""
    dest_path = raw_input(DEST_PATH_MSG)
    print ""

    managers = []
    threads = []

    for path in torrent_paths:
        m = Manager(path, dest_path)
        t = Thread(target=m.start)
        managers.append(m)
        threads.append(t)
        t.start()
