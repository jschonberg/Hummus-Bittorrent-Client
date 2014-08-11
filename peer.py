import socket

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
    def __init__(self, peer_id, manager, sock=None):
        self._stay_alive = True
        self._shaken_hands = False
        self._dataBuffer = []
        self._last_msg_time = None
        self._peer_id = peer_id #Unique id from tracker for remote peer

        self._am_choking = True
        self._am_interested = False
        self._peer_choking = True
        self._peer_interested = False

        self.manager = manager #Reference to manager managing this peer
        self.sock = sock


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

    def execute(self):
        #TODO: Return reason for dying when stay_alive becomes false?

        if self.sock is not None: #Is a responder peer

        else: #Is an initator peer

        while(self._stay_alive):
            #Start sending and receiving messages with remote peer
            #TODO: What is the logic here? Alternate between sending messages/requests, and parsing messages/requests from peer? Alternative is some kind of action Queue and have the two things work in parallel. That sounds complicated though…

            #First step of receiving is to just receive enough data to know the length and message type of incomming, then pass along to proper message function to self.recv rest


    #----
    #Networking Functions
    #----
    def send(self, bytes):
        "Send entirety of bytes to remote peer"
        "Rasies RuntimeError if socket connection is broken"
        total_sent = 0
        while total_sent < len(bytes):
            sent = self.sock(byes[total_sent:])
            if sent == 0:
                raise RuntimeError("Error: socket connect to peer:" + self._peer_id + " broken")
            total_sent = total_sent + sent


    def recv(self, length=BLOCK_SIZE):
        "Get length bytes from Peer"
        "Returns bytestring. Raises RuntimeError if connection is broken"

        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.sock.recv(min(length - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("Error: could not receive data from peer:" + self._peer_id + ". Socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return ''.join(chunks)

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