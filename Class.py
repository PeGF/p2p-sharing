import socket
import threading
import os
import random as rd

PORT = rd.randint(1000, 6000)
class Server:
    def __init__(self, host='localhost', port=PORT):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.peers = []
        threading.Thread(target=self.start, daemon=True).start()

        print("Servidor iniciado. Esperando por conexões...\n")
        print(f"Servidor rodando em {host}:{port}")

    def start(self):
        while True:
            conn, addr = self.server.accept()
            if conn not in self.peers:
                # Adiciona o novo peer à lista de peers
                self.connect_to_peer(addr[0], addr[1])
                self.peers.append(conn)
            print(f"Novo jogador conectado: {addr}")
            threading.Thread(target=self.handle_player, args=(conn, addr), daemon=True).start()
        self.server.close()

    def handle_player(self, conn, addr):
        print(f"Jogador conectado: {addr}")
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print(f"Jogador enviou: {data}")
                self.broadcast(f"Jogador: {data}", current_conn=conn)
            except ConnectionResetError:
                break

        conn.close()

    def broadcast(self, message, current_conn=None):
        """
        Envia uma mensagem para todos os jogadores, exceto o remetente, se especificado.
        """
        for peer in self.peers:
            peer.sendall(message.encode())

    def connect_to_peer(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))

        threading.Thread(target=self.listen_for_messages, daemon=True).start()

        self.send_message()

    def send_message(self):
        while True:
            message = input()
            self.client.send(message.encode())

    def listen_for_messages(self):
        while True:
            try:
                msg = self.client.recv(1024).decode()
                if msg:
                    print(msg)
            except:
                print("Conexão encerrada.")
                self.client.close()
                break

