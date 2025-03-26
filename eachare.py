import sys
import os
import socket
import threading
import socket
import threading
from clock import Clock

ENDERECO = 0
PORTA = 1
PEERS = 2
ARQUIVOS = 3

def handle_client(cliente, endereco_cliente):
    try:
        mensagem = cliente.recv(1024).decode("utf-8")
        print(f"Mensagem recebida de {endereco_cliente}: {mensagem}")

        # Verifica se a mensagem é um HELLO
        partes = mensagem.split()
        if len(partes) >= 3 and partes[2] == "HELLO":
            receive_hello(config, partes[0])  # O remetente é partes[0] (endereço:porta)
            cliente.sendall(b"HELLO recebido!\n")  # Responder ao peer

    except Exception as e:
        print(f"Erro ao processar mensagem de {endereco_cliente}: {e}")

    finally:
        cliente.close()

def aceita_conexoes(servidor):
    while True:
        try:
            cliente, endereco_cliente = servidor.accept()
            print(f"Conexão recebida de {endereco_cliente}")
            thread = threading.Thread(target=handle_client, args=(cliente, endereco_cliente))
            thread.daemon = True  # Permite que o programa encerre mesmo com threads abertas
            thread.start()
        except Exception as e:
            print(f"Erro ao aceitar conexão: {e}")
            break

def inicia_servidor(endereco, porta):
    try:
        # Cria o socket TCP
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Associa o socket ao endereço e porta
        servidor.bind((endereco, porta))
        # print(f"Servidor iniciado em {endereco}:{porta}")

        # Coloca o socket em modo de escuta
        servidor.listen(5)
        # print("Aguardando conexões...")


        thread = threading.Thread(target=aceita_conexoes, args=(servidor,))
        thread.start()

    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)

def listar_arquivos(diretorio_compartilhado):
    arquivos = [f for f in os.listdir(diretorio_compartilhado) if os.path.isfile(os.path.join(diretorio_compartilhado, f))]
    # print("Arquivos:")
    for arquivo in arquivos:
        print(f"- {arquivo}")
    return arquivos

def listar_peers(vizinhos_arquivo):
    peers = []
    with open(vizinhos_arquivo, "r") as f:
        for linha in f:
            endereco, porta = linha.strip().split(":")
            peers.append([endereco, int(porta), "OFFLINE"])
            print(f"Adicionando novo peer {endereco}:{porta} status OFFLINE")
    return peers

def validar_entrada():
    if len(sys.argv) != 4:
        print("Formato: python eachare.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
        sys.exit(1)

    endereco_porta = sys.argv[1]
    vizinhos_arquivo = sys.argv[2]
    diretorio_compartilhado = sys.argv[3]

    # endereco
    if ":" not in endereco_porta:
        print("Formato: <endereço>:<porta>")
        sys.exit(1)

    endereco, porta = endereco_porta.split(":")
    
    # porta
    if not porta.isdigit():
        print("Formato da porta incorreto")
        sys.exit(1)

    inicia_servidor(endereco, int(porta))

    # arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    peers = listar_peers(vizinhos_arquivo)

    # diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)

    arquivos = listar_arquivos(diretorio_compartilhado)

    # print("Parametros Validos")

    config = [endereco, porta, peers, arquivos]
    return config

def obter_comando(n, zero:bool):
    comando_escolhido = ""
    if zero:
        while comando_escolhido not in [i for i in range(0, n + 1) ]:
            try:
                comando_escolhido = int(input("> ").strip())
            except ValueError:
                pass
    else:
        while comando_escolhido not in [i for i in range(1, n + 1) ]:
            try:
                comando_escolhido = int(input("> ").strip())
            except ValueError:
                pass
    return comando_escolhido

def update_peer_status(peer, status):
    peer[2] = status
    print(f"Atualizando peer {peer[0]}:{peer[1]} status {peer[2]}")
    return peer

def enviar_mensagem(peer, mensagem):
    try:
        # socket TCP
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.settimeout(2)  # Evita que o socket trave indefinidamente

        # conectar ao peer
        endereco, porta = peer[0], peer[1]
        cliente.connect((endereco, porta))

        # envia mensagem
        cliente.sendall(mensagem.encode("utf-8"))

        # recebe repsosta
        resposta = cliente.recv(1024).decode("utf-8")
        print(f"📩 Resposta recebida de {endereco}:{porta}: {resposta}")

        cliente.close()
        return True  # deu certo

    except Exception as e:
        print(f"⚠ Erro ao enviar mensagem para {peer[0]}:{peer[1]} → {e}")
        return False  # n deu certo

def send_hello(clock, config, index):   
    # incrementa o clock 
    clock.incrementClock()
    print(f"=> Atualizando relógio para {clock.clock}")

    peer = config[PEERS][index]
    mensagem = f"{config[ENDERECO]}:{config[PORTA]} {clock.clock} HELLO"

    print(f'Mensagem "{mensagem}" para {peer[0]}:{peer[1]}')

    if enviar_mensagem(peer, mensagem):
        config[PEERS][index] = update_peer_status(peer, "ONLINE")
    else:
        config[PEERS][index] = update_peer_status(peer, "OFFLINE")

def receive_hello(clock, config, peer_endereco):
    print(f"Mensagem recebida: {peer_endereco} HELLO")

    # incrementa o clock ao receber a mensagem
    clock.incrementClock()
    print(f"=> Atualizando relógio para {clock.clock}")

    endereco, porta = peer_endereco.split(":")
    porta = int(porta)

    # verifica se o peer já está na lista
    for peer in config[PEERS]:
        if peer[0] == endereco and peer[1] == porta:
            update_peer_status(peer, "ONLINE")
            return

    # se o peer não está na lista, adiciona
    novo_peer = [endereco, porta, "ONLINE"]
    config[PEERS].append(novo_peer)
    print(f"Novo peer descoberto: {endereco}:{porta} (ONLINE)")

def show_peers(clock, config):
    print("Lista de peers:")
    print("[0] voltar para o menu anterior")
    for peer in config[PEERS]:
        print(f"[{config[PEERS].index(peer) + 1}] {peer[0]}:{peer[1]} {peer[2]}")
    comando = obter_comando(len(config[PEERS]), True)
    match comando:
        case 0:
            return
        case _:
            send_hello(clock, config, comando - 1)

def menu(clock, config):
    while True:
        print("Escolha um comando:")
        print("[1] Listar peers")
        print("[2] Obter peers")
        print("[3] Listar arquivos locais")
        print("[4] Buscar arquivos")
        print("[5] Exibir estatisticas")
        print("[8] Alterar tamanho de chunk")
        print("[9] Sair")
        comando = obter_comando(9, False)
        match comando:
            case 1:
                show_peers(clock, config)
            case 2:
                print("2")	
            case 3:
                print(config)
            case 4:
                print("3")
            case 5:
                print("3")
            case 6:
                print("3")
            case 7:
                print("3")
            case 8:
                print("3")
            case 9:
                break


def main():
    clock = Clock()
    config = validar_entrada()
    menu(clock, config)
    # TODO not terminating correctly

if __name__ == "__main__":
    main()
