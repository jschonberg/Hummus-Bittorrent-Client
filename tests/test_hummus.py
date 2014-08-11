import unittest
from nose.tools import eq_

import socket
from threading import Thread, Lock

from hummus.utilities import connectToPeer
from hummus.peer import Peer.send, Peer.recv

INVALID_PORT = 6889
LOCALHOST_PORT = 6885
clientsocket_lock = Lock()
address_lock = Lock()

def runServer(self):
    global clientsocket_lock, address_lock
    with clientsocket_lock:
        with address_lock:
            (clientsocket, address) = serversocket.accept()

def setUp():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', LOCALHOST_PORT))
    serversocket.listen(5)
    t = Thread(target=runServer)
    t.daemon = True
    t.start()

def tearDown():
    serversocket.close()

class TestGlobalFunctions(unittest.TestCase):
    def test_connectToPeer_valid(self):
        socket = connectToPeer('localhost', LOCALHOST_PORT)
        eq_(socket.getpeername(), ('127.0.0.1', LOCALHOST_PORT))

    def test_connectToPeer_invalid(self):
        socket = connectToPeer('localhost', INVALID_PORT)
        eq_(socket, None)
        
class TestCreatePeer(unittest.TestCase):
    def setUp(self):
        self.manager = {}
    def test_create_peer(self):
        peer = Peer(peer_id, self.manager)

class TestPeerMethods(unittest.TestCase):
    # def setUp(self):
    #     test_peer1 = Peer()
    #     test_peer2 = Peer()

    def test_send(self):
        class TestSocket(object):
            def __init__(self):
        eq_()
    def test_recv(self):

        eq_()

