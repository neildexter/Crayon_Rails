import math as m

h = 30 # size (height) of the square bounding box for each hex image
hex_gap = h*(2-m.sqrt(3))/4
hex_width = h - 2*hex_gap
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

track_endpts = { "ne": (h/2 + h/(2*m.sqrt(3)),	0),
				 "e" : (h-hex_gap,					h/2),
				 "se": (h/2 + h/(2*m.sqrt(3)),	h),
				 "sw": (h/2 - h/(2*m.sqrt(3)),	h),
				 "w" : (hex_gap,					h/2),
				 "nw": (h/2 - h/(2*m.sqrt(3)),	0) }

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