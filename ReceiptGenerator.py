from YDKReader import Reader
from ZipDeck import ZipDeck
import pandas as pd
import os

class YugiohReceipt():
    def __init__(self, deck: Reader, extra_cards_filename: str, price_per_card: float, price_per_extra_card: float, output_path:str):
        self.database = self.import_database()
        self.deck = Reader(deck) if deck != None else None
        self.extra_cards = ZipDeck(extra_cards_filename, output_path) if extra_cards_filename != None else None
        self.price_per_card = price_per_card
        self.price_per_extra_card = price_per_extra_card
        self.output_path = output_path

        self.RECEIPT_FILE = 'receipt.txt'
    def import_database(self):
        '''
        Import database. A dataframe object is then returned
        '''
        database_filename = os.getcwd() + '/database.csv'
        database = pd.read_csv(database_filename, index_col="id")
        database.index = database.index.astype(str)
        return database

    def generate_receipt(self):
        cards = dict()
        extra_cards_number = len(self.extra_cards.get_deck()) if self.extra_cards != None else 0
        normal_cards_number = sum(self.deck.get_result().values()) if self.deck != None else 0
        total_cards = normal_cards_number + extra_cards_number
        
        print('Making the receipt....')
        if self.deck is not None:
            for id, count in self.deck.get_result().items():
                card_name = self.database.at[id, 'name'] if id in self.database.index else 'Unknown Card'
                if card_name not in cards:
                    cards[card_name] = 0
                cards[card_name] += count
            cards = dict(sorted(cards.items(), key=lambda x: x[1], reverse=True))
        # create text file to populate the receipt data in
        with open(self.output_path + '/' + self.RECEIPT_FILE, 'w') as f:
            f.write('=== \t\t========= \n')
            f.write("Qty \t\tCard Name \n")
            f.write('=== \t\t========= \n')
            for name, qty in cards.items():
                f.write('{} x \t\t{} \n'.format(str(qty), name))
            f.write('\n\nCustom cards: \t{}'.format(extra_cards_number))
            f.write('\n\nTotal number of cards: \t{}\nCheck : \t\t {} LE'.format(total_cards, (extra_cards_number * self.price_per_extra_card) + (normal_cards_number * self.price_per_card) ))
        print("Receipt created!")
        return self.output_path + '/' + self.RECEIPT_FILE
