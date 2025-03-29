import sys
import os
import socket
import threading
from clock import Clock
from peers import Peer
PEER = 0
PEERS = 1
ARQUIVOS = 2

def listar_arquivos(diretorio_compartilhado):
    arquivos = [f for f in os.listdir(diretorio_compartilhado) if os.path.isfile(os.path.join(diretorio_compartilhado, f))]
    # print("Arquivos:")
    print("")
    for arquivo in arquivos:
        print(f"{arquivo}")
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

    peer = Peer(endereco, int(porta))

    # arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    peers = listar_peers(vizinhos_arquivo)

    # diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)

    # arquivos = listar_arquivos(diretorio_compartilhado)

    # print("Parametros Validos")

    config = [peer, peers, diretorio_compartilhado]
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
            conn = config[PEER].connect_to_peer(config[PEERS][comando - 1][0], config[PEERS][comando - 1][1])
            if conn:
                clock.incrementClock()
                message = f'Encaminhando mensagem "{config[PEER].host}:{config[PEER].port} 1 HELLO" para {config[PEERS][comando - 1][0]}:{config[PEERS][comando - 1][1]}'
                config[PEER].send_message(config[PEERS][comando - 1][0], config[PEERS][comando - 1][1], message)
                update_peer_status(config[PEERS][comando - 1], "ONLINE")
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
                listar_arquivos(config[ARQUIVOS])
            case 4:
                print("3")
            case 5:
                print(config)
            case 6:
                print(config[PEER])
            case 7:
                print(config[PEERS])
            case 8:
                print("8")
            case 9:
                break

def main():
    clock = Clock()
    config = validar_entrada()
    menu(clock, config)
    # TODO not terminating correctly

if __name__ == "__main__":
    main()