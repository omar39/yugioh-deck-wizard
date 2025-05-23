import re

class Reader:
    def __init__(self, file_name: str):
        self.deck = self._process_file(file_name)

    def get_result(self):
        return self.deck if self.deck != None else dict()
    def remove_card(self, card_id: str):
        self.deck.pop(card_id)

    def _process_file(self, file_name: str):
        try:
            with open(file_name, "r") as f:
                ydk_deck = re.findall('\\d+', ''.join(f.readlines()))
        except FileNotFoundError:
            print(f"File {file_name} not found.")
            return None

        deck = dict()

        for card in ydk_deck:
            if deck.get(card) == None:
                deck[card] = 0
            deck[card] += 1

        return deck
