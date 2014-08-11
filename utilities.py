import socket
from threading import Lock


BLOCK_SIZE = 16384 #16KB

def listen(port, manager):
    "Start listening for incoming connections on port"
    "If a connection request comes in, ceate a socket ask manager to create responder Peer to manage"
    "Should be executed on it's own thread or will block program execution"
    #TODO: I think this function needs to be able,generate peers, and then parse the handshake, so that it knows which manager to add this peer to?? Then it needs to hand the peer off to the manager in question
    #TODO: Once we connect to a peer, will future messages from them get routed to the right socket or will it battle with the .listen() method happening here? In other words is recieving specifically different than listening?

def connectToPeer(ip_address, port):
    "Connect to peer at ip_address:port"
    "Returns connected socket on success, None on failure"
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
        print ("Could not connect to peer at "
              + str(ip_address) + ":" + str(port))
    else:
        print ("Successfully connected to peer at "
              + str(ip_address) + ":" + str(port))

    return sock

