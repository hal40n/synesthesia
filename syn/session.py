class Session:
    def __init__(self, mode: str):
        self.mode = mode

    def start(self):
        print(f"syn session started in {self.mode} mode")