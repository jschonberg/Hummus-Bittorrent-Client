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
        self.mock_master_record = Mock()
        piece_length = 512 * KILOBYTE
        self.mock_manager = Mock(torrent_file={'piece_length': piece_length}, master_record=self.mock_master_record)
        self.mock_manager.mock_master_record = self.mock_master_record
        self.mock_master_record.totalSizeInBytes.return_value = 2 * KILOBYTE ** 4 + 3 * KILOBYTE + 22
        self.mock_master_record.numPieces.return_value = int(math.ceil(float(self.mock_master_record.totalSizeInBytes()) / self.mock_manager.torrent_file['piece_length']))
        
        # local_peer = Peer(mock_manager, '-HU0010-hZNIBCmgrY5Y', 'localhost', LOCALHOST_PORT)
        self.local_peer = Peer(self.mock_manager, SELF_PEER_ID,'localhost', LOCALHOST_PORT)
        self.remote_peer = Peer(self.mock_manager, u'-HU0010-0HyZeTecrY0m'.encode('utf-8'), 'localhost', REMOTEHOST_PORT)

    def tearDown(self):
        if self.local_peer._sock:
            self.local_peer._sock.close()
        if self.remote_peer._sock:
            self.remote_peer._sock.close()

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