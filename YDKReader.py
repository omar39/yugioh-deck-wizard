import re

class Reader:
    deck = dict()
    def __init__(self, file_name: str):
                
        ydk_deck = open(file_name, "r")
        ydk_deck = re.findall('\d+', str(ydk_deck.readlines()))

        deck = dict()

        for card in ydk_deck:
            if deck.get(card) == None:
                deck[card] = 0
            deck[card] += 1

        self.deck = deck

    def get_result(self):
        return self.deck