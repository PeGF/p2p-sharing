import sys
import os
import time
from Class import Clock, Peer

# atualizei essa função pra tbm listar o tamanho dos arquivos, só pra ficar mais coerente com a outra parte do código
# e tbm adicionei um tratamento de erro caso o diretório não exista / nao tenha arquivos
def listar_arquivos(diretorio_compartilhado):
    try:
        arquivos = [
            (f, os.path.getsize(os.path.join(diretorio_compartilhado, f)))
            for f in os.listdir(diretorio_compartilhado)
            if os.path.isfile(os.path.join(diretorio_compartilhado, f))
        ]
        print("")
        for arquivo, tamanho in arquivos:
            print(f"{arquivo} - {tamanho} bytes")
            print()
        return arquivos
    except FileNotFoundError:
        print(f"Diretório {diretorio_compartilhado} não encontrado.")
        return []

def listar_peers(vizinhos_arquivo):
    peers = []
    with open(vizinhos_arquivo, "r") as f:
        for linha in f:
            try:
                endereco, porta = linha.strip().split(":")
                if not porta.isdigit():
                    raise ValueError("Porta não é um número")
                peers.append([endereco, int(porta), "OFFLINE"])
                print(f"Adicionando novo peer {endereco}:{porta} status OFFLINE")
            except ValueError:
                continue
    return peers

def validar_entrada(clock):
    if len(sys.argv) != 4:
        print("Formato: python3 eachare.py <endereço>:<porta> <vizinhos.txt> <diretório_compartilhado>")
        sys.exit(1)

    endereco_porta = sys.argv[1]
    vizinhos_arquivo = sys.argv[2]
    diretorio_compartilhado = sys.argv[3]

    #endereco
    if ":" not in endereco_porta:
        print("Formato: <endereço>:<porta>")
        sys.exit(0)

    endereco, porta = endereco_porta.split(":")
    
    #porta
    if not porta.isdigit():
        print("Formato da porta incorreto")
        sys.exit(0)

    #arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Arquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(0)

    #diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(0)
    
    #arquivos = listar_arquivos(diretorio_compartilhado)
    #print("Parametros Validos")

    peer = Peer(endereco, int(porta), clock)
    peer.set_peers_conhecidos(listar_peers(vizinhos_arquivo), vizinhos_arquivo)
    peer.set_diretorio_compartilhado(diretorio_compartilhado)

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
        conn = peer.connect_to_peer(peers_filtrados[comando - 1][0], peers_filtrados[comando - 1][1])
        if conn:  # Verifica se a conexão foi bem-sucedida
            peer.send_message(peers_filtrados[comando - 1][0], peers_filtrados[comando - 1][1], "HELLO")
        else:
            return

def get_peers(peer):
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if (peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()) and peer_conhecido[2]
    ]
    for peer_conhecido in peers_filtrados:
        conn = peer.connect_to_peer(peer_conhecido[0], peer_conhecido[1])
        if conn:
            message = f"GET_PEERS"
            peer.send_message(peer_conhecido[0], peer_conhecido[1], message)
            peer.update_peer_status(peer_conhecido, "ONLINE")
        else:
            peer.update_peer_status(peer_conhecido, "OFFLINE")

def list_files(peer):
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if (peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()) and peer_conhecido[2] == "ONLINE"
    ]
    for peer_conhecido in peers_filtrados:
        conn = peer.connect_to_peer(peer_conhecido[0], peer_conhecido[1])
        if conn:
            message = f"LS"
            peer.send_message(peer_conhecido[0], peer_conhecido[1], message)

def sair(peer):
    print("Saindo...")
    # Filtra os peers conhecidos que estão ONLINE
    peers_filtrados = [
        peer_conhecido for peer_conhecido in peer.peers_conhecidos
        if peer_conhecido[0] != peer.get_host() or peer_conhecido[1] != peer.get_port()
    ]
    message = "BYE"

    # Envia a mensagem BYE para cada peer conhecido
    for peer_conhecido in peers_filtrados:
        if peer_conhecido[2] == "ONLINE":  # Apenas para peers ONLINE
            conn = peer.connect_to_peer(peer_conhecido[0], peer_conhecido[1])
            if conn:
                peer.send_message(peer_conhecido[0], peer_conhecido[1], message)

    # Fecha o servidor e encerra o programa
    peer.server.close()
    time.sleep(5)  # Espera para garantir que as mensagens sejam processadas
    os._exit(1)

def menu(peer):
    while True:
        print("Escolha um comando:")
        print("[1] Listar peers")
        print("[2] Obter peers")
        print("[3] Listar arquivos locais")
        print("[4] Buscar arquivos")
        print("[5] Exibir estatisticas")
        print("[6] Alterar tamanho de chunk")
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
                list_files(peer)
            case 5:
                print("Não implementado")
            case 6:
                print("Não implementado")
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