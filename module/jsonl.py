import json

class JsonLoader:
    def __init__(self, file):
        self.file = file

        with open(file, 'r') as f:
            self.cont = json.load(f)
        f.close()
    def edit(self, file_cont):
        with open(self.file, 'w') as f:
            json.dump(file_cont, f, indent = 4)
        f.close()
