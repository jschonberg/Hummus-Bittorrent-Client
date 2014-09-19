import sys
from manager import Manager
from threading import Thread

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "You need a torrent file and destination path to run Hummus"
        exit(1)

    torrent_paths = [sys.argv[1]]
    dest_path = sys.argv[2]
    GREETING = "<--Welcome to the Hummus Bittorrent client!-->\n"
    print GREETING

    managers = []
    threads = []

    for path in torrent_paths:
        m = Manager(path, dest_path)
        t = Thread(target=m.execute)
        t.daemon = True
        managers.append(m)
        threads.append(t)
        # t.start()
        m.execute()

    while True:
        #TODO: What is the main program exit condition?
        pass
