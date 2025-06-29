import threading
import base64
import socket
import time
import os

class Clock:
    def __init__(self):
        self.clock = 0  # Inicializa o relógio lógico com valor 0

    def incrementClock(self):
        self.clock += 1  # Incrementa o valor do relógio em 1
        print(f"=> Atualizando relogio para {self.clock}")

    def updateClock(self, received_clock=None):
        # Se o relógio recebido for None, usa o relógio local
        if received_clock is None:
            received_clock = self.clock
        # Atualiza o relógio local para o maior valor entre o local e o recebido
        self.clock = max(self.clock, received_clock)
        #print(f"=> Relógio atualizado para {self.clock} com base no valor recebido: {received_clock}")
        self.incrementClock()  # Incrementa o relógio após a atualização

class Peer:
    def __init__(self, host, port, clock):
        self.host = host
        self.port = port
        self.clock = clock
        self.file_list = []  # Lista de arquivos compartilhados
        self.chunk_size = 256
        self.chosen_file = None  # Arquivo escolhido para download
        self.file_parts = {}  # Dicionário para armazenar partes do arquivo
        self.peers_download = []
        self.download_stats = {} # {(chunk_size, n_peers, file_size): [tempos]}
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(10)
        # self.peers = # lista de peers conectados ativamente (e status), cada elemento é um objeto de socket
        threading.Thread(target=self.start_server, daemon=True).start()
        print(f"Peer iniciado em {host}:{port}")

    # armazena lista de infos sobre os peers conhecidos
    # lista: [endereço de ip, porta, status, clock]
    def set_peers_conhecidos(self, peers, vizinhos_arquivo):
        self.peers_conhecidos = []
        self.vizinhos_arquivo = vizinhos_arquivo
        for peer in peers:
            # formato [ip, porta, status, clock]
            if len(peer) == 3:
                peer.append(0)  # adiciona o clock inicial como 0
            self.peers_conhecidos.append(peer)

    def set_diretorio_compartilhado(self, diretorio):
        self.diretorio_compartilhado = diretorio

    # testar pra ver se o clock tá atualizando direito
    def print_peers_conhecidos(self):
        for peer in self.peers_conhecidos:
            print(f"Peer conhecido: {peer[0]}:{peer[1]} - Status: {peer[2]} - Clock: {peer[3]}")

    def update_peer_status(self, peer, status):
        peer[2] = status
        print(f"Atualizando peer {peer[0]}:{peer[1]} status {peer[2]}")
        return peer
    
    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port

    def get_peers_conhecidos(self):
        return self.peers_conhecidos
    
    def get_peers_online(self):
        peers_filtrados = [
            peer_conhecido for peer_conhecido in self.peers_conhecidos
            if (peer_conhecido[0] != self.get_host() or peer_conhecido[1] != self.get_port()) and peer_conhecido[2] == "ONLINE"
        ]
        return peers_filtrados
    
    def get_peers_conhecidos_formatado(self):
        result = ""
        for peer in self.peers_conhecidos:
            result += f"{peer[0]}:{peer[1]}:{peer[2]}:{peer[3]} "
        return result.strip()
    
    def get_peer_status(self, ip, port):
        for peer in self.get_peers_conhecidos():
            if peer[0] == ip and peer[1] == port:
                return peer[2]  # retorna o status
        return None  # retorna None se o peer não for encontrado
    
    def get_diretorio_compartilhado(self):
        return self.diretorio_compartilhado

    def get_chunk_size(self):
        return self.chunk_size
    
    def set_chunk_size(self, new_size):
        if new_size > 0:
            self.chunk_size = new_size
            return True
        return False

    def add_download_stat(self, chunk_size, n_peers, file_size, tempo):
        key = (chunk_size, n_peers, file_size)
        if key not in self.download_stats:
            self.download_stats[key] = []
        self.download_stats[key].append(tempo)

    def start_server(self):
        try:
            while True:
                conn, addr = self.server.accept()
                #print(f"Conexão recebida de {addr}")
                try:
                    # Recebe a mensagem e processa diretamente
                    data = conn.recv(1024).decode()
                    if data:
                        self.tratar_mensagem(data, conn)
                except ConnectionResetError:
                    print(f"Conexão perdida com {addr}")
                finally:
                    conn.close()  # Fecha a conexão imediatamente após o uso
        except KeyboardInterrupt:
            print("Servidor encerrado.")
        finally:
            self.server.close()

    def connect_to_peer(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                conn.connect((host, port))
            print(f"Conexão bem-sucedida com {host}:{port}")
            return True
        except ConnectionRefusedError:
            print(f"Falha ao conectar ao peer {host}:{port}")
            return False

    def tratar_mensagem(self, mensagem, conn):
        # Extrai o valor do relógio da mensagem recebida
        partes = mensagem.strip().split(" ")
        if len(partes) >= 2:  # ve se tem um valor de relógio na mensagem
            try:
                clock_mensagem = int(partes[1])  # o valor do relógio está na segunda parte da mensagem
                # atualiza o relógio local para o maior valor entre o local e o da mensagem
                self.clock.updateClock(clock_mensagem)

                # Atualiza o clock do peer correspondente em self.peers_conhecidos
                ip_port = partes[0].split(":")  # Extrai o IP e a porta do peer remetente
                ip = ip_port[0]
                port = int(ip_port[1])

                for peer in self.peers_conhecidos:
                    if peer[0] == ip and peer[1] == port:
                        if clock_mensagem > peer[3]:  # Compara o clock recebido com o salvo
                            peer[3] = clock_mensagem  # Atualiza o clock salvo
                            #print(f"clock do peer {ip}:{port} atualizado: {clock_mensagem}")
                        break
            except ValueError:
                print("Erro ao interpretar o valor do relógio na mensagem.")

        # só mostra a mensagem se tiver algo nela
        if mensagem.strip() != "":
            print(f'Mensagem recebida: "{mensagem.strip()}"')

        ip = partes[0].split(":")

        if len(partes) >= 3:
            if partes[2] == "HELLO":
                mensagem = f"{self.host}:{self.port} {self.clock.clock} RETURN_HELLO"
                self.reply(mensagem, conn)
                # verifica se o peer é conhecido e adiciona caso não seja
                peer_found = False
                for peer in self.peers_conhecidos:
                    if peer[0] == ip[0] and peer[1] == int(ip[1]):
                        peer_found = True
                        peer = self.update_peer_status(peer, "ONLINE")
                        break
                if not peer_found:
                    self.add_peer([ip[0], int(ip[1]), "ONLINE"])
                    self.escrever_peers(self.get_peers_conhecidos(), self.vizinhos_arquivo)

            elif partes[2] == "GET_PEERS":
                mensage = f"{self.host}:{self.port} {self.clock.clock} PEER_LIST {len(self.peers_conhecidos)} {self.get_peers_conhecidos_formatado()}"
                self.reply(mensage, conn)
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
                    ip_recebido = peers_recebidos[0]
                    porta_recebida = int(peers_recebidos[1])
                    status_recebido = peers_recebidos[2]
                    clock_recebido = int(peers_recebidos[3])  # Clock recebido do peer

                    if ip_recebido == self.host and porta_recebida == self.port:
                        # Ignora o próprio peer
                        continue

                    for peer in self.peers_conhecidos:
                        if peer[0] == ip_recebido and peer[1] == porta_recebida:
                            conhecido = True
                            # Atualiza o clock do peer conhecido com o maior valor
                            peer[3] = max(peer[3], clock_recebido)
                            break

                    if not conhecido:
                        # Adiciona o peer com o clock recebido
                        self.add_peer([ip_recebido, porta_recebida, status_recebido, clock_recebido])

                # Salva a lista atualizada de peers conhecidos
                self.escrever_peers(self.get_peers_conhecidos(), self.vizinhos_arquivo)

            elif partes[2] == "BYE":
                for peer in self.peers_conhecidos:
                    if peer[0] == ip[0] and peer[1] == int(ip[1]):
                        peer = self.update_peer_status(peer, "OFFLINE")
                        #mensage = f"{self.host}:{self.port} {self.clock.clock} RETURN_BYE"
                        #self.reply(mensage, conn)


            elif partes[2] == "LS":
                try:
                    # Lista os arquivos no diretório compartilhado com seus tamanhos
                    arquivos = [
                        (f, os.path.getsize(os.path.join(self.diretorio_compartilhado, f)))
                        for f in os.listdir(self.diretorio_compartilhado)
                        if os.path.isfile(os.path.join(self.diretorio_compartilhado, f))
                    ]
                    # Formata a lista de arquivos para o cabeçalho
                    arquivos_formatados = " ".join([f"{nome}:{tamanho}" for nome, tamanho in arquivos])
                    mensage = f"{self.host}:{self.port} {self.clock.clock} LS_LIST {len(arquivos)} {arquivos_formatados}"
                    self.reply(mensage, conn)
                except FileNotFoundError:
                    mensage = f"{self.host}:{self.port} {self.clock.clock} Diretório não encontrado"
                    self.reply(mensage, conn)


            elif partes[2] == "LS_LIST":
                # pega os arquivos
                arquivos_recebidos = partes[4:]
                self.file_list.append([arquivos_recebidos, (f"{ip[0]}:{ip[1]}")])

                if len(self.file_list) == len(self.get_peers_online()):
                    escolha = exibir_menu_arquivos(self.file_list)

                    if escolha == 0:
                        self.file_list = []  # Limpa a lista de arquivos
                        return
                    else:
                        # ['file.txt:49', ['127.0.0.1:5001', '127.0.0.1:5002']]
                        arquivo, peers = escolha
                        self.chosen_file = arquivo
                        nome_arquivo, tamanho_arquivo = arquivo.split(":")
                        tamanho_arquivo = int(tamanho_arquivo)
                        quant_chunks = tamanho_arquivo // self.chunk_size + (1 if tamanho_arquivo % self.chunk_size > 0 else 0)
                        quant_peers = len(peers)

                        # pedir o chunk para cada peer
                        idx = 0
                        while idx < quant_chunks:
                            # calcula o peer que vai receber o chunk
                            peer_idx = idx % quant_peers
                            peer = peers[peer_idx]
                            ip = peer.split(":")
                            mensagem = f"DL {nome_arquivo} {self.chunk_size} {idx}"
                            self.send_message(ip[0], int(ip[1]), mensagem)
                            idx += 1
                            self.file_list = []  # Limpa a lista de arquivos

            elif partes[2] == "DL":
                arquivo = partes[3].split(":")[0]
                size_chunk = partes[4]
                chunk_part = partes[5]
                caminho_arquivo = os.path.join(self.diretorio_compartilhado, arquivo)
                arquivo_codificado = codificar_base64(caminho_arquivo, size_chunk, chunk_part)
                mensage = f"{self.host}:{self.port} {self.clock.clock} FILE {arquivo} {size_chunk} {chunk_part} {arquivo_codificado}"
                if conn: 
                    self.reply(mensage, conn)
                else:
                    print("[tratar_mensagem][DL] Erro ao enviar mensagem para o peer, conexão não estabelecida.")

            elif partes[2] == "FILE":

                nome_arquivo = partes[3]
                tamanho_chunk = int(partes[4])
                parte_chunk = int(partes[5])
                conteudo_codificado = partes[6]

                tamanho_arquivo = int(self.chosen_file.split(":")[1])
                quant_chunks = tamanho_arquivo // tamanho_chunk + (1 if tamanho_arquivo % tamanho_chunk > 0 else 0)
                peer = f"{ip[0]}:{ip[1]}"
                if peer not in self.peers_download:
                    self.peers_download.append(peer)

                # Início da medição de tempo
                if not hasattr(self, 'download_start_time') or self.download_start_time is None:
                    self.download_start_time = time.perf_counter()

                # transforma em binário
                conteudo_binario = base64.b64decode(conteudo_codificado)
                self.file_parts[parte_chunk] = conteudo_binario

                if len(self.file_parts) == quant_chunks:

                    # Fim da medição de tempo
                    download_end_time = time.perf_counter()
                    tempo_download = download_end_time - self.download_start_time

                    arquivo_binario = b""
                    for i in range(quant_chunks):
                        arquivo_binario += self.file_parts.get(i, b"")
                    
                    # salva o arquivo no diretório compartilhado
                    caminho_arquivo = os.path.join(self.diretorio_compartilhado, nome_arquivo)

                    try:
                        with open(caminho_arquivo, "wb") as arquivo:
                            arquivo.write(arquivo_binario)

                        print(f"Download do arquivo {nome_arquivo} finalizado.")
                        print()

                        n_peers = len(self.peers_download)
                        self.add_download_stat(tamanho_chunk, n_peers, tamanho_arquivo, tempo_download)

                    except Exception as e:
                        print(f"[tratar_mensagem][FILE] Erro ao salvar o arquivo {nome_arquivo}: {e}")

                    finally:
                        self.chosen_file = None
                        self.file_parts = {}
                        self.download_start_time = None 
                        self.peers_download = []  # Limpa a lista de peers que participaram do download
                

            elif partes[2] == "RETURN_HELLO":
                for peer in self.peers_conhecidos:
                    if peer[0] == ip[0] and peer[1] == int(ip[1]):
                        peer = self.update_peer_status(peer, "ONLINE")
                        break

        else:
            if len(partes) >= 3 and partes[2] == "RETURN_HELLO":
                for peer in self.peers_conhecidos:
                    if peer[0] == ip[0] and peer[1] == int(ip[1]):
                        peer = self.update_peer_status(peer, "ONLINE")
                        break

    def send_message(self, host, port, message, timeout=5):
        self.clock.updateClock()
        mensagem_formatada = f"{self.host}:{self.port} {self.clock.clock} {message}\n"
        print(f'Encaminhando mensagem "{mensagem_formatada.strip()}" para {host}:{port}')

        try:
            # Cria uma nova conexão temporária
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn:
                conn.settimeout(timeout)
                conn.connect((host, port))
                conn.sendall(mensagem_formatada.encode())

                # Recebe a resposta
                response = conn.recv(1024).decode()
                self.tratar_mensagem(response, conn)
        except socket.timeout:
            print(f"Timeout ao enviar mensagem para {host}:{port}")
        except (BrokenPipeError, ConnectionResetError) as e:
            print(f"Erro ao enviar mensagem para {host}:{port}: {e}")
    
    def reply(self, message, conn):
        try:
            conn.sendall(message.encode())
        except (BrokenPipeError, ConnectionResetError):
            print("Erro ao enviar resposta.")

    def add_peer(self, peer):
        peer.append(0)
        self.peers_conhecidos.append(peer)

    def escrever_peers(self, peers, vizinhos_arquivo):
        # lê os peers existentes no arquivo
        try:
            with open(vizinhos_arquivo, "r") as f:
                peers_existentes = {line.strip() for line in f.readlines()}
        except FileNotFoundError:
            peers_existentes = set()

        # adiciona apenas os novos peers
        with open(vizinhos_arquivo, "a") as f:
            for peer in peers:
                peer_str = f"{peer[0]}:{peer[1]}"
                if peer_str not in peers_existentes:
                    f.write(f"{peer_str}\n")
                    peers_existentes.add(peer_str) 

def exibir_menu_arquivos(lista_arquivos: list):
    # lista_arquivos = [(nome_arquivo, (peer))]
    arquivos_recebidos = {}
    # if nome e tamanho iguais para arquivos de peers diferentes
    for idx, arquivo in enumerate(lista_arquivos, start=1):
        files = arquivo[0]
        peer = arquivo[1]
        for file in files:
            if arquivos_recebidos.get(f"{file}"):
                arquivos_recebidos[f"{file}"].append(peer)
            else:
                arquivos_recebidos[f"{file}"] = [peer]

    # Debug
    print(lista_arquivos)
    print(arquivos_recebidos)


    # larguras do menu
    largura_nome = 30
    largura_tamanho = 10
    largura_peer = 20

    # cabeçalho
    print()
    print("Arquivos encontrados na rede:")
    print()
    print(f"{'Nome'.center(largura_nome)}|{'Tamanho'.center(largura_tamanho)}|{'Peer'.center(largura_peer)}")
    print("-" * (largura_nome + largura_tamanho + largura_peer + 2))

    # menu
    print(f"{'[0] Cancelar'.ljust(largura_nome)}|{' '.ljust(largura_tamanho)}|{' '.ljust(largura_peer)}")
    nome_arquivos = arquivos_recebidos.keys()

    for idx, arquivo in enumerate(nome_arquivos, start=1):
        nome, tamanho = arquivo.split(":")
        peers = arquivos_recebidos.get(arquivo)
        peer = ", ".join(peers)
        print(f"[{idx}] {nome.ljust(largura_nome - len(f'[{idx}] '))}|{tamanho.ljust(largura_tamanho)}|{peer.ljust(largura_peer)}")

    print()
    print("Digite o numero do arquivo para fazer o download:")
    
    # escolha do arquivo
    escolha = ""
    while escolha not in range(0, len(arquivos_recebidos) + 1):
        try:
            escolha = int(input("> ").strip())
        except ValueError:
            pass

    escolha = escolha - 1  # Ajusta para o índice da lista
    if escolha == -1:
        return 0  # Cancelar
    else:
        # Retorna o nome do arquivo e os peers associados
        arquivo_escolhido = list(arquivos_recebidos.keys())[escolha]
        return [arquivo_escolhido, arquivos_recebidos[arquivo_escolhido]]  


def codificar_base64(caminho_arquivo, size_chunk, chunk_part):
    try:
        inicio = int(chunk_part) * int(size_chunk)
        # abre o arquivo em baixo nivel
        with open(caminho_arquivo, "rb") as arquivo:
            arquivo.seek(inicio)
            # le o conteúdo do arquivo
            conteudo = arquivo.read(int(size_chunk))
            
            # codifica o conteúdo em base64
            conteudo_base64 = base64.b64encode(conteudo)
            return conteudo_base64.decode('utf-8')  # retorna como string
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return None
    except Exception as e:
        print(f"Erro ao ler ou codificar o arquivo: {e}")
        return None