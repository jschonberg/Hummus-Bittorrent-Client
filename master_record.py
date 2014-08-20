import io
import sys
import math

class MasterRecord(object):
    #----
    #Class Functions
    #----
    def __init__(self, manager, torrent_file, dest_path):
        self.manager = manager
        self.torrent_file = torrent_file

        #For each piece create a record entry to track the state of download for that data
        #status can be "needed", "active" or "complete"
        #blocks[index] contains staged, but not yet written bytes
        blocks = [bytearray()] * math.ceil(self.torrent_file.piece_length / BLOCK_SIZE) #Staged block data to be written to disk
        self._statusRecord = [{"status" : "needed",
                              "blocks" : blocks}] * self.numPieces() 
        self._byteFile = self.openFile()
    def __del__(self):
    def __enter__(self):
    def __exit__(self, type, value, traceback):

    #----
    #Utility Functions
    #----
    def totalSizeInBytes():
        #Return self.totalBytes
        """Returns the number of bytes in this torrent"""
    def numPieces():
        """Returns the number of pieces in this torrent"""
    def openFile(self):
        "Open a file at self.dest_path to download to."
        "If file already exists then evaluate validity with SHA1 hash and initialize record"
        "Return io.BufferedRWPair" #TODO what are errors thrown and other return values? #when to close file?
    def setPieceStatus(self, piece_index, new_status):
        "Set status of piece at piece_index to have new_status"
    def getPieceStatus(self, piece_index):
        "Return status of piece at piece_index"

    #----
    #Operational Functions
    #----
    def isPieceNeeded(self, piece_index):
        "Returns True if this piece is needed, False otherwise"
    def getNeededPieces(self):
        """
        Returns a SET of piece_indices that are still needed
        Returns an empty list if no pieces are needed
        """
    def isPieceCompleted(self, piece_index):
        "Returns True if this piece is completed, false otherwise"
    def getCompletedPieces(self):
        "Returns a list of piece_indices that have been completed"
    def isPieceActive(self, piece_index):
        "Returns True if this piece is active, false otherwise"
    def makePieceActive(self, piece_index):
        """
        Set piece_index as active. Returns true if success. None if index is wrong. False if piece is already active.
        """
    def makePieceInactive(self, piece_index):
        """
        Called by a dying Peer. MasterRecord will make piece either "needed" or "complete" based on what has been downloaded
        Returns True on success. False if piece is already inactive. None if the piece_index is wrong.
        """
    def getActivePieces(self):
        "Returns a set of piece_indices that are active"
    def saveData(self, piece_index, begin_offset, bytes):
        "Write bytes data to byteFile. bytes should be an immutable python bytes object"
        "Only save data to disk if all blocks for this piece have now been downloaded. Check hash first."
        "If write to disk was successful and all blocks in this piece have been written, update piece status in record, clear out staged blocks from memory"
        #TODO: Which errors are thrown and what are return values?
    def readData(self, piece_index, begin_offset, length):
        "Read length bytes from byteFile beginning from piece at piece_index and data starting at begin_offset"
        "Return bytes or None if there is an error"
        #TODO: Which errors are thrown and what are return values?
