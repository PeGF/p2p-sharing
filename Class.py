import socket
import threading

class Peer:
    def __init__(self, host, port, clock):
        self.host = host
        self.port = port
        self.clock = clock
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(5)
        self.peers = []
        threading.Thread(target=self.start_server).start()
        print(f"Peer iniciado em {host}:{port}")

    def peers_conhecidos(self, peers):
        self.peers_conhecidos = peers

    def add_peer(self, peer):
        self.peers_conhecidos.append(peer)

    def diretorio_compartilhado(self, diretorio):
        self.diretorio_compartilhado = diretorio

    def update_peer_status(self, peer, status):
        peer[2] = status
        print(f"Atualizando peer {peer[0]}:{peer[1]} status {peer[2]}")
        return peer

    def start_server(self):
        try:
            while True:
                conn, addr = self.server.accept()
                # print(f"Conexão recebida de {addr}")
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
                if not "RETURN" in data:
                    print(f'Mensagem recebida: "{data.strip()}"')
                    self.clock.incrementClock()
                    partes = data.strip().split(" ")
                    if partes[2] == "HELLO":
                        ip = partes[0].split(":")
                        mensagem = f"{self.host}:{self.port} {self.clock.clock} RETURN_HELLO"
                        self.broadcast(mensagem, conn)
                        #  Atualiza o status do peer
                        for peer in self.peers_conhecidos:
                            if peer[0] == ip[0] and peer[1] == int(ip[1]):
                                peer = self.update_peer_status(peer, "ONLINE")
                    elif partes[2] == "BYE":
                        for peer in self.peers_conhecidos:
                            if peer[0] == ip[0] and peer[1] == int(ip[1]):
                                peer = self.update_peer_status(peer, "OFFLINE")

        except ConnectionResetError:
            print(f"Conexão perdida com {addr}")
        finally:
            conn.close()
            self.peers.remove(conn)

    def broadcast(self, message, sender_conn):
        for peer in self.peers:
            if peer == sender_conn:
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
            return True
        except ConnectionRefusedError:
            print(f"Falha ao conectar ao peer {host}:{port}")
            return False

    def listen_to_peer(self, client):
        try:
            while True:
                data = client.recv(1024).decode()
                
                if data:
                    if not "RETURN" in data:	
                        print(f'Mensagem recebida: {data.strip()}"')
                        # incrementa o clock ao receber a mensagem
                        self.clock.incrementClock()
                        # verifica se é hello e responde com outro hello
                        partes = data.strip().split(" ")
                        if len(partes) >= 3:
                            ip = partes[0].split(":")
                            if partes[2] == "HELLO":
                                print(f"Atualizando peer {partes[0]} status ONLINE")
                                resposta = f"RETURN_HELLO"
                                self.send_message(ip[0], ip[1], resposta.encode())
                            elif partes[2] == "BYE":
                                for peer in self.peers_conhecidos:
                                    if peer[0] == ip[0] and peer[1] == int(ip[1]):
                                        peer = self.update_peer_status(peer, "OFFLINE")

                    else:
                        partes = data.strip().split(" ")
                        if len(partes) >= 3:
                            if partes[2] == "RETURN_HELLO":
                                print("online")
        except ConnectionResetError:
            print("Conexão com o peer foi encerrada.")
        finally:
            client.close()
            if client in self.peers:
                self.peers.remove(client)


    def send_message(self, host, port, message):
        self.clock.incrementClock() # incrementa o clock
        # host, porta e clock
        mensagem_formatada = f"{self.host}:{self.port} {self.clock.clock} {message}\n"
        
        print(f'Encaminhando mensagem "{mensagem_formatada.strip()}" para {host}:{port}')
        
        for peer in self.peers:
            try:
                if peer.getpeername() == (host, port):
                    peer.sendall(mensagem_formatada.encode())
            except (BrokenPipeError, ConnectionResetError):
                self.peers.remove(peer)

    def close_all_sockets(self):
        """Closes all active sockets and the server socket."""
        for peer in self.peers:
            try:
                peer.close()
            except Exception as e:
                print(f"Erro ao fechar conexão com peer: {e}")
        self.peers.clear()
        try:
            self.server.close()
        except Exception as e:
            print(f"Erro ao fechar o servidor: {e}")