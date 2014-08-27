# -*- coding: utf-8 -*-

import unittest
from nose.tools import eq_
import logging

import socket
from threading import Thread, Lock
import struct

import hummus.utilities as utilities
import hummus.bencode as bencode
from __init__ import LOCALHOST_PORT, INVALID_PORT

KILOBYTE = utilities.KILOBYTE
SELF_PEER_ID = utilities.SELF_PEER_ID

clientsocket_lock = Lock()
address_lock = Lock()
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('localhost', LOCALHOST_PORT))
serversocket.listen(5)

def runServer(clientsocket_lock, address_lock, serversocket):
    with clientsocket_lock:
        with address_lock:
            (clientsocket, address) = serversocket.accept()

def setUp():
    logging.basicConfig(level=logging.INFO)

    t = Thread(target=runServer, args=(clientsocket_lock, address_lock, serversocket))
    t.daemon = True
    t.start()

def tearDown():
    serversocket.close()

class TestBencode(unittest.TestCase):
    def setUp(self):
        self.bencoded_info = b'd5:filesld6:lengthi764393e4:pathl89:029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download___________.exeeed6:lengthi291e4:pathl27:Distributed by Mininova.txteee4:name76:029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download_ 12:piece lengthi1048576e6:pieces20:/ZPl\xa0\x82\x0ck}\xb3\xf4\xc3\x9f\x96CA\xbc\xd0\t6e'

        self.info = [(b'files', 
                        [
                            [(b'length', 764393), 
                             (b'path', [b'029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download___________.exe'])], 
                            [(b'length', 291), 
                             (b'path', [b'Distributed by Mininova.txt'])]
                        ]
                ), 
                (b'name', b'029_7daystoeasymoneygetpaidtowriteabook_Sjhd Free Plr Mrr Article Download_ '), 
                (b'piece length', 1048576), 
                (b'pieces', b'/ZPl\xa0\x82\x0ck}\xb3\xf4\xc3\x9f\x96CA\xbc\xd0\t6')]
    def test_bencode(self):
        bencode_test = bencode.bencode(self.info)
        eq_(bencode_test, self.bencoded_info)

    def test_bdecode(self):
        bdecode_test = bencode.bdecode(self.bencoded_info)
        eq_(bdecode_test, self.info)

class TestUtilities(unittest.TestCase):
    def setUp(self):
        self.info_hash = b'/ZPl\xa0\x82\x0ck}\xb3\xf4\xc3\x9f\x96CA\xbc\xd0\t6'
        self.peer_id = SELF_PEER_ID
        self.preconstructed_handshake = struct.pack('>B19s8x40s', 19, 'BitTorrent protocol', self.info_hash + self.peer_id)

    def test_connectToPeer_valid(self):
        test_socket = utilities.connectToPeer('localhost', LOCALHOST_PORT)
        eq_(test_socket.getpeername(), ('127.0.0.1', LOCALHOST_PORT))

    def test_connectToPeer_invalid(self):
        test_socket = utilities.connectToPeer('localhost', INVALID_PORT)
        eq_(test_socket, None)

    def test_constructHandshake(self):
        handshake = utilities.constructHandshake(self.info_hash, self.peer_id)
        eq_(handshake, self.preconstructed_handshake)

    def test_parseHandshake(self):
        info_hash, peer_id = utilities.parseHandshake(self.preconstructed_handshake)
        eq_((info_hash, peer_id), (self.info_hash, self.peer_id))








