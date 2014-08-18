import logging
import socket
import time
import utilities

class Peer(object):
    #----
    #MSGID Constants
    #----
    KEEPALIVE_MSGID = -1
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
        self._shaken_hands = False if sock == None else True
        self._dataBuffer = []
        self._last_msg_time = None
        self._peer_id = peer_id #Unique id from tracker for remote peer
        self._ip_address = ip_address
        self._port = port
        self._pieces_peer_has = set()
        self._pending_requests = {} #{piece_index : [true/false]*num_blocks_per_piece}
        self._actively_held_pieces = set() #piece_indices of pieces we have marked as active in master record

        self._am_choking = True
        self._am_interested = False
        self._peer_choking = True
        self._peer_interested = False

        self._recv_dispatch = {
            KEEPALIVE_MSGID : recvKeepAlive,
            CHOKE_MSGID : recvChoke,
            UNCHOKE_MSGID : recvUnchoke,
            INTERESTED_MSGID : recvInterested,
            NOTINTERESTED_MSGID : recvNotInterested,
            HAVE_MSGID : recvHave,
            BITFIELD_MSGID : recvBitfield,
            REQUEST_MSGID : recvRequest,
            PIECE_MSGID : recvPiece,
        }

        self.manager = manager #Reference to manager managing this peer
        self.sock = sock


    def __del__(self):
        #close the socket
        #make sure all pieces that are active with this peer are marked as inactive
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

    def isKeepAliveMsg(chunk):
        (data,) = struct.unpack('>i', chunk)
        return data == 0

    def stayConnected():
        """
        Return True if last msg received from peer was <=2min ago
        Return false otherwise
        """
        #TODO:Rename this and should be called by manager
        pass

    def interestedInPeer():
        """
        Return True if this Peer has at least one piece that we need
        Return False otherwise
        """
        for piece_id in self._pieces_peer_has:
            if manager.master_record.isPieceNeeded(piece_id):
                return True
        return False

    def execute(self):
        if self.sock == None: 
            #initiator peer (from manager). connect to peer and shake hands.
            self.sock = utilities.connectToPeer()
            if self.sock == None:
                #Could not create a connection, kill this peer
                self.die()
                logging.error("Couldn't connect to peer")
                return None

            assert (self._ip_address, self._port) == self.sock.getpeername()

            self.shakeHands()
            if self.isAlive() == False or self._shaken_hands == False:
                self.die()
                logging.error("Couldn't shake hands")
                return None

        self.sock.settimeout(3)
        self.sendBitfield()
        
        while True:
            #Unchoke them
            if(self._am_choking): self.sendUnchoke()

            #Send them what pieces we have
            if(self._peer_interested): self.sendHaveMsgs()

            #Determine if we're interested. Update peer if interest state changes
            if self.interestedInPeer():
                if not self._am_interested:
                    self.sendInterested()
                    self._am_interested = True
            else:
                if self._am_interested:
                    self.sendNotInterested()
                    self._am_interested = False

            #Send out requests for needed blocks
            if not self._peer_choking and self._am_interested:
                self.sendRequestMsgs()

            try:
                max_msgs = 50
                for x in range(max_msgs):
                    chunk = self.recv(4)
                    if isKeepAliveMsg(chunk):
                        self._recv_dispatch[KEEPALIVE_MSGID]()
                    else:
                        chunk += self.recv(1)
                        (msg_id,msg_length) = self.parseMsgType(chunk)
                        self._recv_dispatch[msg_id](msg_length)
            except timeout:
                logging.info("Peer timed out")
            except HummusError as e:
                self.die()
                logging.error(str(e))
                return None

            #Send a keep alive message
            if self.isAlive(): self.sendKeepAlive()

    #----
    #Networking Functions
    #----
    def send(self, bytes):
        """
        Send entirety of bytes to remote peer
        Raises HummusError if socket connection is broken
        """
        total_sent = 0
        while total_sent < len(bytes):
            sent = self.sock(byes[total_sent:])
            if sent == 0:
                raise HummusError("Error: socket connect to peer:" + self._peer_id + " broken")
            total_sent = total_sent + sent


    def recv(self, length=BLOCK_SIZE):
        """
        Get length bytes from Peer
        Returns bytestring of len length. Raises HummusError if connection is broken
        """

        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self.sock.recv(min(length - bytes_recd, 2048))
            if chunk == '':
                raise HummusError("Error: could not receive data from peer:" + self._peer_id + ". Socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        return ''.join(chunks)

    #----
    #Messaging Functions
    #----
    def parseMsgType(self, bytes):
        """
        Parse and return (msg_id,msg_length)
        Throws HummusError if can't determine valid message type or length is nonsensical
        """
        assert len(bytes) == 5
        pass

    def shakeHands(self):
        # Contruct the handshake
        handshake_to_send = utilities.constructHandshake(self.manager.getInfoHash(), !!!utilities.SELF_PEER_ID!!!!! )

        # send the handshake
        try:
            self.send(handshake_to_send)
        except HummusError as e:
            self.die()
            logging.error(str(e))
            return None

        # receive the first byte of the response, make sure its an int of value 19
        try:
            (data,) = struct.unpack('>B',self.recv(1))
        except HummusError as e:
            self.die()
            logging.error(str(e))
            return None

        if data != 19:
            self.die()
            logging.error("Ill-formed handshake response from peer.")
            return None

        # receive the rest of the handshake (67 bytes)
        data = struct.pack('>B', 19)
        try:
            data.append(self.recv(67))
        except HummusError as e:
            self.die()
            logging.error(str(e))
            return None

        # parse response
        handshake_response = utilities.parseHandshake(data)
        if handshake_response == None:
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

#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
#check my choking and interested state and vice versa in the following functions
    #====Sending messages
    def sendKeepAlive(self):
        pass
    def sendChoke(self):
        pass
    def sendUnchoke(self):
        pass
    def sendInterested(self):
        pass
    def sendNotInterested(self):
        pass
    def sendHaveMsgs(self):
        #Send a have message for every piece we have completed
        # completed_pieces = manager.master_record.getCompletedPieces()
        # for piece_id in completed_pieces:
        #     self.sendHave(piece_id) <--construct message, send it
        pass
    def sendBitfield(self):
        pass
    def sendRequestMsgs(self):
        #For every piece that the peer has that we need
        #so long as we have <20 pending requests and there are still pieces needed that HAVE NOT been requested already
        #make sure to only request blocks from pieces that are not active in master_record or are actively held by us
        #mark piece as active in master_record before sending request
        #if we mark as active in master record, make sure to add to our actively held pieces set
        #mark new request in self._pending_requests dict
        pass
    def sendPiece(self):
        pass        


    #====Receiving messages
    def recvKeepAlive(self):
        """"keep-alive: <len=0000>"""
        self._last_msg_time = time.time()

    def recvChoke(self, length=None):
        """choke: <len=0001><id=0>"""
        self._peer_choking = True

    def recvUnchoke(self, length=None):
        """unchoke: <len=0001><id=1>"""
        self._peer_choking = False

    def recvInterested(self, length=None):
        """interested: <len=0001><id=2>"""
        self._peer_interested = True

    def recvNotInterested(self, length=None):
        """not interested: <len=0001><id=3>"""
        self._peer_interested = False

    def recvHave(self, length=None):
        """have: <len=0005><id=4><piece index>"""
        if length != 5:
            raise HummusError("\"Have\" message does not have the proper length")

        chunk = self.recv(4)
        (piece_index,) = struct.unpack('>i',chunk)
        assert piece_index >= 0
        assert piece_index < self.master_record.numPieces()
        self._pieces_peer_has.add(piece_index)


    def recvBitfield(self, length):
        pass
    def recvRequest(self, length=None):
        pass
    def recvPiece(self, length):
        pass