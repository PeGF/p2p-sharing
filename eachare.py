import sys
import os

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

def menu(diretorio_compartilhado):
    while True:
        print("Escolha um comando:")
        print("[1] Listar peers")
        print("[2] Obter peers")
        print("[3] Listar arquivos locais")
        print("[4] Buscar arquivos")
        print("[5] Exibir estatisticas")
        print("[8] Alterar tamanho de chunk")
        print("[9] Sair")
        
        comando_escolhido = input("> ").strip()

        if comando_escolhido == "1":
            print("1")
        elif comando_escolhido == "2":
            print("2")
        elif comando_escolhido == "3":
            listar_arquivos(diretorio_compartilhado)
        elif comando_escolhido == "4":
            print("3")
        elif comando_escolhido == "5":
            print("3")
        elif comando_escolhido == "6":
            print("3")
        elif comando_escolhido == "7":
            print("3")
        elif comando_escolhido == "8":
            print("3")
        elif comando_escolhido == "9":
            print("3")


if __name__ == "__main__":
    validar_entrada()