import socket
import threading
import random as rd

PORT = rd.randint(1000, 6000)

class Peer:
    """
    A class to represent a peer in a peer-to-peer (P2P) network.

    Attributes:
        host (str): The hostname or IP address of the peer. Defaults to '127.0.0.1'.
        port (int): The port number on which the peer listens for connections.
        server (socket.socket): The server socket for handling incoming connections.
        peers (list): A list of connected peer sockets.

    Methods:
        __init__(host='127.0.0.1', port=PORT):
            Initializes the Peer instance, sets up the server socket, and starts the server thread.

        start_server():
            Listens for incoming connections and spawns a thread to handle each connected peer.

        handle_peer(conn, addr):
            Handles communication with a connected peer, receives messages, and broadcasts them to other peers.

        broadcast(message, sender_conn):
            Sends a message to all connected peers except the sender.

        connect_to_peer(host, port):
            Connects to another peer in the network and starts a thread to listen for messages from it.

        listen_to_peer(client):
            Listens for messages from a connected peer and handles disconnection.

        send_message(message):
            Sends a message to all connected peers.
    """
    def __init__(self, host='127.0.0.1', port=PORT):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.peers = []
        threading.Thread(target=self.start_server).start()
        print(f"Peer iniciado em {host}:{port}")

    def start_server(self):
        try:
            while True:
                conn, addr = self.server.accept()
                print(f"Conexão recebida de {addr}")
                threading.Thread(target=self.handle_peer, args=(conn, addr)).start()
        except KeyboardInterrupt:
            print("Servidor encerrado.")
        finally:
            self.server.close()

    def handle_peer(self, conn, addr):
        self.peers.append(conn)
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Mensagem recebida de {addr}: {data}")
                self.broadcast(data, conn)
        except ConnectionResetError:
            print(f"Conexão perdida com {addr}")
        finally:
            conn.close()
            self.peers.remove(conn)

    def broadcast(self, message, sender_conn):
        for peer in self.peers:
            if peer != sender_conn:
                try:
                    peer.sendall(message.encode())
                except (BrokenPipeError, ConnectionResetError):
                    self.peers.remove(peer)

    def connect_to_peer(self, host, port):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((host, int(port)))
            self.peers.append(client)
            threading.Thread(target=self.listen_to_peer, args=(client,)).start()
            print(f"Conectado ao peer {host}:{port}")
        except ConnectionRefusedError:
            print(f"Falha ao conectar ao peer {host}:{port}")

    def listen_to_peer(self, client):
        try:
            while True:
                data = client.recv(1024).decode()
                if data:
                    print(f"Mensagem recebida: {data}")
        except ConnectionResetError:
            print("Conexão com o peer foi encerrada.")
        finally:
            client.close()
            self.peers.remove(client)

    def send_message(self, message):
        for peer in self.peers:
            try:
                peer.sendall(message.encode())
            except (BrokenPipeError, ConnectionResetError):
                self.peers.remove(peer)
