"""
Objects:
    Manager()
    Does: initializes other objects, updates tracker, listens for requests, establishes and manages peers.
    Manages: peers, master array, scribes.
    
    Peer()
    Does: Establishes remote connection with peer. 

        LeechPeer()
        Does: Gets needed blocks from remote peer

        SeedPeer()
        Does: Sends requested blocks to remote peer.

    MasterRecord()
    Does: Thread safe record of what blocks/pieces of file(s) we already have. Interface to access/write btFile data to disk
    Accepts: Metainfo() object, 

        BTFile()
        Does: Wrapper for FileIO to write, read, and verify byte-chunks of data to and from Disk
        Should: Only be accesses through a MasterRecord() object, to ensure state of our progress is recorded properly

    Listener()
    Does: Waits for seed requests to come in on an open socket. Delegates requests back to Manager() when they come in, so that the Manager() may kick off a Peer to handle the request
    Accepts: Reference to a Manager()

    View()
    Does: Renders the download and upload progress of all files to the user
    Accepts: Reference to a Manager()

    Metainfo()
    Does: Parsed, structured representation of a .torrent metainfo file
    Accepts: metainfo .torrent file location

Structure:
<The basic idea here is that we do some initial initialization and create a manager, which itself kicks off some initialization.
After this initialization phase, the manager only responds to requests from other objects, delegates work as necessary, and gets information from other objects and passes back to requesting object as necessary.>


    __main__:
        * Get metainfo file list from argv or, if None, ask the user for a metainfo file one at a time until done
        * Get save location from argv, or if None, ask the user for a save location
        * Create a Manager() that will, for each metainfo file:
            - Create a Metainfo() object which will parse the .torrent file and structure its contents
            - Create a MasterRecord() object which will scan the file system, figure out what parts of the file(s) have already been downloaded, and set up initial state to act as record keeper (for this .torrent) for rest of program session
            - Register this MasterRecord in the Manager() registry, so our Manager() knows which files it's currently seeding/leeching
        * Create and start() a Listener() on it's own thread on an open socket port that will respond to seed requests
            NOTE: Make sure Listener() renders properly and avoids race conditions if Manager.start() has not been called yet
        * Create and start() a View() on it's own thread so we can keep an eye on the system state
            NOTE: Make sure View() renders properly and avoids race conditions if Manager.start() has not been called yet
        * Manager().start() on it's own thread

    __Manager().start()__:
        * 

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
