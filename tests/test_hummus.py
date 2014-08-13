# -*- coding: utf-8 -*-

import unittest
from nose.tools import eq_
import logging

import socket
from threading import Thread, Lock
import hashlib

import hummus.utilities as utilities
import hummus.bencode as bencode

INVALID_PORT = 6889
LOCALHOST_PORT = 6885
clientsocket_lock = Lock()
address_lock = Lock()
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind(('localhost', LOCALHOST_PORT))
serversocket.listen(5)

bencoded_info = u'd5:filesld6:lengthi764393e4:pathl89:029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download___________.exeeed6:lengthi291e4:pathl27:Distributed by Mininova.txteee4:name76:029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download_ 12:piece lengthi1048576e6:pieces20:/ZPl ‚k}³ôÃŸ–CA¼Ð 6e'

info = [(u'files', 
                        [
                            [(u'length', 764393), 
                             (u'path', [u'029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download___________.exe'])], 
                            [(u'length', 291), 
                             (u'path', [u'Distributed by Mininova.txt'])]
                        ]
                ), 
                (u'name', u'029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download_ '), 
                (u'piece length', 1048576), 
                (u'pieces', u'/ZPl ‚k}³ôÃŸ–CA¼Ð 6')]

def runServer():
    global clientsocket_lock, address_lock, serversocket
    with clientsocket_lock:
        with address_lock:
            (clientsocket, address) = serversocket.accept()

def setUp():
    logging.basicConfig(level=logging.INFO)
    t = Thread(target=runServer)
    t.daemon = True
    t.start()

def tearDown():
    serversocket.close()

class TestBencode(unittest.TestCase):
    def test_bencode(self):
        bencode_test = bencode.bencode(info)
        eq_(bencode_test, bencoded_info)

    def test_bdecode(self):
        bdecode_test = bencode.bdecode(bencoded_info)
        eq_(bdecode_test, info)

class TestUtilities(unittest.TestCase):
    def test_connectToPeer_valid(self):
        socket = utilities.connectToPeer('localhost', LOCALHOST_PORT)
        eq_(socket.getpeername(), ('127.0.0.1', LOCALHOST_PORT))

    def test_connectToPeer_invalid(self):
        socket = utilities.connectToPeer('localhost', INVALID_PORT)
        eq_(socket, None)

    def test_constructHandshake(self):
        pass

    def test_parseHandshake(self):
        pass
        
# class TestCreatePeer(unittest.TestCase):
#     def setUp(self):
#         self.manager = {}
#     def test_create_peer(self):
#         peer = Peer(peer_id, self.manager)

# class TestPeerMethods(unittest.TestCase):
#     def setUp(self):
#         test_peer1 = Peer()
#         test_peer2 = Peer()

#     def test_send(self):
#         class TestSocket(object):
#             def __init__(self):
#         eq_()
#     def test_recv(self):

#         eq_()

