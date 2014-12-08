import board, display, pygame as pg
from globals import *
pg.init()
f = open('india_rails_gameboard.txt', 'r')

terr_matrix = [line.replace('\n', '').split(' ') for line in f]

b1 = board.Board(terr_matrix,hex_names)

display.display(b1)
input("Press enter...")