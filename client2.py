from Class import Peer

if __name__ == "__main__":
    # Initialize a peer
    peer = Peer('127.0.0.1')

    # Optionally, connect to another peer
    peer.connect_to_peer('127.0.0.1', 2270)

    # Send a message to connected peers
    peer.send_message("Hello, peers!")