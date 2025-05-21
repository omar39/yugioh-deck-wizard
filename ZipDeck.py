import zipfile
import os
class ZipDeck:
    deck = list()
    def __init__(self, file_name:str, working_dir:str):
        # unzip file
        self.deck = list()
        with zipfile.ZipFile(file_name, 'r') as zip_ref:
            zip_ref.extractall(working_dir)
            # get list of files
            for file in zip_ref.infolist():
                if file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.jfif')):
                    self.deck.append(file.filename)
    def get_deck(self):
        return self.deck
    def clear_deck(self):
        self.deck = list()
