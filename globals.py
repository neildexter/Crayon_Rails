import pygame as pg, operator as op
import math, time, random

def init():
global hex_size
hex_size = 60
global h
h = hex_size
global hex_gap
hex_gap = hex_size*(2-math.sqrt(3))/4
global hex_width
hex_width = hex_size - 2*hex_gap
global hex_line_width
hex_line_width = 1
global rail_width
rail_width = 3

global left_pad
left_pad = h/3
global top_pad
top_pad = h/3
global right_pad
right_pad = h/3
global bot_pad
bot_pad = h/3

global white
white = (255,255,255)
global color_key
color_key = (254, 254, 254) # used as color key for blitting
global black
black = (0,0,0)
global red
red = (255,30,30)
global brown
brown = (188, 150, 50)
global green
green = (0,255,0)
global blue
blue = (0,0,255)
global yellow
yellow = (255, 255, 0)
global gray
gray = (200,200,200)

# 'even' means rows 0, 2, 4, etc. (start with 0)
global even_tracks
even_tracks = { (-1,-1): 'nw',
				(-1, 0): 'w',
				(-1, 1): 'sw',
				(0, -1): 'ne',
				#(0, 0): self
				(0,  1): 'se',
				#(1,-1): NOT ADJACENT
				(1,  0): 'e'
				#(1,1): NOT ADJACENT
					}
# List of tuples adjacent to an even node
global even_list
even_list = [(-1,-1), (-1, 0), (-1, 1),	(0, -1), (0,  1), (1,  0)]

# odd means rows 1, 3, 5, etc. (start with 0)
global odd_tracks
odd_tracks = { #(-1,-1) NOT ADJACENT
				(-1, 0): 'w',
				#(-1,1) NOT ADJACENT
				(0, -1): 'nw',
				#(0, 0) self
				(0,  1): 'sw',
				(1, -1): 'ne',
				(1,  0): 'e',
				(1,  1): 'se'
					}
# List of tuples adjacent to an odd node
global odd_list
odd_list = [(1, 1), (-1, 0), (1, -1), (0, -1), (0,  1), (1,  0)]

global player_color
player_color = { #0: no player
				 1: red,
				 2: blue,
				 3: green,
				 4: brown,
				 5: yellow }

global track_endpts
track_endpts = { "ne": (h/2 + h/(2*math.sqrt(3)),	0),
				 "e" : (h-hex_gap,					h/2),
				 "se": (h/2 + h/(2*math.sqrt(3)),	h),
				 "sw": (h/2 - h/(2*math.sqrt(3)),	h),
				 "w" : (hex_gap,					h/2),
				 "nw": (h/2 - h/(2*math.sqrt(3)),	0) }


global infty
infty = 10000000
# Cost to move to terrain depending on type
global terr_cost
terr_cost = { 	"p": 1,
				"m": 2,
				"a": 5,
				"d": 1,
				"s": 2,
				"cs": 3,
				"cm": 3,
				"cl": 5,
				"w": infty }
