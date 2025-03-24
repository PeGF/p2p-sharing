import sys
import os
import socket
import threading
from clock import Clock

ENDERECO = 0
PORTA = 1
PEERS = 2
ARQUIVOS = 3

def handle_client(cliente, endereco_cliente):
    """Função para lidar com a conexão de um cliente."""
    try:
        print(f"Conexão recebida de {endereco_cliente}")
        # Aqui você pode adicionar lógica para comunicação com o cliente
        cliente.sendall(b"Bem-vindo ao servidor!\n")
    except Exception as e:
        print(f"Erro ao lidar com o cliente {endereco_cliente}: {e}")
    finally:
        cliente.close()

def aceita_conexoes(servidor):
    """Função para aceitar conexões em uma thread separada."""
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

def send_hello(clock, config, index):
    clock.incrementClock()
    print(f'Encaminhando mensagem "{config[ENDERECO]}:{config[PORTA]} 1 HELLO" para {config[PEERS][index][0]}:{config[PEERS][index][1]}')
    # TODO send message to peer
    config[PEERS][index][2] = "ONLINE"
    print(f"Peer {config[PEERS][index][0]}:{config[PEERS][index][1]} status ONLINE")

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
