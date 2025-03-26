class Clock:
    def __init__(self):
        self.clock = 0

    def incrementClock(self):
        self.clock += 1
        print(f"=> Atualizando relogio para {self.clock}")

def sendMessage(message, clock):
    clock.incrementClock()

    # envia a mensagem
    print(f"Encaminhando mensagem {message} para <endereço:porta destino>")

def receiveMessage(clock):
    # recebe a mensagem
    print("recebendo a mensagem")
    
    clock.incrementClock()
