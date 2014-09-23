import bitstring
import logging
import math
import socket
import struct
import time
import sys
import utilities
from utilities import BLOCKSIZE, HummusError, KILOBYTE
from threading import Lock
# from pudb import set_trace

NEEDED = 0
REQUESTED = 1
DOWNLOADED = 2


class PeerError(HummusError):
    pass


class Peer(object):
    """TODO"""

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
    VALID_IDS = range(-1, 10)
    MAX_PENDING = 20  # By convention, <20 requests at a time

    def __init__(self, manager, ip_address, port, sock=None):
        print "__init__", manager, ip_address, port, sock  # TESTING
        self._alive_lock = Lock()
        with self._alive_lock:
            self._alive = True
        self._sock = sock
        self._ip_address = ip_address
        self._port = port
        self.manager = manager
        self.ID = str(ip_address) + str(port)

        self._pieces_remote_serves = set()

        self._am_choking = True
        self._am_interested = False
        self._peer_choking = True
        self._peer_interested = False

        self._pending_requests = []
        for i in xrange(self.manager.num_pieces):
            self._pending_requests.append([NEEDED] *
                                          self.manager.numBlocks(i))

    def __del__(self):
        print "__del__"  # Testing
        self.die()
        if self._sock:
            self._sock.close()

    def die(self, message=None):
        """Log error message and kill this peer. Thread safe."""
        print "die()", message  # Testing
        if message:
            print "DIE: " + message
        with self._alive_lock:
            self._alive = False

    def _interestedInPeer(self):
        """Return True if remote has at least one piece that we need"""
        print "_interestedInPeer"
        for piece in self._pieces_remote_serves:
            if (self.manager.pieceStatus(piece) == "free" or
                    self.manager.pieceStatus(piece) == self.ID):
                return True
        return False

    def _getNumPendingRequests(self):
        """Return the number of unfulfilled data requests sent to remote."""
        print "_getNumPendingRequests"
        count = 0
        for pending_blocks in self._pending_requests:
            count += sum([x for x in pending_blocks if x == REQUESTED])
        return count

    def _connectAndShake(self):
        """If necessary, open connection with remote and shake hands.

        Raises:
          PeerError if can't connect or can't shake hands

        """
        print "_connectAndShake"
        if self._sock:
            self._shaken_hands = True
            return
        else:
            self._sock = utilities.connectToPeer(self._ip_address,
                                                 self._port)
            if not self._sock:
                raise PeerError("Could not connect to peer")
            self.shakeHands()

    def execute(self):
        """Open connection with remote and download/upload data with them."""
        print "execute"

        self._recv_dispatch = {
            self.CHOKE_MSGID: self.recvChoke,
            self.UNCHOKE_MSGID: self.recvUnchoke,
            self.INTERESTED_MSGID: self.recvInterested,
            self.NOTINTERESTED_MSGID: self.recvNotInterested,
            self.HAVE_MSGID: self.recvHave,
            self.BITFIELD_MSGID: self.recvBitfield,
            self.REQUEST_MSGID: self.recvRequest,
            self.PIECE_MSGID: self.recvPiece,
        }

        try:
            self._connectAndShake()
        except PeerError as e:
            self.die("PE: " + str(e))
            return
        self._sock.settimeout(3)
        self.sendBitfield()

        while self.isAlive():
            try:
                self.sendHaveMsgs()

                if self._am_choking:
                    self.sendUnchoke()
                    self._am_choking = False

                if self._interestedInPeer():
                    if not self._am_interested:
                        self.sendInterested()
                        self._am_interested = True
                else:
                    if self._am_interested:
                        self.sendNotInterested()
                        self._am_interested = False

                if not self._peer_choking and self._am_interested:
                    self.sendRequestMsgs()

                chunk = self.recv(4)
                if self.isKeepAliveMsg(chunk):
                    self.recvKeepAlive()
                else:
                    chunk += self.recv(1)
                    (msg_id, msg_length) = self.parseMsgType(chunk)
                    self._recv_dispatch[msg_id](msg_length)
            except socket.timeout as e:
                print "Peer timed out"
                self.die("PE:" + str(e))
                return
            except HummusError as e:
                self.die("PE:" + str(e))
                return

            # if self.isAlive():
            #     self.sendKeepAlive()

    def send(self, data):
        """Send entirety of data to remote peer.

        Raises:
          PeerError if socket connection is broken

        """
        print "send", repr(data)
        total_sent = 0
        while total_sent < len(data):
            sent = self._sock.send(data[total_sent:])
            if sent == 0:
                raise PeerError("".join(["Error: socket connect to peer: ",
                                self._peer_id, " broken"]))
            total_sent = total_sent + sent

    def recv(self, length=BLOCKSIZE):
        """Get length bytes from Peer.

        Args:
          length (int): Number of bytes to receive
        Returns:
          bytestring of len length.

        Raises:
          PeerError if connection is broken

        """
        sys.stderr.write("Downloading " + str(length) + " bytes")
        chunks = []
        bytes_recd = 0
        while bytes_recd < length:
            chunk = self._sock.recv(min(length - bytes_recd, 2048))
            if chunk == '':
                raise PeerError("".join(["Socket connection with ",
                                self._peer_id, " broken."]))
            chunks += chunk
            bytes_recd = bytes_recd + len(chunk)
        print ""
        return ''.join(chunks)

    def parseMsgType(self, data):
        """Parse data and return (msg_id, msg_length)

        Raises:
          PeerError if invalid message type or length

        """
        print "parseMsgType", repr(data)
        if len(data) != 5:
            raise PeerError("Message length more than 5 bytes.")
        (msg_length, msg_id) = struct.unpack('>IB', data)
        if msg_id not in self.VALID_IDS:
            raise PeerError("MSG ID not a valid ID number")
        return (msg_id, msg_length)

    def shakeHands(self):
        """Initiate a handshake with remote, parse and validate response

        Sets:
          _peer_id to remote ID on SUCCESS
          _shaken_hands to True on SUCCESS

        Raises:
          PeerError if handshake response is invalid or nonexistant

        """
        print "shakeHands"
        initiate = utilities.constructHandshake(self.manager.info_hash,
                                                utilities.SELF_PEER_ID)
        self.send(initiate)
        data = self.recv(68)
        response = utilities.parseHandshake(data)
        if not response:
            raise PeerError("Handshake response is invalid.")
        if response[0] != self.manager.info_hash:
            raise PeerError("Received Info hash doesn't match in handshake.")
        self._peer_id = response[1]
        self._shaken_hands = True
        print ">>SUCCESSFULLY SHOOK HANDS!!!<<"

    def isAlive(self):
        """Return whether this peer is alive. Thread safe."""
        print "isAlive"
        with self._alive_lock:
            return self._alive

    def isKeepAliveMsg(self, chunk):
        """Return true if chunk binary data is a keep alive message."""
        print "isKeepAliveMsg", chunk
        if len(chunk) != 4:
            return False
        (data,) = struct.unpack('>I', chunk)
        return data == 0

    def sendKeepAlive(self):
        """Pack and send keep-alive: <len=0000>"""
        print "sendKeepAlive"
        chunk = struct.pack('>I', 0)
        self.send(chunk)

    def sendChoke(self):
        """Pack and send choke: <len=0001><id=0>"""
        print "sendChoke"
        chunk = struct.pack('>IB', 1, 0)
        self.send(chunk)

    def sendUnchoke(self):
        """Pack and send unchoke: <len=0001><id=1>"""
        print "sendUnchoke"
        chunk = struct.pack('>IB', 1, 1)
        self.send(chunk)

    def sendInterested(self):
        """Pack and send interested: <len=0001><id=2>"""
        print "sendInterested"
        chunk = struct.pack('>IB', 1, 2)
        self.send(chunk)

    def sendNotInterested(self):
        """Pack and send not interested: <len=0001><id=3>"""
        print "sendNotInterested"
        chunk = struct.pack('>IB', 1, 3)
        self.send(chunk)

    def sendHaveMsgs(self):
        """For each piece downloaded, send a have message to remote."""
        print "sendHaveMsgs"
        completed_pieces = self.manager.getCompletedPieces()
        for piece_id in completed_pieces:
            self.sendHave(piece_id)

    def sendHave(self, piece_id):
        """Pack and send have: <len=0005><id=4><piece index>"""
        print "sendHave", piece_id
        chunk = struct.pack('>IBI', 5, 4, piece_id)
        self.send(chunk)

    def sendBitfield(self):
        """Pack and send bitfield: <len=0001+X><id=5><bitfield>"""
        print "sendBitfield"
        bits = bitstring.BitArray(self.manager.num_pieces)
        for index in self.manager.getCompletedPieces():
            bits[index] = True
        chunk = struct.pack('>IB', len(bits.tobytes()) + 1, 5)
        chunk += bits.tobytes()
        self.send(chunk)

    def sendPiece(self, index, begin, block):
        """Pack and send piece: <len=0009+X><id=7><index><begin><block>"""
        print "sendPiece", index, begin, block
        msg = struct.pack('>IB2I', 9 + len(block), 7, index, begin)
        chunk = msg + block
        self.send(chunk)

    def _neededBlocks(self, piece):
        """Return list of needed block indices in piece"""
        print "_neededBlocks", piece
        needed = []
        for i, state in enumerate(self._pending_requests[piece]):
            if state == NEEDED:
                needed.append(i)
        return needed

    def _getNewRequests(self):
        """Return an appropriately sized list of request to be made.

        Will prioritize making requests for pieces already held first before
        generating requests for new pieces. Will pieces ensure requests for
        new pieces are activel held with Manager.

        Returns:
          list(tuple(piece id, block id)) for each request that should be
          sent to remote. Will be of length such that pending requests +
          these new requests <= MAX_PENDING allowed requests.

        """
        print "_getNewRequests"
        new_reqs = []
        num_needed = self.MAX_PENDING - self._getNumPendingRequests()

        # Enqueue requests for blocks in pieces we already hold
        for p in self.manager.activelyHeldPieces(self):
            new_reqs += [(p, x) for x in self._neededBlocks(p)]

        # If needed, enqueue requests for blocks in a new piece
        while num_needed - len(new_reqs) > 0:
            possibles = set.intersection(self.manager.getNeededPieces(),
                                         self._pieces_remote_serves)
            if len(possibles) == 0:
                break
            new_piece = possibles.pop()
            success = self.manager.makeActive(self, new_piece)
            if not success:
                raise PeerError("Could not make piece active.")
            new_reqs.extend((new_piece, x) for x in
                            self._neededBlocks(new_piece))
        return new_reqs[:self.MAX_PENDING]

    def sendRequestMsg(self, index, begin, length):
        """Pack and send request: <len=0013><id=6><index><begin><length>"""
        print "sendRequestMsg", index, begin, length
        chunk = struct.pack('>IB3I', 13, 6, index, begin, length)
        self.send(chunk)

    def sendRequestMsgs(self):
        """Send requests for more blocks, if pending reqs < MAX_PENDING"""
        print "sendRequestMsgs"
        new_reqs = self._getNewRequests()
        for req in new_reqs:
            piece = req[0]
            block = req[1]
            print "BYTESINBLOCK: ", self.manager.bytesInBlock(piece, block)
            chunk = struct.pack('>IB3I', 13, 6, piece, block * BLOCKSIZE,
                                self.manager.bytesInBlock(piece, block))
            self.send(chunk)
            self._pending_requests[piece][block] = REQUESTED

    def recvKeepAlive(self):
        """"keep-alive: <len=0000>"""
        print "recvKeepAlive"
        # TODO: self._last_msg_time = time.time()
        pass

    def recvChoke(self, length=None):
        """Set peer choking to True."""
        print "recvChoke"
        self._peer_choking = True

    def recvUnchoke(self, length=None):
        """Set peer choking to false."""
        print "recvUnchoke"
        self._peer_choking = False

    def recvInterested(self, length=None):
        """Set peer interested to true"""
        print "recvInterested"
        self._peer_interested = True

    def recvNotInterested(self, length=None):
        """Set peer interested to false"""
        print "recvNotInterested"
        self._peer_interested = False

    def recvHave(self, length=None):
        """Mark piece as data remote has to serve.

        Raises:
          PeerError if have message is illformed or for index out of range.

        """
        print "recvHave"
        if length != 5:
            raise PeerError("\"Have\" message is not length 5.")

        chunk = self.recv(4)
        (piece_index,) = struct.unpack('>I', chunk)
        if piece_index >= self.manager.num_pieces:
            raise PeerError("\"Have\" message index is out of range.")
        self._pieces_remote_serves.add(piece_index)

    def recvBitfield(self, length):
        """Parse bitfield and mark pieces as data remote has to serve."""
        print "recvBitfield", length

        chunk = self.recv(length - 1)
        bits = bitstring.BitArray(hex=chunk.encode('hex'))
        for index, bit in enumerate(bits):
            if bit:
                self._pieces_remote_serves.add(index)

    def recvRequest(self, length=None):
        """Receive request for data and send data to remote.

        If remote requests data off the end of the file, will return data up
        to the end of the file

        Spec:
          request: <len=0013><id=6><index><begin><length>

        Raises:
          PeerError if request is malformed or we don't have requested piece.
        """
        print "recvRequest", length
        if length != 13:
            raise PeerError("\"Request\" length is not 13.")

        chunk = self.recv(12)
        (index, begin_byte, byte_length) = struct.unpack('>3I')

        # Validation
        if self._am_choking:
            print "Ignoring Request due to choking."
            return
        if not self._peer_interested:
            raise PeerError("Remote requesting data but is marked as not "
                            "interested.")
        if index not in self.manager.getCompletedPieces():
            raise PeerError("Don't have piece requested by remote.")
        if index >= self.manager.num_pieces:
            raise PeerError("Index from Request is greater than number of "
                            "pieces")

        # Send data requested to remote
        chunk = self.manager.readData(index, begin_byte, byte_length)
        assert length(chunk) == byte_length
        self.sendPiece(index, begin_byte, byte_length, chunk)

    def recvPiece(self, length):
        """Receive and save data from remote.

        Spec:
          piece: <len=0009+X><id=7><index><begin><block>

        Raises:
          PeerError if remote sends none or illformed data
        """
        print "recvPiece", length
        if length <= 9:
            raise PeerError("Remote did not send any file data.")
        chunk = self.recv(length - 1)
        encoding = '>2I%ss' % str(length - 9)
        (index, offset, data) = struct.unpack(encoding, chunk)

        if not self._am_interested:
            print "Ignoring piece %s message because uninterested" % index
            return

        self.manager.saveData(index, offset, data)
        begin_byte = self.manager.piece_len * index + offset
        blocks = self.manager.blocksEncompassed(begin_byte, len(data))
        for piece, block in blocks:
            self._pending_requests[piece][block] = DOWNLOADED
