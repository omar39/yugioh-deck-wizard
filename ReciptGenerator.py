from YDKReader import Reader
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import *
import pandas as pd
import os

class YugiohRecipt():

    def import_database(self):
        '''
        Import database. A dataframe object is then returned
        '''
        database_filename = os.getcwd() +  '/database.csv'
        database = pd.read_csv(database_filename, index_col="id")
        database.index = database.index.astype(str)
        #database.head()
        return database
    
    def gui_fname(self, dir=None):
        '''
        Select a file via a dialog and return the file name.
        '''
        if dir is None: dir ='./'
        fname = QFileDialog.getOpenFileName(None, "Select data file...", 
                    dir, filter="All files (*);; SM Files (*.sm)")
        return fname[0]
    

    def generate_recipt(self):
        database = self.import_database()
        cards = dict()
        while input("Choose another file to add? (y/n)") == 'y':
            print('adding your file....')
            fname = input("write the full path of the file ")
            # fname = self.gui_fname()
            deck = Reader(fname.split('\'')[1])
            for id, count in deck.get_result().items():
                card_name = database.at[id, 'name']
                if cards.get(card_name) == None:
                    cards[card_name] = 0
                cards[card_name] += count
            print('Done.')
        return cards

recipt = YugiohRecipt()
records = recipt.generate_recipt()
for i, j in records.items():
    print (i + '\t' + j)
