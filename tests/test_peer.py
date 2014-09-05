# -*- coding: utf-8 -*-

import unittest
from nose.tools import eq_, ok_
from mock import Mock
import logging

import math
from threading import Thread

from hummus.utilities import SELF_PEER_ID, KILOBYTE
from hummus.peer import Peer
from __init__ import LOCALHOST_PORT, REMOTEHOST_PORT

class TestPeerMethods(unittest.TestCase):
    def setUp(self):
        #Set up mock Master_record and Manager objects:
        self.mock_master_record = Mock()
        piece_length = 512 * KILOBYTE
        self.mock_manager = Mock(torrent_file={'piece_length': piece_length}, master_record=self.mock_master_record)
        self.mock_manager.mock_master_record = self.mock_master_record
        self.mock_master_record.totalSizeInBytes.return_value = 2 * KILOBYTE ** 4 + 3 * KILOBYTE + 22
        self.mock_master_record.numPieces.return_value = int(math.ceil(float(self.mock_master_record.totalSizeInBytes()) / self.mock_manager.torrent_file['piece_length']))

        #Initialize two peers that use different peer IDs. Peers are initialized w/o sockets.
        self.local_peer = Peer(self.mock_manager, SELF_PEER_ID,'localhost', LOCALHOST_PORT)
        self.remote_peer = Peer(self.mock_manager, u'-HU0010-hZNIBCmgrY5Y'.encode('utf-8'), 'localhost', REMOTEHOST_PORT)

        self.local_peer.createSocket()
        self.remote_peer.createSocket()

    def test_isAlive(self):
        ok_(self.local_peer.isAlive(), True)


    # self.master_record.isPieceNeeded.called returns true/false if called. (callcount)
    # can give side_effects a dict instead of a list.
    # patch = MagicMock, not Mock
    # @patch('peer.socket')
    # def test_socket_recv(self, socket):
    #     socket.recv.return_value = "Blah"

    # def tearDown(self):
    #     self.mock_manager.stop()