"""
Objects:
    Manager()
    Does: initializes other objects, communicates with tracker, establishes and manages peers, manages view.
    
    Peer()
    Does: Connets to remote peer, exchanges messages and data until connection dies, or one/both peers are finished with each other 

    MasterRecord()
    Does: Reads/Writes data to disk and tracks progress and state of data in thread_safe way

    View()
    Does: Renders the download and upload progress of all torrents to the user

Steps:
1) Get metainfo file list from argv or, if None, ask the user for a metainfo file one at a time until done
2) Get save location from argv, or if None, ask the user for a save location
3) Create Mangers for each torrent
    3.1 Manager parses torrent file
    3.2 Manager reaches out to tracker, gets response, parses response
    3.3 Manager creates MasterRecord to manage data and status/state
    3.4 Manager starts initiator peers to go off and collect data
        3.4.1 TODO: What does peer do and in what order?
    3.5 TODO: More?
4) Call listen() on it's own thread on an open socket port that will respond to seed requests
5) Create and start View() on it's own thread to print program state at regular intervals

TODO: FINISH steps :)




====OLD=====

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





"""
