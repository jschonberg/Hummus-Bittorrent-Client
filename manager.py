from collections import namedtuple
import os
import bencode
import utilities
from threading import Lock


class ManagerError(HummusError):
    """Thrown in case of Manager class errors. Inherits HummusError.

    Args:
      msg (str): Human readable string describing the exception.

    Attributes:
      msg (str): Human readable string describing the exception.

    """
    pass

class Manager(object):

    """Download all files for torrent to disk.

    Attributes:
      piece_len (int): Number of bytes per piece. Set after parse of tracker
        response.
      File (namedtuple): ('file_obj, file_path_name, byte_len')
      MAX_PEERS (int): Maximum number of simoultaneous connections

    """

    File = namedtuple('File', 'file_obj, file_path_name, byte_len')
    PORT = 6889
    MAX_PEERS = 30

    def __init__(self, torrent_path, dest_path):
        """Make Manager ready to serve/download files.

        Contact the tracker. Parse and save tracker response.
        Initialize disk files to ready.

        Args:
          torrent_path (str): Absolute filepath to torrent file
          dest_path (str): Absolute path to save destination directory

        """
        self._alive_lock = Lock()
        with self._alive_lock:
            self._alive = True
        self._torrent_path = torrent_path
        self._dest_path = os.path.abspath(dest_path)
        self._info_hash = self._renderInfoHash()
        self._peer_id = utilities.SELF_PEER_ID

        metainfo = self._parseMetainfoFile()
        self._tracker_url = metainfo['announce']
        self.piece_len = metainfo['info']['piece length']
        self._initFiles(metainfo)

        self._bytes_uploaded = 0
        self._bytes_downloaded = 0
        self._bytes_left = sum([x.byte_len for x in self._files])

        request = self._createTrackerReq()
        response = self.contactTracker(request)
        self.peers = response['peers'][:]
        self._interval = response['interval']
        if response['tracker id']:
            self._tracker_id = response['tracker id']

    def __del__(self):
        pass

    def die(self, message=None):
        # TODO Send tracker "Stopped" … Put in die()?
        if message:
            logging.error(message)
        with self._alive_lock:
            self._alive = False

    def _createTrackerReq():
        pass

    def contactTracker(request):
        pass

    def _initFiles(self, metainfo):
        """Open files, as described in metainfo, for writing.
        Args:
          metainfo (dict): .torrent metainfo file properly parsed to dict

        Returns:
          Nothing

        Raises:
          ManagerError if multi or single file mode cannot be determined

        """
        if "files" in metainfo.keys(): #Multiple file torrent
            for info in metainfo["files"]:
                f_path_name = self._dest_path + "/".join(info['path'])
                f_len = info['length']
                f_obj = open(f_path_name, 'r+b')
                f = Manager.File(file_obj=f_obj,
                                 file_path_name=f_path_name,
                                 byte_len=f_len)
                self._files.append(f)
        elif "length" in metainfo.keys(): # Single file torrent
            f_path_name = self._dest_path + "/" + metainfo['name']
            f_len = metainfo['length']
            f_obj = open(f_path_name, 'r+b')
            f = Manager.File(file_obj=f_obj,
                             file_path_name=f_path_name,
                             byte_len=f_len)
            self._files.append(f)
        else:
            raise ManagerError("Cant determine single or multi file mode")

    def _parseMetainfoFile(self, rtn_type={}):
        # """
        # Takes in a path to a .torrent file. Parses it and sets relevant class data members
        # """
        # f = open(self.TORRENT_PATH, 'r')
        # content = f.read()
        # torrent = bencode.bdecode(content)

        # tracker_url = torrent['announce']

        # # TODO: Pull out IP addr and port for UDP tracker

        # self.info_dictionary = torrent['info']
        # assert self.info_dictionary

        # torrent_tuple = bencode.bdecode(content, rtn_type)
        # for t in torrent_tuple:
        #     if t[0] == 'info':
        #         self._info_dictionary_tuple = t
        # assert self._info_dictionary_tuple

    def start(self):
        #Go through peer list and kick off a few peers to start downloading the file.
            #Max out at MAX_PEERS (only create up tot hat many)
        #Query each peer to see if they are active, if not remove them from list of active peers and they should just die
        #Contact tracker and ask for more peers
        pass

    def _renderInfoHash():
        """Render and return urlencoded 20-byte SHA1 hash of the value of
           the info key from the Metainfo file.

        """

    def getInfoHash():
        """
        Return info_hash for this torrent
        """
        pass

if __name__ == '__main__':
    pass
