import unittest
from nose.tools import eq_

import socket
from threading import Thread, Lock

from hummus.utilities import connectToPeer

INVALID_PORT = 6889
LOCALHOST_PORT = 6885
serversocket = None

def setUp():
    global serversocket
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', LOCALHOST_PORT))
    serversocket.listen(5)

def tearDown():
    serversocket.close()

class TestGlobalFunctions(unittest.TestCase):
    def runServer(self):
        with self._clientsocket_lock:
            with self._address_lock:
                (self._clientsocket, self._address) = serversocket.accept()

    def setUp(self):
        self._clientsocket_lock = Lock()
        self._address_lock = Lock()
        t = Thread(target=self.runServer)
        t.daemon = True
        t.start()

    def test_connectToPeer_valid(self):
        socket = connectToPeer('localhost', LOCALHOST_PORT)
        eq_(socket.getpeername(), ('127.0.0.1', LOCALHOST_PORT))

    def test_connectToPeer_invalid(self):
        socket = connectToPeer('localhost', INVALID_PORT)
        eq_(socket, None)



