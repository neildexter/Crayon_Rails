import board, display, pygame as pg, pickle, time
from globals import *
pg.init()
f = open('india_rails_gameboard.txt', 'r')

terr_matrix = [line.replace('\n', '').split(' ') for line in f]

b1 = board.Board({},{},{},terr_matrix)

print b1.height, b1.width

cost_dict = {}

start_time = time.time()

for i in range(b1.height):
    for j in range(b1.width):
        a = (i,j)
        for b in b1.adj_list(a):
            cost_dict[(a,b)] = b1.calc_cost(a,b,1)
            print a, b
print cost_dict[((26,45),(26,46))]

output = open('cost_dict.pk1', 'wb')

pickle.dump(cost_dict, output)

output.close()

#display.display(b1)
input("Press enter...")