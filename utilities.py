import logging
import socket
from threading import Lock
import hashlib
import struct

BLOCK_SIZE = 16384 #16KB

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
    Accepts info_hash, self_peer_id
    Returns packed handshake bytestring ready for sending over the  network on success, None on failure
    """

    #Per Bittorrent spec, handshake: <pstrlen><pstr><reserved><info_hash><peer_id>
    pstrlen = '\x13'
    pstr = 'BitTorrent protocol'
    reserved = '\x00\x00\x00\x00\x00\x00\x00\x00'
    info_hash = info_hash
    peer_id = self_peer_id

    handshake_message = struct.pack('>i19s8x40s', pstrlen, pstr, reserved, (info_hash + peer_id))

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

    if len(handshake_message) is not 68:
        return None

    unpacked = unpack('>i19s8x40s', handshake_message)

    pstrlen = unpacked[0]
    if pstrlen is not 19:
        return None

    pstr = unpacked[1]
    if pstr is not 'BitTorrent protocol':
        return None

    reserved = unpacked[2]
    if len(reserved) is not 8:
        return None

    if len(unpacked[3]) is not 40:
        return None

    info_hash = unpacked[3][0:20]
    peer_id = unpacked[3][20:]

    return (info_hash, peer_id)









