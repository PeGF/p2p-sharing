import sys
import os
import socket

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

    # arquivo vizinhos
    if not os.path.isfile(vizinhos_arquivo):
        print(f"Asrquivo de vizinhos '{vizinhos_arquivo}' não encontrado")
        sys.exit(1)

    # diretorio compartilhafdo
    if not os.path.isdir(diretorio_compartilhado):
        print(f"Diretorio {diretorio_compartilhado} nao encontrado")
        sys.exit(1)

    print("Parametros Validos")

    return endereco, int(porta), vizinhos_arquivo, diretorio_compartilhado


def listar_arquivos(diretorio_compartilhado):
    arquivos = [f for f in os.listdir(diretorio_compartilhado) if os.path.isfile(os.path.join(diretorio_compartilhado, f))]
    print("Arquivos:")
    for arquivo in arquivos:
        print(f"- {arquivo}")
    return arquivos

def listar_peers(vizinhos_arquivo):
    peers = []
    with open(vizinhos_arquivo, "r") as f:
        for linha in f:
            endereco, porta = linha.strip().split(":")
            peers.append((endereco, int(porta), "OFFLINE"))
            
    return peers


def criar_socket_tcp(endereco, porta):
    try:
        servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor_socket.bind((endereco, porta))
        servidor_socket.listen(5)
        print(f"Socket TCP criado e escutando em {endereco}:{porta}")
        return servidor_socket
    except Exception as e:
        print(f"Erro ao criar o socket TCP: {e}")
        sys.exit(1)

if __name__ == "__main__":
    listar_peers("vizinhos.txt")