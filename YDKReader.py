import re

class Reader:
    def __init__(self, file_name: str):
        self.deck = self._process_file(file_name)

    def get_result(self):
        return self.deck if self.deck != None else dict()
    def remove_card(self, card_id: str):
        self.deck.pop(card_id)

    def _process_file(self, file_name: str):
        ydk_deck = []
        card_id_regex = re.compile(r"^\d+$")
        try:
            with open(file_name, "r") as f:
                for line in f:
                    # Remove leading/trailing whitespace, including newlines
                    stripped_line = line.strip()
                    # Check if the stripped line matches the card ID regex
                    if card_id_regex.match(stripped_line):
                        ydk_deck.append(stripped_line)
        except FileNotFoundError:
            print(f"File {file_name} not found.")
            return None

        deck = {}

        for card in ydk_deck:
            if deck.get(card) == None:
                deck[card] = 0
            deck[card] += 1

        return deck
