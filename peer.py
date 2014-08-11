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
    def __init__(self, manager, peer_id, ip_address, port, sock=None):
        self._alive_lock = Lock()
        with self._alive_lock:
            self._alive = True
        self._shaken_hands = False if sock is None else True
        self._dataBuffer = []
        self._last_msg_time = None
        self._peer_id = peer_id #Unique id from tracker for remote peer
        self._ip_address = ip_address
        self._port = port

        self._am_choking = True
        self._am_interested = False
        self._peer_choking = True
        self._peer_interested = False

        self.manager = manager #Reference to manager managing this peer
        self.sock = sock


    def __del__(self):
        pass
    def __enter__(self):
        pass
    def __exit__(self, type, value, traceback):
        #TODO: make sure sockets are closed, don't kill thread/peer until socket is closed!
        pass

    #----
    #Utility Functions
    #----
    def isAlive():
        with self._alive_lock:
            return self._alive

    def stayConnected():
        "Return True if last msg received from peer was <=2min ago"
        "Return false otherwise"
        #TODO:Rename this and should be called by manager
        pass

    def execute(self):
        #TODO: Return reason for dying when alive becomes false?

        if self.sock is None: 
            #initiator peer (from manager)
            self.sock = utilities.connectToPeer()
            if self.sock is None:
                #Could not create a connection, kill this peer
                with self._alive_lock:
                    self._alive = False
                #TODO: Log cause of death
                return

            self.shakeHands() !!!


        assert self._shaken_hands is True
        assert (self._ip_address, self._port) == self.sock.getpeername()
        #Handshake done, move on…

        while(self._alive):
            #Start sending and receiving messages with remote peer
            #TODO: What is the logic here? Alternate between sending messages/requests, and parsing messages/requests from peer? Alternative is some kind of action Queue and have the two things work in parallel. That sounds complicated though…

            #First step of receiving is to just receive enough data to know the length and message type of incoming, then pass along to proper message function to self.recv rest
            # self.parseMsgType(self.recv(5))


    #----
    #Networking Functions
    #----
    def send(self, bytes):
        "Send entirety of bytes to remote peer"
        "Raises RuntimeError if socket connection is broken"
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
        pass
    def shakeHands(self):
        try:
            # self._shaken_hands = True
            pass
        except RuntimeError:
            pass
    def sendKeepAlive(self):
        pass
    def recvKeepAlive(self):
        pass
    def sendChoke(self):
        pass
    def recvChoke(self):
        pass
    def sendUnchoke(self):
        pass
    def recvUnchoke(self):
        pass
    def sendInterested(self):
        pass
    def recvInterested(self):
        pass
    def sendNotInterested(self):
        pass
    def recvNotInterested(self):
        pass
    def sendHave(self):
        pass
    def recvHave(self,bytes):
        pass
    def sendBitfield(self):
        pass
    def recvBitfield(self, length, bytes):
        pass
    def sendRequest(self):
        pass
    def recvRequest(self,bytes):
        pass
    def sendPiece(self):
        pass
    def recvPiece(self, length, bytes):
        pass
    def sendCancel(self):
        pass
    def recvCancel(self, bytes):
        pass
    def sendPort(self):
        pass
    def recvPort(self, bytes):
        pass