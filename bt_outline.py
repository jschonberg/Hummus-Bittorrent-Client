"""
Steps:
    Connect to tracker.
        Get URL (params). > from .torrent
        Register with tracker?
        Parse tracker response.
            Peers and info.
            Files and pieces.
            Tracker info.

    Connect to peer.
        Open socket with IP.
        Handshake.
        Bitfield message?
        Message parsing.
            Payload vs. non-payload messages (ie, have/piece vs. interested, choke, etc).
        Initiate download.
        Respond to upload requests.
        Terminate connection.
        Deal with dropped connections.

    Evaluate what to get where.
        What do you have/not have already.
        Which peers have what you want.

    Networking.
        Open sockets.
        Get data.
        Close socket.
        Deal with UDP.

    Saving and Verifying Files.
        Check that binary data is correct against a hash.
            At the piece level.
            Entire file = too big (fills memory).
            Ind. blocks = have no IDing hash.
        Save data to disk.


Structure:
    Octopus master.
    Does: updates tracker, listens for requests, establishes and manages peers.
    Manages: peers, master array, scribes.
        Peers.
        Does: Receives and parses messages, figures out what block piece to download next (or if upload peer, serves a block of requested piece).
        Do we want two different types of peers (download vs. upload)?
        How does peer know that block x of piece y is still needed?

        Master Array.
        Does: locks/unlocks itself when peers need to check what to download next.

        Scribes.
        Does: created when a piece is finished downloading, checks piece's hash, and saves it to disk.
"""
