from Class import Server

if __name__ == "__main__":
    server = Server()
    host = 'localhost'
    port = int(input())
    server.connect_to_peer(host, port)
    