import random
from random import choice

class Square:
    def draw(self):
        print(f'Inside Square::draw()')

s = Square()
print(s.draw().__repr__())
