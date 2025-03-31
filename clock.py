class Clock:
    def __init__(self):
        self.clock = 0

    def incrementClock(self):
        self.clock += 1
        print(f"=> Atualizando relogio para {self.clock}")
