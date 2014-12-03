# CLASS GAME
# contains CLASS BOARD
#	VARIABLES
#	root cell (0,0)
# 	contains class CELLS
#		VARIABLES
#		enum terrain in {"(p)lain", "(d)esert", "(s)wamp", "(m)ountain", "(a)lpine", "city small (cs)", "city med (cm)", "city large (sl)"}
#		occupied_by 0 (unoccupied), 1, 2, 3, 4, etc.
#		x, y
#		string city_name
#		contains PATH ne, e, se, sw, w, nw
#		FUNCTIONS
#		ne(), e(), se(), sw(), w(), nw() returns the cells in the given direction
#		contains class PATH
#			cost (int)
#			built_by 0 (unbuilt), 1, 2, 3, 4, etc.
#			adjacent_path (pointer to path in another cell)
#	FUNCTIONS
#	create_board(height, width): creates a board with null cells of specified height and width
#	cell_coord: returns cell at given coordinate
#	display_board: displays the board

import pygame as pg, operator as op
import math, time, random

#adds pathfinding information
#import dijkstra


hex_size = 60
h = hex_size
hex_gap = hex_size*(2-math.sqrt(3))/4
hex_width = hex_size - 2*hex_gap
hex_line_width = 1
rail_width = 3

left_pad = h/3
top_pad = h/3
right_pad = h/3
bot_pad = h/3

white = (255,255,255)
color_key = (254, 254, 254) # used as color key for blitting
black = (0,0,0)
red = (255,30,30)
brown = (188, 150, 50)
green = (0,255,0)
blue = (0,0,255)
yellow = (255, 255, 0)
gray = (200,200,200)

# 'even' means rows 0, 2, 4, etc. (start with 0)
even_tracks = { (-1,-1): 'nw',
				(0, -1): 'w',
				(1, -1): 'sw',
				(-1, 0): 'ne',
				#(0, 0): self
				(1,  0): 'se',
				#(-1,1): NOT ADJACENT
				(0,  1): 'e'
				#(1,1): NOT ADJACENT
					}
# List of tuples adjacent to an even node
even_list = list(even_tracks.keys())

# odd means rows 1, 3, 5, etc. (start with 0)
odd_tracks = { #(-1,-1) NOT ADJACENT
				(0, -1): 'w',
				#(-1,1) NOT ADJACENT
				(-1, 0): 'nw',
				#(0, 0) self
				(1,  0): 'sw',
				(-1, 1): 'ne',
				(0,  1): 'e',
				(1,  1): 'se'
					}
# List of tuples adjacent to an odd node
odd_list = list(odd_tracks.keys())

player_color = { #0: no player
				 1: red,
				 2: blue,
				 3: green,
				 4: brown,
				 5: yellow }

track_endpts = { "ne": (h/2 + h/(2*math.sqrt(3)),	0),
				 "e" : (h-hex_gap,					h/2),
				 "se": (h/2 + h/(2*math.sqrt(3)),	h),
				 "sw": (h/2 - h/(2*math.sqrt(3)),	h),
				 "w" : (hex_gap,					h/2),
				 "nw": (h/2 - h/(2*math.sqrt(3)),	0) }

inf = float('inf')
# Cost to move to terrain depending on type
terr_cost = { 	"p": 1,
				"m": 2,
				"a": 5,
				"d": 1,
				"s": 2,
				"cs": 3,
				"cm": 3,
				"cl": 5,
				"w": inf }



class Cell(object):	
	def plain(self):
		pg.draw.circle(self.hex_image, black, (h/2,h/2), h/20,0)	
	def mount(self):
		pg.draw.polygon(self.hex_image, black,
			[(h/2.-h/(10),h/2.+h/10.), \
			(h/2.,h/2.-h/10.), \
			(h/2.+h/(10),h/2.+h/10.), \
			(h/2.-h/(10),h/2.+h/10.)], 0)	
	def desert(self):
		# Fill with yellow
		pg.draw.circle(self.hex_image, yellow, (h/2,h/2), h/10,0)
		# Black border
		pg.draw.circle(self.hex_image, black, (h/2,h/2), h/10,1)		
	def alp(self):
		# Draw polygon with white
		pg.draw.polygon(self.hex_image, white,
			[(h/2.-h/(10),h/2.+h/10.), \
			(h/2.,h/2.-h/10.), \
			(h/2.+h/(10),h/2.+h/10.), \
			(h/2.-h/(10),h/2.+h/10.)], 0)
		# Draw border in black
		pg.draw.polygon(self.hex_image, black,
			[(h/2.-h/(10),h/2.+h/10.), \
			(h/2.,h/2.-h/10.), \
			(h/2.+h/(10),h/2.+h/10.), \
			(h/2.-h/(10),h/2.+h/10.)], 1)
	def swamp(self):
		size = h/3
		# Define letter as a font object
		letter = pg.font.Font(None,size)
		# Render the letter S with anti-aliasing
		pic = letter.render("S", 1, blue, color_key)
		# letter.metrics("S") # gives the drawn characteristics of text entered
		# 	minx, 	maxx,	miny, 	maxy, 	advance
		pic.set_colorkey(color_key)
		self.hex_image.blit(pic, (h/2 - .45*size/2.,h/2 - .80*size/2.))	
	def city_s(self):
		# Large circle (2x radius), filled with red
		pg.draw.circle(self.hex_image, red, (h/2,h/2), h/5,0)
		# Small circle (normal radius) filled with black
		pg.draw.circle(self.hex_image, black, (h/2,h/2), h/20,0)
	def city_m(self):
		width = int(2.*h/5.)
		height = width # since square
		left = (h - width)/2
		top = left # same coordinate for both since square
		pg.draw.rect(self.hex_image, red, pg.Rect((left, top), (width, height)),0)
		pg.draw.circle(self.hex_image, black, (h/2,h/2), h/20,0)
	def city_l(self): #STILL NOT DEFINED
		#placeholder
		1+1	
	def water(self):
		1+1
	def print_name(self):
		size = h/3
		# Define letter as a font object
		letter = pg.font.Font(None,size)
		# Render the letter S with anti-aliasing
		pic = letter.render(self.name, 1, black, color_key)
		#print letter.metrics("X")
		#[(	2, 		43, 	-2, 	49, 	45)]
		# 	minx, 	maxx,	miny, 	maxy, 	advance
		pic.set_colorkey(color_key)
		self.hex_image.blit(pic, (0,0))
	def draw_rails(self):
		for direction in self.tracks:
			num = self.tracks[direction]
			if num != 0:
				pg.draw.line(self.hex_image, player_color[num], (h/2,h/2), track_endpts[direction],rail_width)
		
	def create_display(self):
		# Creates a separate surface for each cell
		self.hex_image.fill(color_key)
		self.hex_image.set_colorkey(color_key)
		if self.terrain == 'w':
			color = blue
			line_width = 0
		else:
			color = gray
			line_width = hex_line_width
		# Draws hexagonal border around each item
		# Could reuse for drawing rivers?
		"""
		pg.draw.polygon(self.hex_image, color, \
			[(h/2,0), (h-hex_gap, h/4), \
			(h-hex_gap, 3*h/4), (h/2,h), \
			(hex_gap, 3*h/4), (hex_gap, h/4), \
			(h/2,0)], line_width)
		"""
		self.draw_rails()
		self.terrain_graphic[self.terrain]()
		if self.name != None:
			self.print_name()
		
	def __init__(self,terrain,name):	
		self.terrain = terrain
		
		#if self.terrain in ['cs', 'cm', 'cl']:
		self.name = name
		
		self.hex_image = pg.Surface((hex_size,hex_size+2))
		self.terrain_graphic = { "p": self.plain,
								 "m": self.mount,
								 "a": self.alp,
								 "d": self.desert,
								 "s": self.swamp,
								 "cs": self.city_s,
								 "cm": self.city_m,
								 "cl": self.city_l,
								 "w": self.water
								 }
		
		# if 0, no track; if a number, track belongs to player #
		self.tracks= { "ne": 0,
						"e": 0,
						"se": 0,
						"sw": 0,
						"w": 0,
						"nw": 0 }
		#starts from ne and goes clockwise to nw
		self.rivers = { "ne": 0,
						"e": 0,
						"se": 0,
						"sw": 0,
						"w": 0,
						"nw": 0 }
		self.create_display()

class Game(object):	

	def corner(self,i,j): # Returns the coordinate for the upper left hand corner of a hex image
		if i % 2 == 0: # if row number is even
			x = left_pad - hex_gap + (hex_width)*j
		else:
			x = left_pad - hex_gap + (hex_width)*(j+0.5)
			
		y = top_pad + (hex_size/2.0 + (hex_width)/(2.0*math.sqrt(3.0)))*i
		
		return (x,y)
		
	def valid(self, item):
		item_valid = True
		if min(item) < 0:
			item_valid = False
		if item[0] >= self.height or item[1] >= self.width:
			item_valid = False
		return item_valid
	
	def cost(self, a, b): # Returns the cost of going from location tuple a to tuple b
		if self.adj(a, b) == False or not self.valid(b):
			return inf # "infinite" cost
		else:
			return terr_cost[self.board[b[0]][b[1]].terrain]
	
	def adj(self, a, b): # Takes in tuples and returns True if adjacent (False if identity or not adjacent)
		if a == b: # a point is not considered adjacent to itself
			return False
		else:
			dist = tuple(map(op.sub, b, a))
			abs_dist = max(map(lambda coord: abs(coord), dist)) # find largest coordinate distance
		if abs_dist > 1:
			return False
		if a[0] % 2 == 0: #check if the y coordinate is even or odd
			if dist == (1, 1) or dist == (-1, 1):
				return False
		else:
			if dist == (-1, -1) or dist == (1, -1):
				return False
		
		# If it gets through all of the requirements it is adjacent
		return True
	
	def adj_list(self, a): # Returns a list of all items adjacent to tuple a
		# Check for even or odd y value
		if a[1] % 2 == 0:
			all_adj = [tuple(map(op.add, a, b)) for b in even_list]
		else:
			all_adj = [tuple(map(op.add, a, b)) for b in odd_list]
			
		valid_adj = [item for item in all_adj if self.valid(item)]
		return valid_adj
	
	# Displays the cost for the hexes surrounding a given location
	def test_cost(self):
		test_path = [(5, 28), (6, 28), (6, 27), (6, 26), (6, 25), (6, 24), (6, 23), (6, 22), (5, 21), (4, 21), (4, 20), (3, 19), (3, 18), (3, 17), (4, 17), (4, 16)]
		for node in test_path:
			for i in range(self.width):
				for j in range(self.height):
					size = h/3
					if self.cost(node,(i,j)) < 100:
						cost_str = str(self.cost(node,(i,j)))
						letter = pg.font.Font(None,size)
						pic = letter.render(cost_str, 1, green, color_key)
						pic.set_colorkey(color_key)
						self.board[i][j].hex_image.blit(pic, (h/2,h/2))

	
	def refresh_display(self): # Redraws the entire display
		self.screen.fill(white)
		self.test_cost()
		for i in range(self.height):
			for j in range(self.width):
				self.screen.blit(self.board[i][j].hex_image,self.corner(i,j))
		pg.display.flip()
		
	def create_display(self): # Initializes and displays the board
		
		# Uses first (index [0]) of corner function to get x value (width)
		self.screen_width = int(math.floor(self.corner(0,self.width)[0] + hex_width/2 + left_pad + right_pad))
		# Uses second (index [1]) of corner function to get y value (width)
		self.screen_height = int(math.floor(self.corner(self.height,0)[1] + top_pad + bot_pad))
				
		self.screen = pg.display.set_mode([self.screen_width, self.screen_height])
		self.refresh_display()

	def create_path(self,node_list):
		for i in range(1,len(node_list)):
			self.create_rail(node_list[i-1],node_list[i],1)
		
	def create_rail(self, a, b, player_num): # Creates a rail between the two nodes
		if not self.adj(a,b):
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
		
	def __init__(self): # Initializes the game board from a file
		
		#creates board with the height (# of rows) and width (# of cols)
		#refer to board as self.board[height][width]
		pg.init()
		
		f = open('game_board.txt', 'r')
		self.terr_matrix = [ line.replace('\n','').split(' ') for line in f]
		
		#f = open('hex_names.txt', 'r')
		
		# Creates names for all cities/important hexes
		self.hex_names = { (3,2): "Abbot", # City
							(9,6): "Baker", # City
							(5,28): "Camino", # City
							(1,8): "Dawson", # City
							(4,16): "Emmen" } # City
		# Makes inverse dictionary for finding coordinates by name
		self.inv_names = {name: coord for coord, name in self.hex_names.items()}
		
		self.height = len(self.terr_matrix)
		self.width = len(self.terr_matrix[0])
		
		# Creates an array of cells with (terrain, name). hex_names.get() returns None if empty
		self.board = [[Cell( self.terr_matrix[i][j], self.hex_names.get((i,j))) \
						for j in range(self.width)] for i in range(self.height)]
		print self.height
		print self.width
		self.create_display()
		
	##### Dijkstra search code shamelessly ripped from http://geekly-yours.blogspot.com/
	
	def dijkstra(self,src,dest,visited=[],distances={},predecessors={}):
		if src == dest:
			# We build the shortest path and display it
			path=[]
			pred=dest
			while pred != None:
				path.append(pred)
				pred=predecessors.get(pred)
			print('shortest path: '+str(path)+" cost="+str(distances[dest]))
		else:
			# if it is the initial  run, initializes the cost
			if not visited: 
				distances[src]=0
			# visit the neighbors
			for neighbor in self.adj_list(src): ######
				if neighbor not in visited:
					new_distance = distances[src] + self.cost(src,neighbor)
					if new_distance < distances.get(neighbor,float('inf')):
						distances[neighbor] = new_distance
						predecessors[neighbor] = src
			# mark as visited
			visited.append(src)
			# now that all neighbors have been visited: recurse
			# select the non visited node with lowest distance 'x'
			# run Dijskstra with src='x'
			unvisited={}
			for k in [(i,j) for i in range(self.height) for j in range(self.width)]:
				if k not in visited:
					unvisited[k] = distances.get(k,float('inf'))
			x=min(unvisited, key=unvisited.get)  
			self.dijkstra(x,dest,visited,distances,predecessors)
	
g = Game()
pathtest = g.dijkstra(g.inv_names["Emmen"],g.inv_names["Camino"],[],{},{})

print pathtest
g.create_path([(5, 28), (6, 28), (6, 27), (6, 26), (6, 25), (6, 24), (6, 23), (6, 22), (5, 21), (4, 21), (4, 20), (3, 19), (3, 18), (3, 17), (4, 17), (4, 16)])
#g.refresh_display()
input("Press Enter to continue...")
