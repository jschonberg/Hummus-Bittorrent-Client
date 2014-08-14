import logging
import socket
from threading import Lock
import hashlib
import struct

BLOCK_SIZE = 16384 #16KB

class HummusError(RuntimeError):
    def __init__(self, reason):
        self.reason = reason
    def __repr__(self):
        return str(reason)
    def __str__(self):
        return str(reason)

def listen(port, manager):
    """Start listening for incoming connections on port
    If a connection request comes in, ceate a socket ask manager to create responder Peer to manage
    Should be executed on it's own thread or will block program execution
    """
    pass
    #TODO: I think this function needs to be able,generate peers, and then parse the handshake, so that it knows which manager to add this peer to?? Then it needs to hand the peer off to the manager in question
    #TODO: Once we connect to a peer, will future messages from them get routed to the right socket or will it battle with the .listen() method happening here? In other words is recieving specifically different than listening?

def connectToPeer(ip_address, port):
    """
    Connect to peer at ip_address:port
    Returns connected socket on success, None on failure
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except sock.error as msg:
        sock = None

    try:
        sock.connect((ip_address,port))
    except socket.error as msg:
        sock.close()
        sock = None

    if sock is None:
        logging.error("Could not connect to peer at "
              + ip_address + ":" + str(port))
    else:
        logging.info("Successfully connected to peer at "
              + str(ip_address) + ":" + str(port))

    return sock

def constructHandshake(info_hash, self_peer_id):
    """
    Accepts info_hash, self_peer_id (pre-encoded in utf-8)
    Returns packed handshake bytestring ready for sending over the  network on success, None on failure
    """

    #Per Bittorrent spec, handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
    pstrlen = 19
    pstr = 'BitTorrent protocol'
    info_hash = info_hash
    peer_id = self_peer_id

    handshake_message = struct.pack('>B19s8x40s', pstrlen, pstr, info_hash + peer_id)

    if len(handshake_message) is not 68:
        logging.error("Constructing handshake produced a string not 68 in length.")
        return None
    else:
        return handshake_message

def parseHandshake(handshake_message):
    """
    Accepts bytearray handshake_message, checks to make sure it's a legitimate message
    Accepts info as python data structure format of info dictionary
    Returns (info_hash, peer_id) tuple on success.  None on failure
    """
    # import pdb; pdb.set_trace()

    if len(handshake_message) != 68:
        logging.error('Received handshake length is not 68.')
        return None

    unpacked = struct.unpack('>B19s8x40s', handshake_message)

    pstrlen = unpacked[0]
    if pstrlen != 19:
        logging.error('Received handshake prstrlen is not 19.')
        return None

    pstr = unpacked[1]
    if pstr != 'BitTorrent protocol':
        logging.error('''Received handshake pstr is not 'BitTorrent protocol'.''')
        return None

    if len(unpacked[2]) != 40:
        #This is sort of pointless because we only told struct to unpack the characters UP to the 40th string charater. So it'll notice if the bytestring is shorter than requested but not if longer, since it'll be cut off. Can we do a check on the len of handshake_message vs. unpacked (above) instead?
        logging.error('''Length of received handshake's info_hash + peer_id is not 40.''')
        return None

    info_hash = unpacked[2][0:20]
    peer_id = unpacked[2][20:]

    return (info_hash, peer_id)









