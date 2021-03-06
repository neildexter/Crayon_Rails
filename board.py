import operator as op, heapq
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
            return False
        if item[0] >= self.height or item[1] >= self.width:
            return False
        if self.terrain[item] == 'w' or self.terrain[item] == 'i':
            return False
        return True

    # Returns the cost of going from location tuple a to tuple b
    def calc_cost(self, a, b, player_num):
        cost = inf # cost is infinite unless otherwise set
        a_terr = self.terrain[a]
        b_terr = self.terrain[b]
        if self.adj(a, b) == True and self.valid(b):   # This is necessary if a, b are not known to be adjacent
            # Determines if the track to the destination is occupied by another player
            occupied_by = self.tracks.get((a,b),0)
            rvr = rivers.get((a,b), False)

            if occupied_by == 0:
                if a_terr == 'f' and b_terr == 'f':
                    cost = 0
                else:
                    cost = terr_cost[b_terr]
                    if rvr:
                        cost += 2
            elif occupied_by == player_num:
                cost = 0 # "free" to rebuild over owned track
            else:
                cost = inf # can't build over other player's tracks
        # Overrides any other conditions (i.e., multiple players can share, no river cost, no need to build, etc.
        if a_terr == 'L' and b_terr == 'L':
            cost = 0
        return cost

     # Takes in tuples and returns True if adjacent (False if identity or not adjacent)

    # Returns "True" if the two input tuples are adjacent on the hex board
    def adj(self, a, b):
        if (a == (54, 28) and b == (54, 32)) or (a == (54, 32) and b ==(54, 28)):
            return True
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
        if self.terrain[b] == 'w' or self.terrain[b] == 'i':
            return False
        # If it gets through all of the requirements it is adjacent
        return True

    # Returns a list of all valid tuples adjacent to tuple a
    def find_adj(self, a):
        # Check for even or odd y value
        if a[0] % 2 == 0:
            all_adj = [tuple(map(op.add, a, b)) for b in even_list]
        else:
            all_adj = [tuple(map(op.add, a, b)) for b in odd_list]
        if a == (54, 28):
            all_adj.append((54, 32))
        elif a == (54, 32):
            all_adj.append((54, 28))
        valid_adj = [item for item in all_adj if self.valid(item)]
        return valid_adj

    def set_adj_list(self):
        for i in range(self.height):
            for j in range(self.width):
                # if (i,j) == (54, 28):
                #     possible_adj.append((54, 32))
                # elif (i,j) == (54, 32):
                #     possible_adj.append((54, 28))
                self.adj_list[(i,j)] = self.find_adj((i,j))

    def create_cost_dict(self):
        for i in range(self.height):
            for j in range(self.width):
                for hex in self.adj_list[(i,j)]:
                    self.cost_dict[((i,j),hex)] = self.calc_cost((i,j), hex, 1)

    def create_path(self, node_list, player_num):
        for i in range(1, len(node_list)):
            self.create_rail(node_list[i - 1], node_list[i], player_num)

    def create_rail(self, a, b, player_num):  # Creates a rail between the two nodes
        if not self.adj(a, b):
            print "Cannot create rail. Points %r and %r are not adjacent." % (a, b)
        elif not( self.terrain[b] == 'L' and self.terrain[a] == 'L'):
            self.tracks[(a,b)] = player_num
            self.tracks[(b,a)] = player_num
        self.cost_dict[(a,b)] = 0
        self.cost_dict[(b,a)] = 0

    def set_terrain(self,terr_matrix):
        self.height = len(terr_matrix)
        self.width = len(terr_matrix[0])
        for i in range(self.height):
            for j in range(self.width):
                self.terrain[(i,j)] = terr_matrix[i][j]

    def __init__(self, terrain = {}, tracks = {}, cost_dict = {}, adj_list = {}, terr_matrix = None):  # Initializes the game board from a file
        # Default values set to 0 if nothing provided
        self.terrain = terrain
        self.tracks = tracks
        self.cost_dict = cost_dict
        self.adj_list = adj_list

        if not terrain:
            self.height = 0 # "i"
            self.width = 0  # "j"
        else:
            self.height = max(i for (i,j) in self.terrain)
            self.width = max(j for (i,j) in self.terrain)


        if terr_matrix is not None:
            self.set_terrain(terr_matrix)

        if not adj_list:
            self.set_adj_list()

        if not cost_dict:
            self.create_cost_dict()

    def conv_to_cube(self,coord):
        col = coord[1]
        row = coord[0]
        x = col - (row - (row % 2)) / 2
        z = row
        y = -x-z
        return (x,y,z)

    def hex_distance(self,src,dest):
        # row1 = src[0]
        # col1 = src[1]
        # x1 = col1 - (row1 - row1 % 2)/2
        # row2 = dest[0]
        # col2 = dest[1]
        # x2 = col2 - (row2 - row2 % 2)/2
        # return (abs(x1-x2)+abs(x1+row1+x2+row2)+abs(row1-row2))/2

        src_cube = self.conv_to_cube(src)
        dest_cube = self.conv_to_cube(dest)
        return sum(map(abs,map(op.sub, src_cube, dest_cube)))/2

    def heuristic(self,goal,current,next,player_num):
        dist = self.hex_distance(next,goal)
        if self.cost_dict[(current,next)] == 0:
            heur_cost = dist*.2
        else:
            heur_cost = dist
        return heur_cost

    ### A star algorithm shamelessly ripped from http://www.redblobgames.com/pathfinding/a-star/implementation.html
    def a_star(self, start, goal, player_num):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        move_cost = {}
        came_from[start] = None
        cost_so_far[start] = 0
        move_cost[start] = 0
        get_cost = self.cost_dict.get

        while not frontier.empty():
            current = frontier.get()
            if current == goal:
                break

            for next in self.adj_list[current]:
                new_cost = cost_so_far[current] + get_cost((current, next),inf)
                if new_cost < cost_so_far.get(next, inf):
                    if self.terrain[current] != 'f':
                        move_cost[next] = move_cost[current] + 1
                    else:
                        move_cost[next] = move_cost[current] + 6
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal,current,next,player_num)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far, move_cost

    def ai_a_star(self,start,goal,player_num):
        came_from, cost_so_far, move_cost = self.a_star(start, goal, player_num)
        moves = move_cost[goal]
        build_cost = cost_so_far[goal]
        # Writes the path to the board
        path = self.reconstruct_path(came_from, start, goal)
        self.create_path(path, 1)
        return build_cost, moves

    def reconstruct_path(self, came_from, start, goal):
        current = goal
        path = [current]
        while current != start:
            current = came_from[current]
            path.append(current)
        return path[::-1]