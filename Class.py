import socket
import threading

class Clock:
    def __init__(self):
        self.clock = 0

    def incrementClock(self):
        self.clock += 1
        print(f"=> Atualizando relogio para {self.clock}")


class Peer:
    def __init__(self, host, port, clock):
        self.host = host
        self.port = port
        self.clock = clock
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(10)
        self.peers = [] # lista de peers conectados ativamente (e status), cada elemento é um objeto de socket
        threading.Thread(target=self.start_server).start()
        print(f"Peer iniciado em {host}:{port}")

    # armazena lista de infos sobre os peers conhecidos
    # lista: [endereço de ip, porta, status]
    def peers_conhecidos(self, peers, vizinhos_arquivo): 
        self.peers_conhecidos = peers
        self.vizinhos_arquivo = vizinhos_arquivo

    def add_peer(self, peer):
        self.peers_conhecidos.append(peer)

    def diretorio_compartilhado(self, diretorio):
        self.diretorio_compartilhado = diretorio

    def update_peer_status(self, peer, status):
        peer[2] = status
        if status == "ONLINE":
            print(f"Atualizando peer {peer[0]}:{peer[1]} status {peer[2]}")
        return peer
    
    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port

    def get_peers_conhecidos(self):
        return self.peers_conhecidos
    
    def get_peers_conhecidos_formatado(self):
        result = ""
        for peer in self.peers_conhecidos:
            result += f"{peer[0]}:{peer[1]}:{peer[2]}:0 "
        return result.strip()
    
    def get_peer_status(self, ip, port):
        for peer in self.get_peers_conhecidos():
            if peer[0] == ip and peer[1] == port:
                return peer[2]  # retorna o status
        return None  # retorna None se o peer não for encontrado
    
    def get_peers(self):
        return self.peers
    
    def get_diretorio_compartilhado(self):
        return self.diretorio_compartilhado

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

    def escrever_peers(self, peers, vizinhos_arquivo):
        # sobrescreve o arquivo todo, pois o conteudo da memoria ja foi atualizado corretamente (teoricamente)
        # se fosse adicionar apenas os novos, teria que fazer checagem se ja existe e add apenas os novos, entao assim parece mais simples
        with open(vizinhos_arquivo, "w") as f:
            for peer in peers:
                f.write(f"{peer[0]}:{peer[1]}\n")
                #print(f"Adicionando peer {peer[0]}:{peer[1]}")

    def tratar_mensagem(self, mensagem, conn):
        if not "RETURN" in mensagem:
            print(f'Mensagem recebida: "{mensagem.strip()}"')
            self.clock.incrementClock()
            partes = mensagem.strip().split(" ")
            ip = partes[0].split(":")
            if len(partes) >= 3:

                if partes[2] == "HELLO":
                    mensagem = f"{self.host}:{self.port} {self.clock.clock} RETURN_HELLO"
                    self.broadcast(mensagem, conn)
                    # verifica se o peer é conhecido e adiciona caso n seja
                    peer_found = False
                    for peer in self.peers_conhecidos:
                        if peer[0] == ip[0] and peer[1] == int(ip[1]):
                            peer_found = True
                            peer = self.update_peer_status(peer, "ONLINE")
                            break
                    if not peer_found:
                        self.add_peer([ip[0], int(ip[1]), "ONLINE"])

                elif partes[2] == "GET_PEERS":
                    mensage = f"{self.host}:{self.port} {self.clock.clock} PEER_LIST {len(self.peers_conhecidos)} {self.get_peers_conhecidos_formatado()}"
                    self.broadcast(mensage, conn)
                    peer_found = False
                    for peer in self.peers_conhecidos:
                        if peer[0] == ip[0] and peer[1] == int(ip[1]):
                            peer_found = True
                            peer = self.update_peer_status(peer, "ONLINE")
                            break
                    if not peer_found:
                        self.add_peer([ip[0], int(ip[1]), "ONLINE"])

                elif partes[2] == "PEER_LIST":
                    quant = int(partes[3])
                    for i in range(quant):
                        conhecido = False
                        peers_recebidos = partes[4 + i].split(":")
                        for peer in self.peers_conhecidos:
                            if peer[0] == peers_recebidos[0] and peer[1] == int(peers_recebidos[1]):
                                conhecido = True
                                break
                        if not conhecido:
                            self.add_peer([peers_recebidos[0], int(peers_recebidos[1]), peers_recebidos[2]])
                    self.escrever_peers(self.get_peers_conhecidos(), self.vizinhos_arquivo)
                elif partes[2] == "BYE":
                    for peer in self.peers_conhecidos:
                        if peer[0] == ip[0] and peer[1] == int(ip[1]):
                            peer = self.update_peer_status(peer, "OFFLINE")
                            mensage = f"{self.host}:{self.port} {self.clock.clock} RETURN_BYE"
                            self.broadcast(mensage, conn)
        else:
            partes = mensagem.strip().split(" ")
            ip = partes[0].split(":")
            if len(partes) >= 3:
                if partes[2] == "RETURN_HELLO":
                    for peer in self.peers_conhecidos:
                        if peer[0] == ip[0] and peer[1] == int(ip[1]):
                            peer = self.update_peer_status(peer, "ONLINE")
                            break

    def handle_peer(self, conn, addr):
        self.peers.append(conn)
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                self.tratar_mensagem(data, conn)
        except ConnectionResetError:
            print(f"Conexão perdida com {addr}")
        finally:
            conn.close()
            self.peers.remove(conn)

    def broadcast(self, message, conn):
        for peer in self.peers:
            if peer == conn:
                try:
                    peer.sendall(message.encode())
                except (BrokenPipeError, ConnectionResetError):
                    self.peers.remove(peer)

    def connect_to_peer(self, host, port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            conn.connect((host, int(port)))
            self.peers.append(conn)
            threading.Thread(target=self.listen_to_peer, args=(conn,)).start()
            #print(f"Conectado ao peer {host}:{port}")
            return True
        except ConnectionRefusedError:
            #print(f"Falha ao conectar ao peer {host}:{port}")
            return False

    def listen_to_peer(self, conn):
        try:
            while True:
                data = conn.recv(1024).decode()
                
                if data:
                    self.tratar_mensagem(data, conn)
        except ConnectionResetError:
            print("Conexão com o peer foi encerrada.")
        finally:
            conn.close()
            if conn in self.peers:
                self.peers.remove(conn)


    def send_message(self, host, port, message, timeout=5):
        self.clock.incrementClock() # incrementa o clock
        # host, porta e clock
        mensagem_formatada = f"{self.host}:{self.port} {self.clock.clock} {message}\n"
        
        print(f'Encaminhando mensagem "{mensagem_formatada.strip()}" para {host}:{port}')
        
        for peer in self.peers:
            try:
                if peer.getpeername() == (host, port):
                    peer.sendall(mensagem_formatada.encode())
                    # Wait for a response
                    peer.settimeout(timeout)  # Set a timeout for the response
                    response = peer.recv(1024).decode()  # Receive and decode the response
                    
                    # Handle the response
                    self.tratar_mensagem(response, peer)
            except socket.timeout:
                print(f"Timeout ao enviar mensagem para {host}:{port}")
            except (BrokenPipeError, ConnectionResetError):
                self.peers.remove(peer)
        return None
    
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