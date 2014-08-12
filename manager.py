class Manager(object):
    #----
    #Constants
    #----
    SELF_PEER_ID = #TODO, generate a unique peerid for this client

    #----
    #Class Functions
    #----
    def __init__(self, torrent_path, dest_path, record_registry):
        #torrent_path: string to absolute file path of .torrent metainfo file
        #dest_path: string with absolute path of where to save downloaded data
        #record_registry: Queue of active managers

        self.TORRENT_PATH = torrent_path #TODO: Do we need this?
        self.DEST_PATH = dest_path

        self.torrent_file = self.parseMetainfoFile(torrent_path)
        self.master_record = MasterRecord(self, self.torrent_file, self.DEST_PATH)
        self._active_peers = [] #Queue of active Peer() objects
        self._tracker_response = {}

        record_registry.put(self) 
    def __del__(self):
    def __enter__(self):
    def __exit__(self, type, value, traceback):

    #----
    #Utility Functions
    #----
    def parseMetainfoFile(torrent_path):
        """
        Takes in a path to a .torrent file, parses the bencoded data, and returns a properly formatted dictionary
        """
    def createTrackerRequest(self):
        """
        Returns string which is the GET request to the tracker
        """
    def parseTrackerResponse(raw_request):
        """
        Parses raw_request and fills out self._tracker_response
        """
    def peerCleanup(self):
        """
        Goes through self._active_peers and removes any dead peers
        """

    #----
    #Operational Functions
    #----
    def execute(self):
    def contactTracker(self):
        """
        Formulate request, send request, parse response
        """
    def finishDownload(self):
        """
        Final cleanup on download, including rendering individual files from bytestream
        """
    def createPeer(self, ip_address, port, socket=None):
        """
        Create a new peer, add it to _active_peers, and start its execution
        """
        #TODO return values, errors thrown, etc…
    def getInfoHash():
        """
        Return info_hash for this torrent
        """
