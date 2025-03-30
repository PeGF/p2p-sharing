import sys
import os
import socket
import threading
from clock import Clock
from Class import Peer

PEER = 0
PEERS = 1
ARQUIVOS = 2

def listar_arquivos(diretorio_compartilhado):
    arquivos = [f for f in os.listdir(diretorio_compartilhado) if os.path.isfile(os.path.join(diretorio_compartilhado, f))]
    # print("Arquivos:")
    print("")
    for arquivo in arquivos:
        print(f"{arquivo}")
        print()
    #return arquivos

def listar_peers(vizinhos_arquivo):
    peers = []
    with open(vizinhos_arquivo, "r") as f:
        for linha in f:
            endereco, porta = linha.strip().split(":")
            peers.append([endereco, int(porta), "OFFLINE"])
            print(f"Adicionando novo peer {endereco}:{porta} status OFFLINE")
    return peers

def validar_entrada(clock):
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

    peer = Peer(endereco, int(porta),clock)

    # arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    peer.peers_conhecidos(listar_peers(vizinhos_arquivo))

    # diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)

    # arquivos = listar_arquivos(diretorio_compartilhado)

    # print("Parametros Validos")

    config= [peer, diretorio_compartilhado]
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

def show_peers(clock, config):
    print("Lista de peers:")
    print("[0] voltar para o menu anterior")
    for peer in config[PEER].peers_conhecidos:
        print(f"[{config[PEER].peers_conhecidos.index(peer) + 1}] {peer[0]}:{peer[1]} {peer[2]}")

    comando = obter_comando(len(config[PEER].peers_conhecidos), True)

    if comando == 0:
        return

    peer_selecionado = config[PEER].peers_conhecidos[comando - 1]
    if peer_selecionado[2] != "ONLINE":
        conn = config[PEER].connect_to_peer(peer_selecionado[0], peer_selecionado[1])
        if conn:
            message = f"HELLO"
            config[PEER].send_message(peer_selecionado[0], peer_selecionado[1], message)
            
            try:
                config[PEER].peers[-1].settimeout(3)
                resposta = config[PEER].peers[-1].recv(1024).decode()
                if "HELLO" in resposta:
                    peer_selecionado = config[PEER].update_peer_status(peer_selecionado, "ONLINE")
            except socket.timeout:
                print(f"{peer_selecionado[0]}:{peer_selecionado[1]} não respondeu ao HELLO (timeout).")
            except Exception as e:
                print(f"Erro ao esperar resposta de {peer_selecionado[0]}:{peer_selecionado[1]} - {e}")

def desconectar_peers(config):
    for peer in config[PEER].peers_conhecidos:
        if peer[2] == "ONLINE":
            try:
                config[PEER].send_message(peer[0], peer[1], "BYE")
                print(f"Mensagem 'BYE' enviada para {peer[0]}:{peer[1]}")
            except Exception as e:
                print(f"Erro ao enviar 'BYE' para {peer[0]}:{peer[1]}: {e}")

    # Encerra todas as conexões e o servidor
    config[PEER].close_all_sockets()

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
                listar_arquivos(config[1])
            case 4:
                print("3")
            case 5:
                print(config)
                print(config)
            case 6:
                print(config[PEER])
            case 7:
                print(config[PEER].peers_conhecidos)
            case 8:
                print("8")
            case 9:
                print("Saindo...")
                desconectar_peers(config)
                print("Threads ativas:", threading.enumerate())
                sys.exit(0)
                break
def main():
    clock = Clock()
    config = validar_entrada(clock)
    menu(clock, config)
    return

if __name__ == "__main__":
    main()