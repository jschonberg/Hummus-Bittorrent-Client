import os
import requests
import urllib
import logging
import hashlib
import struct
import math
import ipgetter
import time
from peer import Peer
from bencode import bencode, bdecode
from utilities import HummusError, SELF_PEER_ID, BLOCKSIZE
from threading import Lock, Thread

# MY_IP_ADDRESS = '104.162.109.149'


class ManagerError(HummusError):
    pass


class FileWrapper(object):
    def __init__(self, f_path_name, f_len):
        if not os.path.isfile(f_path_name):
            # If the file didn't previously exists, create one
            with open(f_path_name, mode='wb'):
                pass
        self.f_obj = open(f_path_name, 'r+b')
        self.f_path_name = f_path_name
        self.f_len = f_len

    def __len__(self):
        return self.f_len


class Manager(object):

    """Communicate with tracker, create/remove peers, and manage file I/O.

    Attributes:
      piece_len (int): Number of bytes per piece. Set after parse of tracker
        response.
      total_size (int): Sum total size, in bytes, of all files to be served
      num_pieces (int): The total number of pieces
      File (namedtuple): ('file_obj, file_path_name, byte_len')
      MAX_PEERS (int): Maximum number of simoultaneous connections

    """
    PORT = 6889
    MAX_PEERS = 30

    def __init__(self, torrent_path, dest_path):
        """Make Manager ready to serve/download files.

        Contact the tracker. Parse and save tracker response.
        Initialize disk files to ready.

        Args:
          torrent_path (str): Absolute filepath to torrent file
          dest_path (str): Absolute path to save destination directory

        """
        self._alive_lock = Lock()
        with self._alive_lock:
            self._alive = True
        self._peers = []  # Holds Peer() objects
        self._torrent_path = torrent_path
        self._dest_path = os.path.abspath(dest_path)
        self._peer_id = SELF_PEER_ID
        self.info_hash = self._renderInfoHash()

        self._files = []
        self._files_lock = Lock()
        with open(self._torrent_path, mode='r') as f:
            metainfo = bdecode(f.read())
            self._tracker_url = metainfo['announce']
            self.piece_len = metainfo['info']['piece length']
            self._piece_hashes = metainfo['info']['pieces']
            self._initFiles(metainfo)

        self.total_size = sum(len(x) for x in self._files)
        print "TOTAL: ", self.total_size
        self.num_pieces = ((self.total_size / self.piece_len) +
                           (1 if self.total_size % self.piece_len != 0
                            else 0))
        self._bytes_left = self.total_size
        self._bytes_uploaded = 0
        self._bytes_downloaded = 0

        request = self._createTrackerReq(first_req=True)
        response = self._contactTracker(request, first_req=True)
        self._peer_addresses = self._parsePeers(response)
        self._interval = response['interval']
        self._min_interval = response['min interval']
        if 'tracker id' in response.keys():
            self._tracker_id = response['tracker id']

        self._pieces_ledger = ["free"] * self.num_pieces
        self._pieces_ledger_lock = Lock()
        self._pieces_data = []
        for p in xrange(self.num_pieces):
            self._pieces_data.extend([[None] * self.bytesInBlock(p, b) for
                                     b in xrange(self.numBlocks(p))])
        self._pieces_data_lock = Lock()

    def die(self, message=None):
        """Kill this Manager"""
        # TODO Send tracker "Stopped" Put in die()?
        if message:
            logging.error(message)
        with self._alive_lock:
            self._alive = False

    def isAlive(self):
        """Return whether this Manager is still alive"""
        with self._alive_lock:
            return self._alive

    def _createTrackerReq(self, first_req=False):
        """Create a properly formatted http tracker request.

        Args:
          first (bool): Is this the first request to this tracker?

        Returns:
          tracker_req (str): Tracker URL + params to call GET request on

        Raises:
          ManagerError if any required data to generate request is missing.

        """
        if ((not self.info_hash or not self._tracker_url
             or not self._peer_id or not self.PORT or not self._bytes_left)):
            raise ManagerError("Field for tracker request does not exist")

        tracker_params = {'info_hash': self.info_hash,
                          'peer_id': self._peer_id,
                          'port': self.PORT,
                          'uploaded': self._bytes_uploaded,
                          'downloaded': self._bytes_downloaded,
                          'left': self._bytes_left,
                          'event': "started" if first_req else ""
                          }
        if hasattr(self, '_tracker_id'):
            tracker_params['trackerid'] = self._tracker_id

        return "%s?%s" % (self._tracker_url, urllib.urlencode(tracker_params))

    def _contactTracker(self, request, first_req=False):
        """Make GET call to tracker and return response.

        Args:
          request (str): URL to a tracker with properly formatted params
          first_req (bool): True if this is the first request to this tracker

        Returns:
          response (dict): bdecoded tracker response in python dict form

        """
        r = requests.get(request)
        return bdecode(r.content)

    def _initFiles(self, metainfo):
        """Create and open files, as described in metainfo, for writing.

        Args:
          metainfo (dict): .torrent metainfo file properly parsed to dict

        Returns:
          Nothing

        Raises:
          ManagerError if multi or single file mode cannot be determined

        """

        if "files" in metainfo['info'].keys():  # Multiple file torrent
            for info in metainfo['info']["files"]:
                f_path_name = self._dest_path + "/".join(info['path'])
                f_len = info['length']
                self._files.append(FileWrapper(f_path_name, f_len))

        elif "length" in metainfo['info'].keys():  # Single file torrent
            f_path_name = '/'.join([self._dest_path,
                                   metainfo['info']['name']])
            f_len = metainfo['info']['length']
            self._files.append(FileWrapper(f_path_name, f_len))
        else:
            raise ManagerError("Cant determine single or multi file mode")

    def _startNewPeers(self):
        """Connect with new peers up until MAX_PEERS total connections"""
        for (ip_address, port) in self._peer_addresses:
                if len(self._peers) < self.MAX_PEERS:
                    p = Peer(self, ip_address, port)
                    t = Thread(target=p.execute)
                    self._peers.append(p)
                    print "MANAGER CREATING PEER: ", p.ID
                    # t.start()
                    p.execute()

    def execute(self):
        while self.isAlive():
            self._peers = [p for p in self._peers if not p.isAlive()]
            #TODO: For dead peers, don't just remove them but make sure their actively held pieces are marked as free
            self._startNewPeers()
            self._peer_addresses = self._update_peers()
            time.sleep(self._min_interval)
            #TODO: When do we kill the manager? When the file is done?

    def _update_peers(self):
        request = self._createTrackerReq()
        response = self._contactTracker(request)
        return self._parsePeers(response)

    def _renderInfoHash(self):
        """Return 20-byte SHA1 hash of the value of the info key from the
            Metainfo file.
        """
        with open(self._torrent_path, 'rb') as f:
            read_data = f.read()
        decoded = bdecode(read_data, ())
        info_dict = [item for item in decoded if item[0] == 'info']
        if len(info_dict) != 1:
            raise ManagerError("Single info dict not found in torrent file")
        re_encoded = bencode(info_dict[0][1])

        return hashlib.sha1(re_encoded).digest()

    def _parsePeers(self, response):
        """Return a list of peers for this torrent.
           Currently function only works for binary model tracker response.

        Args:
          response (dict): bdecoded tracker response

        Returns:
          peers (list): list of (ip, port) tuples, one for each peer
           and empty if no peers are found

        Raises:
          ManagerError if peers binary data is wrong len

        Spec:
          Peers value is a string consisting of multiples of 6 bytes. First
          4 bytes are the IP address and last 2 bytes are the port number.
          All in network (big endian) notation.

        """
        myip = ipgetter.myip()
        # myip = MY_IP_ADDRESS  # TODO: Hardcoded for testing purposes
        peers = []
        if 'peers' not in response.keys():
            return peers

        binary_data = response['peers']
        if len(binary_data) % 6 != 0:
            raise ManagerError("Peers binary data is not a multiple of 6.")

        for i in xrange(len(binary_data) / 6):  # each peer is 6 bytes
            (ip1, ip2, ip3, ip4, port) = struct.unpack('>4BH',
                                                       binary_data[:6])
            ip_address = ".".join([str(ip1), str(ip2), str(ip3), str(ip4)])
            if ip_address != myip:
                peers.append((ip_address, port))
            binary_data = binary_data[6:]

        return peers

    def numBlocks(self, piece_index):
        """Given a piece index, return the number of blocks in this piece.

        Raises:
          ManagerError if piece_index is not valid for this torrent

        """
        if piece_index < 0 or piece_index > self.num_pieces:
            raise ManagerError("piece_index is out of range in numBlocks")
        elif piece_index != self.num_pieces - 1:
            return self.piece_len // BLOCKSIZE
        else:
            extra_bytes = self.total_size % self.piece_len
            return int(math.ceil(extra_bytes / float(BLOCKSIZE)))

    def bytesInBlock(self, piece_index, block_index):
        """Return the number of bytes in the block in piece.

        Raises:
          ManagerError if piece_index or block_index is not valid

        """
        if piece_index < 0 or piece_index > self.num_pieces:
            raise ManagerError("Piece index is out of range.")
        if block_index < 0 or block_index > self.numBlocks(piece_index):
            raise ManagerError("Block index is out of range.")
        if (piece_index == (self.num_pieces - 1) and
                block_index == (self.numBlocks(piece_index) - 1)):
            size = self.total_size % BLOCKSIZE
            return (size if size != 0 else BLOCKSIZE)
        else:
            return BLOCKSIZE

    def blocksEncompassed(self, begin, length):
        """Return list of blocks fully encompassed by range(begin,len).

        Will return only block indices where the entirety of the block lies
        within [begin:begin+len]

        Returns:
          list(tuple(piece index, block index))

        """
        blocks = []
        for p_index in xrange(self.num_pieces):
            byte = p_index * self.piece_len
            for b_index in xrange(self.numBlocks(p_index)):
                if byte >= begin and byte < (begin + length):
                    blocks.append((p_index, b_index))
                byte += self.bytesInBlock(p_index, b_index)
        return blocks

    def pieceStatus(self, piece):
        """Return True if piece is not alredy downloaded and not active."""
        if piece < 0 or piece >= self.num_pieces:
            raise ManagerError("Piece index out of range in isPieceNeeded")
        with self._pieces_ledger_lock:
            return self._pieces_ledger[piece]

    def getCompletedPieces(self):
        """Returns a set of piece indices that are completely downloaded."""
        with self._pieces_ledger_lock:
            return set([i for i, x in enumerate(self._pieces_ledger)
                       if x == "downloaded"])

    def getNeededPieces(self):
        """Return the set of piece_indices not downloaded and not active"""
        with self._pieces_ledger_lock:
            return set([i for i, x in enumerate(self._pieces_ledger)
                       if x == "free"])

    def activelyHeldPieces(self, peer):
        """Return a set of piece indices held by peer.

        Args:
          peer (Peer): Peer object to query against

        """
        with self._pieces_ledger_lock:
            return set([i for i, x in enumerate(self._pieces_ledger)
                       if x == peer.ID])

    def makeActive(self, peer, piece):
        """Set piece as actively held by peer.

        Returns:
          True on SUCCESS
          False if index is wrong or piece is already active or downloaded.

        """
        if piece < 0 or piece >= self.num_pieces:
            return False
        with self._pieces_ledger_lock:
            if self._pieces_ledger[piece] == "free":
                self._pieces_ledger[piece] = peer.ID
                return True
        return False

    def readData(self, piece_index, begin_offset, length):
        """Read and return bytes from file.

        Will read length bytes from file beginning from piece_index at
        byte_offset. If piece_index+byte_offset+length runs off the end
        of the file, will return data up to the end of the file.

        Returns:
          bytes (str): array of byte data ready from file

        Raises:
          ManagerError if piece_index or begin_offset are illigitimate, or
          if error occur during read.

        """
        print "TRYING TO READ: ", piece_index, begin_offset, length
        return [0]*length

    def _allDataSaved(self, piece):
        """Return true if piece has all of its bytes saved in buffer"""
        with self._pieces_data_lock:
            for p in self._pieces_data[piece]:
                if p == None:
                    return False
        return True

    def saveData(self, piece, offset, data):
        """Save data to disk starting at offset from beginning of piece.

        Buffer saved data until a full piece is "saved". Upon receiving all
        bytes in a piece, checksum the data, and if legitimate, save data
        to disk. Will truncate data if it runs off the end of the file.

        Raises:
          MangerError if begin byte is illigitimate

        """
        print "saveData: ", piece, offset
        with self._pieces_data_lock:
            for i, byte in enumerate(data):
                self._pieces_data[piece][offset + i] = byte
        if self._allDataSaved(piece):
            with self._pieces_data_lock:
                data = "".join(byte for byte in self._pieces_data[piece])
                self._pieces_data[piece] = []  # Clear out data from RAM
            checksum = hashlib.sha1(data).digest()
            assert(checksum == self._piece_hashes[20*piece:20*piece+20])
            self._write(piece, data)
            with self._pieces_ledger_lock:
                self._pieces_ledger[piece] = "downloaded"

    def _findFileSplits(self, piece):
        """Return list(file index, offset, num_bytes) from piece in a file"""
        splices = []
        p_ptr = piece * self.piece_len
        p_len = sum(self.bytesInBlock(piece, x) for x in
                    xrange(self.numBlocks(piece)))
        f_ptr = 0
        with self._files_lock:
            for i, f in enumerate(self._files):
                if p_ptr >= f_ptr and p_ptr < f_ptr + f.f_len:
                    amt = min(p_len, f.f_len + f_ptr - p_ptr)
                    splices.append((i, p_ptr - f_ptr, amt))
                    if amt == p_len:
                        break
                    p_ptr += amt
                    p_len -= amt
                f_ptr += f.f_len
        return splices

    def _write(self, piece, data):
        """Write data in piece from buffer to files on disk"""
        splits = self._findFileSplits(piece)
        written = 0
        for s in splits:
            f_idx = s[0]
            offset = s[1]
            num_bytes = s[2]
            with self._files_lock:
                self._files[f_idx].f_obj.seek(offset)
                self._files[f_idx].f_obj.write(data[written:num_bytes])
            written += num_bytes
        assert written == len(data)
