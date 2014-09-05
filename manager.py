import bencode
import Queue
import utilities
import socket
# import master_record

class Manager(object):
    #----
    #Constants
    #----
    SELF_PEER_ID = utilities.SELF_PEER_ID

    #----
    #Class Functions
    #----
    def __init__(self, torrent_path, dest_path):

        self.TORRENT_PATH = torrent_path
        self.DEST_PATH = dest_path
        self.info_dictionary = {}
        self._info_dictionary_tuple = () # Tuple form of info_dictionary, used when encoding/hashing required
        self._tracker_ip = None
        self._tracker_url = None
        # self.master_record = MasterRecord(self)
        self._active_peers = Queue.Queue()
        self._tracker_response = {}

    def __del__(self):
        #TODO
        #Send tracker "Stopped"
        pass

    #----
    #Utility Functions
    #----
    def die(self):

    def parseMetainfoFile(self):
        """
        Takes in a path to a .torrent file. Parses it and sets relevant class data members
        """
        f = open(self.TORRENT_PATH,'r')
        content = f.read()
        torrent = bencode.bdecode(content)

        tracker_url = torrent['announce']

        #TODO: Pull out IP addr and port for UDP tracker

        self.info_dictionary = torrent['info']
        assert self.info_dictionary

        torrent_tuple = bencode.bdecode(content,())
        for t in torrent_tuple:
            if t[0] == 'info':
                self._info_dictionary_tuple = t
        assert self._info_dictionary_tuple

    def pingTracker():
        """
        Sends a request to tracker. Receives response and updates
        Manager state accordingly
        """

    def peerCleanup(self):
        """
        Goes through self._active_peers and removes any dead peers
        """
        pass

    #----
    #Operational Functions
    #----
    def execute(self):
        #create a UDP socket to be used
        #send connect request to tracker
        #wait for and receive connect reply
        #verify reply
        #format and send annoucne request
        #get announce reply
            #verify reply
            #Get list of peers, store the peer list (ip,port) pairs in some data structure
        #handle error messages

        #TODO:send tracker "completed" if started <100% and now completely donwloaded
        pass

    def finishDownload(self):
        """
        Final cleanup on download, including rendering individual files from bytestream
        """
        pass
    def createPeer(self, ip_address, port, socket=None):
        """
        Create a new peer, add it to _active_peers, and start its execution
        """
        pass
        #TODO return values, errors thrown, etc
    def cleanupPeer(peer_obj):
        pass
    def getInfoHash():
        """
        Return info_hash for this torrent
        """
        pass

#For Testing==
if __name__ == '__main__':
    # m = Manager('./test.torrent','./')
    # m.parseMetainfoFile()
