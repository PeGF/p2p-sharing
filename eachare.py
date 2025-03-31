import sys
import os
import socket
import threading
from clock import Clock
from Class import Peer

def listar_arquivos(diretorio_compartilhado):
    arquivos = [f for f in os.listdir(diretorio_compartilhado) if os.path.isfile(os.path.join(diretorio_compartilhado, f))]
    # print("Arquivos:")
    print("")
    for arquivo in arquivos:
        print(f"{arquivo}")
        print()
    return arquivos

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

    peer = Peer(endereco, int(porta), clock)

    # arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    peer.peers_conhecidos(listar_peers(vizinhos_arquivo))

    # diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)
    peer.diretorio_compartilhado(diretorio_compartilhado)
    # arquivos = listar_arquivos(diretorio_compartilhado)

    # print("Parametros Validos")

    return peer

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

def show_peers(peer):
    print("Lista de peers:")
    print("[0] voltar para o menu anterior")
    for peer_conhecido in peer.peers_conhecidos:
        print(f"[{peer.peers_conhecidos.index(peer_conhecido) + 1}] {peer_conhecido[0]}:{peer_conhecido[1]} {peer_conhecido[2]}")

    comando = obter_comando(len(peer.peers_conhecidos), True)

    if comando == 0:
        return

    peer_selecionado = peer.peers_conhecidos[comando - 1]
    if peer_selecionado[2] != "ONLINE":
        conn = peer.connect_to_peer(peer_selecionado[0], peer_selecionado[1])
        if conn:
            message = f"HELLO"
            peer.send_message(peer_selecionado[0], peer_selecionado[1], message)
            
            try:
                peer.peers[-1].settimeout(3)
                resposta = peer.peers[-1].recv(1024).decode()
                if "HELLO" in resposta:
                    peer_selecionado = peer.update_peer_status(peer_selecionado, "ONLINE")
            except socket.timeout:
                print(f"{peer_selecionado[0]}:{peer_selecionado[1]} não respondeu ao HELLO (timeout).")
            except Exception as e:
                print(f"Erro ao esperar resposta de {peer_selecionado[0]}:{peer_selecionado[1]} - {e}")

def get_peers(peer):
    for peer in peer.peers_conhecidos:
        conn = peer.connect_to_peer(peer[0], peer[1])
        if conn:
            message = f"GET_PEERS"
            peer.send_message(peer[0], peer[1], message)

def menu(peer):
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
                show_peers(peer)
            case 2:
                print("2")	
            case 3:
                listar_arquivos(peer.diretorio_compartilhado)
            case 4:
                print("3")
            case 5:
                print(peer)
                print(peer)
            case 6:
                print(peer)
            case 7:
                print(peer.peers_conhecidos)
            case 8:
                print("8")
            case 9:
                print("Saindo...")
                for peer in peer.peers_conhecidos:
                    if peer[2] == "ONLINE":
                        peer.send_message(peer[0], peer[1], "BYE")
                return
def main():
    clock = Clock()
    config = validar_entrada(clock)
    menu(config)
    return

if __name__ == "__main__":
    main()