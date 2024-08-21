from YDKReader import Reader
import os
folder = input("Enter folder path contains YDK Files")
ydkFiles = os.listdir(folder)

with open(folder + '/' + 'All.ydk', 'w') as file:
    for d in ydkFiles:
        if d.split('.')[-1] == 'ydk':
            deck = Reader(folder + '/' + d)
            for c, n in deck.get_result().items():
                id = str(c) + '\n'
                file.write(id * n)