import sys
import os
from Class import Clock, Peer

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

    #endereco
    if ":" not in endereco_porta:
        print("Formato: <endereço>:<porta>")
        sys.exit(1)

    endereco, porta = endereco_porta.split(":")
    
    #porta
    if not porta.isdigit():
        print("Formato da porta incorreto")
        sys.exit(1)

    peer = Peer(endereco, int(porta), clock)

    #arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    peer.set_peers_conhecidos(listar_peers(vizinhos_arquivo), vizinhos_arquivo)

    #diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)
    peer.set_diretorio_compartilhado(diretorio_compartilhado)
    #arquivos = listar_arquivos(diretorio_compartilhado)
    #print("Parametros Validos")

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
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()
    ]
    for index, peer_conhecido in enumerate(peers_filtrados, start=1):
        print(f"[{index}] {peer_conhecido[0]}:{peer_conhecido[1]} {peer_conhecido[2]}")

    comando = obter_comando(len(peers_filtrados), True)

    if comando == 0:
        return
    else:
        peer.connect_to_peer(peers_filtrados[comando - 1][0], peers_filtrados[comando - 1][1])
        peer.send_message(peers_filtrados[comando - 1][0], peers_filtrados[comando - 1][1], "HELLO")

def get_peers(peer):
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()
    ]
    for peer_conhecido in peers_filtrados:
        conn = peer.connect_to_peer(peer_conhecido[0], peer_conhecido[1])
        if conn:
            message = f"GET_PEERS"
            peer.send_message(peer_conhecido[0], peer_conhecido[1], message)
            peer.update_peer_status(peer_conhecido, "ONLINE")
        else:
            peer.update_peer_status(peer_conhecido, "OFFLINE")

def sair(peer):
    print("Saindo...")
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if (peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()) and peer_conhecido[2] != "OFFLINE"
    ]
    peers_desconectados = []
    message = f"BYE"
    for peer_conhecido in peers_filtrados:
        for peer_conectado in peer.peers:
            ip = peer_conectado.getpeername()
            if ip[0] == peer_conhecido[0] and ip[1] == peer_conhecido[1]:
                peer.send_message(peer_conhecido[0], peer_conhecido[1], message)
            else:
                peers_desconectados.append(peer_conhecido)
    for peer in peers_desconectados:
        conn = peer.connect_to_peer(peer_conhecido[0], peer_conhecido[1])
        if conn:
            peer.send_message(peer_conhecido[0], peer_conhecido[1], message)
    peer.close_all_sockets()
    sys.exit(0)

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
                get_peers(peer)	
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
                sair(peer)
                break

def main():
    clock = Clock()
    config = validar_entrada(clock)
    menu(config)
    return

if __name__ == "__main__":
    main()