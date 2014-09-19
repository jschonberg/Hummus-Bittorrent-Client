import logging
import socket
import struct

KILOBYTE = 1024
BLOCKSIZE = 16 * KILOBYTE
SELF_PEER_ID = u'-HU0010-0HyZeTecrY0m'.encode('utf-8')


class HummusError(Exception):
    """Base class for all errors thrown by Hummus.

    Args:
      msg (str): Human readable string describing the exception.

    Attributes:
      msg (str): Human readable string describing the exception.

    """
    def __init__(self, msg):
        self.msg = msg


def connectToPeer(ip_address, port):
    """Connect to peer at ip_address:port

    Args:
      ip_address (str): IP address of the peer to conenct to
      port (int): port number of peer to connect to

    Returns:
      Active socket on success, None on failure

    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip_address, port))
    except socket.error:
        sock.close()
        sock = None

    if sock is None:
        print "".join(["Could not connect to network at ",
                      ip_address, ":", str(port)])
    else:
        print "".join(["Successfully connected to network at ",
                      str(ip_address), ":", str(port)])

    return sock


def constructHandshake(info_hash, self_peer_id):
    """ Construct a packed handshake bytestring ready for sending to a peer

    Args:
      info_hash (str): 20-byte SHA1 hash of the value of the torrent info key
      self_peer_id (str): 20-byte UTF-8 encoded peer id

    Returns:
      Packed handshake bytestring on SUCCESS
      None on FAILURE

    Spec:
      Bittorrent protocol specifies handshake message will be in the format
      <pstrlen><pstr><reserved><info_hash><peer_id>

      <pstrlen> -> 1 byte == 19
      <pstr> -> 19 bytes == 'BitTorrent protocol'
      <reserved> -> 8 bytes == 0
      <info_hash> -> 20 bytes == string info hash for this torrent
      <peer_id> -> 20 bytes == string for peer unique ID

    """

    pstrlen = 19
    pstr = 'BitTorrent protocol'
    info_hash = info_hash
    peer_id = self_peer_id

    handshake_message = struct.pack('>B19s8x40s',
                                    pstrlen, pstr, info_hash + peer_id)

    if len(handshake_message) != 68:
        logging.error("len of constructred handshake is not 68.")
        return None
    else:
        return handshake_message


def parseHandshake(handshake_message):
    """Verify and unpack a handshake message into an info hash and a peer id

    Args:
      handshake_message (bytearray): handshake message from peer

    Returns:
        (info_hash, peer_id) on SUCCESS
        None on FAILURE

    Spec:
      See docstring for 'constructHandshake()' for handshake spec details

    """
    if len(handshake_message) != 68:
        logging.error('Received handshake length is not 68.')
        return None

    unpacked = struct.unpack('>B19s8x40s', handshake_message)
    if unpacked[0] != 19:
        logging.error('Received handshake prstrlen is not 19.')
        return None
    if unpacked[1] != 'BitTorrent protocol':
        logging.error("Received handshake pstr is not 'BitTorrent protocol'.")
        return None
    info_hash = unpacked[2][0:20]
    peer_id = unpacked[2][20:]

    return (info_hash, peer_id)
