import pygame as pg, operator as op, numpy as np, cell as c, math as m, time, random, heapq
from globals import *

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

class Board(object):
    # Returns "True" if the coordinate tuple fed to it is a valid board location
    def valid(self, item):
        item_valid = True
        if min(item) < 0:
            item_valid = False
        if item[0] >= self.height or item[1] >= self.width:
            item_valid = False
        return item_valid

    # Returns the cost of going from location tuple a to tuple b
    def cost(self, a, b, player_num):
        cost = inf # cost is infinite unless otherwise set
        #if self.adj(a, b) == True and self.valid(b):   THIS IS NECESSARY IF NOT RUNNING A STAR!!!!!
        a_dist = tuple(map(op.sub, b, a))
        # Determines if the track to the destination is occupied by another player
        if a[0] % 2 == 0:
            occupied_by = self.board[a[0],a[1]].tracks[even_tracks[a_dist]]
        else:
            occupied_by = self.board[a[0],a[1]].tracks[odd_tracks[a_dist]]

        if occupied_by == 0:
            a_terr = self.board[b[0],b[1]].terrain
            b_terr = self.board[a[0],a[1]].terrain
            if a_terr == 'L' and b_terr == 'L':
                cost = 0
            else:
                cost = terr_cost[b_terr]
        elif occupied_by == player_num:
            # Could set cost to small number to reduce unnecessary travel when building paths
            # (or larger for saving turns (.6?))
            cost = 0 # "free" to rebuild over owned track
        else:
            cost = inf # can't build over other player's tracks
        return cost

     # Takes in tuples and returns True if adjacent (False if identity or not adjacent)

    # Returns "True" if the two input tuples are adjacent on the hex board
    def adj(self, a, b):
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

    # Returns a list of all valid tuples adjacent to tuple a
    def adj_list(self, a):
        # Check for even or odd y value
        if a[0] % 2 == 0:
            all_adj = [tuple(map(op.add, a, b)) for b in even_list]
        else:
            all_adj = [tuple(map(op.add, a, b)) for b in odd_list]

        valid_adj = [item for item in all_adj if self.valid(item)]
        return valid_adj

    def create_path(self, node_list, player_num):
        for i in range(1, len(node_list)):
            self.create_rail(node_list[i - 1], node_list[i], player_num)

    def tracks_at(self,loc):
        if loc[0] % 2 == 0:
            print self.board[loc[0],loc[1]].tracks[even_tracks]
        else:
            print self.board[loc[0],loc[1]].tracks[odd_tracks]

    def create_rail(self, a, b, player_num):  # Creates a rail between the two nodes
        if not self.adj(a, b):
            print "Cannot create rail. Points %r and %r are not adjacent." % (a, b)
        else:
            a_dist = tuple(map(op.sub, b, a))
            b_dist = tuple(map(op.sub, a, b))

            if a[0] % 2 == 0:
                self.board[a[0],a[1]].tracks[even_tracks[a_dist]] = player_num
            else:
                self.board[a[0],a[1]].tracks[odd_tracks[a_dist]] = player_num

            # If b is in an odd row, interpret the distance accordingly
            if b[0] % 2 == 0:
                self.board[b[0],b[1]].tracks[even_tracks[b_dist]] = player_num
            else:
                self.board[b[0],b[1]].tracks[odd_tracks[b_dist]] = player_num
    def get(self, i, j):
        return self.board[i,j]

    def __init__(self, terr_matrix, hex_names):  # Initializes the game board from a file

        #creates board with the height (# of rows) and width (# of cols)
        #refer to board as self.board[height][width]

        # Creates names for all cities/important hexes
        self.hex_names = hex_names
        # Makes inverse dictionary for finding coordinates by name
        self.inv_names = {name: coord for coord, name in self.hex_names.items()}
        self.terr_matrix = terr_matrix
        self.height = len(self.terr_matrix)
        self.width = len(self.terr_matrix[0])

        self.board = np.empty((self.height, self.width),dtype=object)

        # Creates an array of cells with (terrain, name). hex_names.get() returns None if empty
        for i in range(self.height):
            for j in range(self.width):
                self.board[i,j] = c.Cell(terr_matrix[i][j], self.hex_names.get((i, j)))

        #self.create_display()

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

    def heuristic(self,goal,current,next,player_num):
        if self.cost(current,next,player_num) == 0:
            heur_cost = 0
        else:
            heur_cost = self.hex_distance(next,goal)
        return heur_cost

    ### A star algorithm shamelessly ripped from http://www.redblobgames.com/pathfinding/a-star/implementation.html
    def a_star(self, start, goal, player_num):
        frontier = PriorityQueue()
        frontier.put(start,0)
        came_from = {}
        cost_so_far = {}
        move_cost = {}
        came_from[start] = None
        cost_so_far[start] = 0
        move_cost[start] = 0

        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break

            for next in self.adj_list(current):
                new_cost = cost_so_far[current] + self.cost(current, next, player_num)
                if new_cost < cost_so_far.get(next, inf):
                    move_cost[next] = move_cost[current]+1
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal,current,next,player_num)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far, move_cost

    def ai_a_star(self,start,goal,player_num):
        came_from, cost_so_far, move_cost = self.a_star(start,goal,1)
        moves = move_cost[goal]
        build_cost = cost_so_far[goal]

        # Writes the path to the board
        pathtest = self.reconstruct_path(came_from, start, goal)
        self.create_path(pathtest,1)
        return build_cost, moves

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        return path