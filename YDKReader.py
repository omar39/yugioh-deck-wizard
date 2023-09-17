import os
import re

class Reader:
    deck = dict()
    def __init__(self, file_name: str):    
        ##file_name = "Orcust PangChy.ydk"
        folder_name = file_name.split('.ydk')[0] 
        path = os.path.normpath(os.getcwd() + '/' + folder_name)
        print(path)
        exists = (os.path.exists(path))
        if not exists:
            try:
                os.mkdir(folder_name)
                print("New Directory Created '{}' ".format(folder_name) )
            except FileExistsError:
                print('Directory already exists!')
                
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

#Reader('./YDK Files/FLOOWANDEREEZE META.ydk')