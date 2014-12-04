import pygame as pg, operator as op, cell as c, math, time, random
import cProfile
from globals import *

class Game(object):
    def corner(self, i, j):  # Returns the coordinate for the upper left hand corner of a hex image
        if i % 2 == 0:  # if row number is even
            x = left_pad - hex_gap + (hex_width) * j
        else:
            x = left_pad - hex_gap + (hex_width) * (j + 0.5)

        y = top_pad + (h/ 2.0 + (hex_width) / (2.0 * math.sqrt(3.0))) * i

        return (x, y)

    def valid(self, item):
        item_valid = True
        if min(item) < 0:
            item_valid = False
        if item[0] >= self.height or item[1] >= self.width:
            item_valid = False
        return item_valid

    def cost(self, a, b, player_num):  # Returns the cost of going from location tuple a to tuple b
        cost = inf # cost is infinite unless otherwise set
        if self.adj(a, b) == True or self.valid(b):
            a_dist = tuple(map(op.sub, b, a))
            # Determines if the track to the destination is occupied by another player
            if a[0] % 2 == 0:
                occupied_by = self.board[a[0]][a[1]].tracks[even_tracks[a_dist]]
            else:
                occupied_by = self.board[a[0]][a[1]].tracks[odd_tracks[a_dist]]

            if occupied_by == 0:
                cost = terr_cost[self.board[b[0]][b[1]].terrain]
            elif occupied_by == player_num:
                # Could set cost to small number to reduce unnecessary travel when building paths
                # (or larger for saving turns (.6?))
                cost = 0 # "free" to rebuild over owned track
            else:
                cost = inf # can't build over other player's tracks
        return cost

    def adj(self, a, b):  # Takes in tuples and returns True if adjacent (False if identity or not adjacent)
        if a == b:  # a point is not considered adjacent to itself
            return False
        else:
            dist = tuple(map(op.sub, b, a))
            abs_dist = max(map(lambda coord: abs(coord), dist))  # find largest coordinate distance
        if abs_dist > 1:
            return False
        if a[0] % 2 == 0:  #check if the y coordinate is even or odd
            if dist == (1, 1) or dist == (-1, 1):
                return False
        else:
            if dist == (-1, -1) or dist == (1, -1):
                return False

        # If it gets through all of the requirements it is adjacent
        return True

    def adj_list(self, a):  # Returns a list of all items adjacent to tuple a
        # Check for even or odd y value
        if a[0] % 2 == 0:
            all_adj = [tuple(map(op.add, a, b)) for b in even_list]
        else:
            all_adj = [tuple(map(op.add, a, b)) for b in odd_list]

        valid_adj = [item for item in all_adj if self.valid(item)]
        return valid_adj

    def refresh_display(self):  # Redraws the entire display
        self.screen.fill(white)
        for i in range(self.height):
            for j in range(self.width):
                self.screen.blit(self.board[i][j].hex_image, self.corner(i, j))
        pg.display.flip()

    def create_display(self):  # Initializes and displays the board

        # Uses first (index [0]) of corner function to get x value (width)
        self.screen_width = int(math.floor(self.corner(0, self.width)[0] + hex_width / 2 + left_pad + right_pad))
        # Uses second (index [1]) of corner function to get y value (width)
        self.screen_height = int(math.floor(self.corner(self.height, 0)[1] + top_pad + bot_pad))

        self.screen = pg.display.set_mode([self.screen_width, self.screen_height])
        self.refresh_display()

    def create_path(self, node_list):
        for i in range(1, len(node_list)):
            self.create_rail(node_list[i - 1], node_list[i], 1)

    def tracks_at(self,loc):
        if loc[0] % 2 == 0:
            print self.board[loc[0]][loc[1]].tracks[even_tracks]
        else:
            print self.board[loc[0]][loc[1]].tracks[odd_tracks]

    def create_rail(self, a, b, player_num):  # Creates a rail between the two nodes
        if not self.adj(a, b):
            print "Cannot create rail. Points %r and %r are not adjacent." % (a, b)
        else:
            a_dist = tuple(map(op.sub, b, a))
            b_dist = tuple(map(op.sub, a, b))

            if a[0] % 2 == 0:
                self.board[a[0]][a[1]].tracks[even_tracks[a_dist]] = player_num
            else:
                self.board[a[0]][a[1]].tracks[odd_tracks[a_dist]] = player_num

            # If b is in an odd row, interpret the distance accordingly
            if b[0] % 2 == 0:
                self.board[b[0]][b[1]].tracks[even_tracks[b_dist]] = player_num
            else:
                self.board[b[0]][b[1]].tracks[odd_tracks[b_dist]] = player_num

            self.board[a[0]][a[1]].create_display()
            self.board[b[0]][b[1]].create_display()
        self.refresh_display()

    def __init__(self):  # Initializes the game board from a file

        #creates board with the height (# of rows) and width (# of cols)
        #refer to board as self.board[height][width]
        pg.init()

        f = open('game_board.txt', 'r')
        self.terr_matrix = [line.replace('\n', '').split(' ') for line in f]

        #f = open('hex_names.txt', 'r')

        # Creates names for all cities/important hexes
        self.hex_names = {(3, 2): "Abbot",  # City
                          (9, 6): "Baker",  # City
                          (5, 28): "Camino",  # City
                          (1, 8): "Dawson",  # City
                          (4, 16): "Emmen"}  # City
        # Makes inverse dictionary for finding coordinates by name
        self.inv_names = {name: coord for coord, name in self.hex_names.items()}

        self.height = len(self.terr_matrix)
        self.width = len(self.terr_matrix[0])

        # Creates an array of cells with (terrain, name). hex_names.get() returns None if empty
        self.board = [[c.Cell(self.terr_matrix[i][j], self.hex_names.get((i, j))) \
                       for j in range(self.width)] for i in range(self.height)]
        self.create_display()

    def conv_to_cube(self,coord):
        col = coord[1]
        row = coord[0]
        x = col - (row - (row % 2)) / 2
        z = row
        y = -x-z
        return (x,y,z)

    def hex_distance(self,src,dest):
        src_cube = self.conv_to_cube(src)
        dest_cube = self.conv_to_cube(dest)
        return sum(map(abs,map(op.sub, src_cube, dest_cube)))/2

    ##### Dijkstra search code shamelessly ripped from http://geekly-yours.blogspot.com/

    def dijkstra(self, src, dest, player_num, visited=[], distances={}, predecessors={}):
        if src == dest:
            # We build the shortest path and display it
            path = []
            pred = dest
            while pred is not None:
                path.append(pred)
                pred = predecessors.get(pred)
            return path, distances[dest]
        else:
            # if it is the initial  run, initializes the cost
            if not visited:
                distances[src] = 0
            # visit the neighbors
            for neighbor in self.adj_list(src):  ######
                if neighbor not in visited:
                    new_distance = distances[src] + self.cost(src, neighbor, player_num)+self.hex_distance(src,dest)
                    if new_distance < distances.get(neighbor, float('inf')):
                        distances[neighbor] = new_distance
                        predecessors[neighbor] = src
            # mark as visited
            visited.append(src)
            # now that all neighbors have been visited: recurse
            # select the non visited node with lowest distance 'x'
            # run Dijskstra with src='x'
            unvisited = {}
            for k in [(i, j) for i in range(self.height) for j in range(self.width)]:
                if k not in visited:
                    unvisited[k] = distances.get(k, float('inf'))
            x = min(unvisited, key=unvisited.get)
            return self.dijkstra(x, dest, player_num, visited, distances, predecessors)

g = Game()

cities = g.hex_names.keys()
random.shuffle(cities)

total_cost = 0
for i in range(len(cities)-1):
   pathtest, cost = g.dijkstra(cities[i], cities[i+1], 1, [], {}, {})
   g.create_path(pathtest)
   print g.hex_names[cities[i]], g.hex_names[cities[i+1]], cost
   total_cost += cost
print total_cost


# This chooses a slightly longer path...
# Emmen Camino 23
# Emmen Baker 15
# Emmen Dawson 7
# Emmen Abbot 9


input("Press Enter to continue...")
