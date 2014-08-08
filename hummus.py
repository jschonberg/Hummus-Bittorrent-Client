import math
import io
import os

def listen(port, manager):
    "Start listening for incomming connections on port"
    "If a connection request comes in, ceate a socket ask manager to create responder Peer to manage"
    "Should be executed on it's own thread or will block program execution"
    #TODO: I think this function needs to be able,generate peers, and then parse the handshake, so that it knows which manager to add this peer to?? Then it needs to hand the peer off to the manager in question
    #TODO: Once we connect to a peer, will future messages from them get routed to the right socket or will it battle with the .listen() method happening here? In other words is recieving specifically different than listening?

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

        self.torrent_file = self.decodeMetainfoFile(torrent_path)
        self.master_record = MasterRecord(self, self.torrent_file, self.DEST_PATH)
        self._active_peers = [] #List of Peer() objects
        self._tracker_response = {}

        record_registry.put(self) 
    def __del__(self):
    def __enter__(self):
    def __exit__(self, type, value, traceback):

    #----
    #Utility Functions
    #----
    def decodeMetainfoFile(torrent_path):
        "Takes in a path to a .torrent file, parses the bencoded data, and returns a properly formated dictionary"
    def parseTrackerResponse(raw_request):
        "Parses raw_request and fills out self._tracker_response"
    def peerCleanup(self):
        "Goes through self._active_peers and removes any dead peers"

    #----
    #Operational Functions
    #----
    def execute(self):
    def contactTracker(self):
        "Formulate request, send request, parse response"
    def createTrackerRequest(self):
        "Returns string which is the GET request to the tracker"
    def finishDownload(self):
        "Final cleanup on download, including rendering individual files from bytestream"
    def createPeer(self, ip_address, port, socket=None):
        "Create a new peer, add it to _active_peers, and start its execution"
        #TODO return values, errors thrown, etc…
    def managePeer(peer):
        "Begin managing peer, add to active peers queue, etc…"
    def getInfoHash():
        "Return info_hash for this torrent"

class MasterRecord(object):
    BLOCK_SIZE = 16384 #16KB

    #----
    #Class Functions
    #----
    def __init__(self, manager, torrent_file, dest_path):
        self.manager = manager
        self.torrent_file = torrent_file

        #For each peice create a record entry to track the state of download for that data
        #status can be "needed", "active" or "complete"
        #blocks[index] contains staged, but not yet written bytes
        blocks = [bytearray()] * math.ceil(piece_length / BLOCK_SIZE) #Staged block data to be written to disk
        self._statusRecord = [{"satus" : "needed",
                              "blocks" : blocks }] * self.torrent_file.pieces 
        self._byteFile = self.openFile()
    def __del__(self):
    def __enter__(self):
    def __exit__(self, type, value, traceback):

    #----
    #Utility Functions
    #----
    def openFile(self):
        "Open a file at self.dest_path to download to."
        "If file already exists then evaluate validity with SHA1 hash and initialize record"
        "Return io.BufferedRWPair" #TODO what are errors thrown and other return values?
    def setPieceStatus(self, piece_index, new_status):
        "Set status of piece at piece_index to have new_status"
    def getPieceStatus(self, piece_index):
        "Return status of piece at piece_index"

    #----
    #Operational Functions
    #----
    def isPieceNeeded(self, piece_index):
        "Returns True if this piece is needed, False otherwise"
    def getNeededPieces(self):
        "Returns a list of piece_indices that are still needed"
    def isPieceCompleted(self, piece_index):
        "Returns True if this piece is completed, false otherwise"
    def getCompletedPieces(self):
        "Returns a list of piece_indices that have been completed"
    def isPieceActive(self, piece_index):
        "Returns True if this piece is active, false otherwise"
    def getActivePieces(self):
        "Returns a list of piece_indices that are active"
    def saveData(self, piece_index, begin_offset, bytes):
        "Write bytes data to byteFile. bytes should be an immutable python bytes object"
        "Only save data to disk if all blocks for this piece have now been downloaded"
        "If write to disk was successful and all blocks in this peice have been written, update piece status in record, clear out staged blocks from memory"
        #TODO: Which errors are thrown and what are return values?
    def readData(self, piece_index, begin_offset, length):
        "Read length bytes from byteFile beginning from piece at piece_index and data starting at begin_offset"
        #TODO: Which errors are thrown and what are return values?


class Peer(object):
    #----
    #MSGID Constants
    #----
    KEEPALIVE_MSGID = None
    CHOKE_MSGID = 0
    UNCHOKE_MSGID = 1
    INTERESTED_MSGID = 2
    NOTINTERESTED_MSGID = 3
    HAVE_MSGID = 4
    BITFIELD_MSGID = 5
    REQUEST_MSGID = 6
    PIECE_MSGID = 7
    CANCEL_MSGID = 8
    PORT_MSGID = 9

    #----
    #Class Functions
    #----
    def __init__(self, master_record, peer_id, manager, sock=None):
        self.stay_alive = True
        self.shaken_hands = False
        self.dataBuffer = []
        self.master_record = master_record
        self.sock = sock
        self.last_msg_time = None
        self.peer_id = peer_id #Unique id from tracker for remote peer
        self.manager = manager #Reference to manager managing this peer

        self.am_choking = True
        self.am_interested = False
        self.peer_choking = True
        self.peer_interested = False
    def __del__(self):
    def __enter__(self):
    def __exit__(self, type, value, traceback):
        #TODO: make sure sockets are closed, don't kill thread/peer until socket is closed!

    #----
    #Utility Functions
    #----
    def stayConnected():
        "Return True if last msg received from peer was <=2min ago"
        "Return false otherwise"

    def execute(self, ip_address=None, port=None):
        #TODO: Return reason for dying when stay_alive becomes false?

        if self.sock is not None: #Is a responder peer

        else: #Is an initator peer

        while(self.stay_alive):
            #Start sending and receiving messages with remote peer
            #TODO: What is the logic here? Alternate between sending messages/requests, and parsing messages/requests from peer? Alternative is some kind of action Queue and have the two things work in parallel. That sounds complicated though…

            #First step of receiving is to just recieve enough data to know the length and message type of incomming, then pass along to proper message function to self.recv rest


    #----
    #Networking Functions
    #----
    def connectToPeer(self):
        "Open a socket connection with peer"

    #TODO: Look at http://bit.ly/1uwLX2O for ex on how to do send,recv
    def send(self, bytes):
        "Send entirety of bytes to remote peer"
        #TODO: Return values and exceptions thrown?
        #TODO: NOte, we'll need to loop until completely sent, as networking spec doesn't guaruntee this on each send call

    def recv(self, length):
        "Get length bytes from Peer, append to self.dataBuffer"
        #TODO: Error handling, dead peers, return types, etc…

    #----
    #Messaging Functions
    #----
    def parseMsgType(self, bytes):
        "len(bytes) must == 5. "
        "Parse and return (msg_length, msg_id)"
    def sendHandshake(self):
    def recvHandshake(self,bytes):
    def sendKeepAlive(self):
    def recvKeepAlive(self):
    def sendChoke(self):
    def recvChoke(self):
    def sendUnchoke(self):
    def recvUnchoke(self):
    def sendInterested(self):
    def recvInterested(self):
    def sendNotInterested(self):
    def recvNotInterested(self):
    def sendHave(self):
    def recvHave(self,bytes):
    def sendBitfield(self):
    def recvBitfield(self, length, bytes):
    def sendRequest(self):
    def recvRequest(self,bytes):
    def sendPiece(self):
    def recvPiece(self, length, bytes):
    def sendCancel(self):
    def recvCancel(self, bytes):
    def sendPort(self):
    def recvPort(self, bytes):

class View(object):
    #----
    #Class Functions
    #----
    def init(self, manager):

    #----
    #Printing Functions
    #----
    def printStatus():
        "Query Manager and print current program state to STD_OUT"





