import logging
import socket
import utilities

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
    def die():
        with self._alive_lock:
            self._alive = False

    def isAlive():
        with self._alive_lock:
            return self._alive

    def stayConnected():
        """
        Return True if last msg received from peer was <=2min ago
        Return false otherwise
        """
        #TODO:Rename this and should be called by manager
        pass

    def execute(self):
        if self.sock is None: 
            #initiator peer (from manager). connect to peer and shake hands.
            self.sock = utilities.connectToPeer()
            if self.sock is None:
                #Could not create a connection, kill this peer
                self.die()
                print "Error: couldn't connect to peer"
                return None

            assert (self._ip_address, self._port) == self.sock.getpeername()

            self.shakeHands()
            if self.isAlive() is False or self._shaken_hands is False:
                return None

        #Send bitfield message
   
   #LOOP
        #Send unchoke message if they're choked

        #Send have messages for all peices I have

        #Go through all pieces they told us they have, send a request for all the ones we still need




        #Send a keep alive message
    #----
    #Networking Functions
    #----
    def send(self, bytes):
        """
        Send entirety of bytes to remote peer
        Raises RuntimeError if socket connection is broken
        """
        total_sent = 0
        while total_sent < len(bytes):
            sent = self.sock(byes[total_sent:])
            if sent == 0:
                raise RuntimeError("Error: socket connect to peer:" + self._peer_id + " broken")
            total_sent = total_sent + sent


    def recv(self, length=BLOCK_SIZE):
        """
        Get length bytes from Peer
        Returns bytestring. Raises RuntimeError if connection is broken
        """

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
        """
        len(bytes) must == 5. 
        Parse and return (msg_length, msg_id)
        pass
        """
    def shakeHands(self):
        # Sketch of steps (jake)

        # Contruct the handshake
        handshake_to_send = utilities.constructHandshake(self.manager.getInfoHash(), !!!SELF_PEER_ID!!!!! )

        # send the handshake
        self.send(handshake_to_send)

        # receive the first byte of the response, make sure its an int of value 19
        data = struct.unpack('>i',self.recv(1))
        if data is not 19:
            self.die()
            logging.error("Ill-formed handshake response from peer.")
            return None

        # receive the rest of the handshake (67 bytes)
        data = struct.pack('>i', 19)
        data.append(self.recv(67))

        # parse response
        handshake_response = utilities.parseHandshake(data)
        if handshake_response is None:
            self.die()
            logging.error("Handshake response is invalid.")
            return None

        # verify response
        if handshake_response[0] != self.manager.getInfoHash():
            self.die()
            logging.error("Could not complete handshake. Info hash from peer does not match.")
            return None
        if handshake_response[1] != self._peer_id:
            self.die()
            logging.error("Could not complete handshake. Peer ID does not match.")
            return None

        self._shaken_hands = True

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