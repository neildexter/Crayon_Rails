import math as m

h = 60 # size (height) of the square bounding box for each hex image
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

resources_by_name = {'Agra': ['Textiles'],
                     'Ahmadabad': ['Cotton'],
                     'Allahabad': ['Linseed Oil'],
                     'Anuradhapura': ['Rubber','Salt'],
                     'Asansol': ['Copper'],
                     'Bangalore': ['Steel'],
                     'Bareilly': ['Millet'],
                     'Bellary': ['Mica'],
                     'Bhopal': ['Machinery'],
                     'Bhubaneshwar': ['Bauxite'],
                     'Bombay': [],
                     'Calcutta': [],
                     'Chittagong': ['Jute', 'Rice'],
                     'Cochin': ['Coffee', 'Imports'],
                     'Colombo': ['Indigo', 'Tea'],
                     'Darjeeling': ['Tea'],
                     'Delhi': [],
                     'Dhaka': ['Rice'],
                     'Dibrugarh': ['Oil'],
                     'English Bazar': ['Textiles'],
                     'Gorakhpur': ['Millet'],
                     'Guwahati': ['Coal'],
                     'Hyderabad India': ['Textiles'],
                     'Hyderabad Pakistan': ['Rice', 'Sugar'],
                     'Jabalpur':[],
                     'Jaipur': [],
                     'Jamnagar': ['Salt'],
                     'Jamshedpur': ['Steel'],
                     'Jodhpur': ['Mica'],
                     'Kanpur': ['Corn'],
                     'Karachi': [],
                     'Kathmandu': ['Goats'],
                     'Khulna': ['Imports'],
                     'Lahore': ['Cotton','Goats'],
                     'Lucknow': ['Corn'],
                     'Madras': [],
                     'Mangalore': ['Fish'],
                     'Multan': ['Rugs'],
                     'Nagpur': ['Bauxite'],
                     'Patna': ['Machinery', 'Steel'],
                     'Pune': ['Peanuts'],
                     'Quetta': ['Dates', 'Gypsum'],
                     'Raipur': ['Coal'],
                     'Rawalpindi': ['Oil'],
                     'Solapur': ['Sugar'],
                     'Srinagar': ['Gypsum'],
                     'Tiruchchirappalli': ['Coal'],
                     'Trivandrum': ['Fish', 'Peanuts'],
                     'Varanasi': ['Millet'],
                     'Vijayawada': ['Coal'],
                     'Visakhapatnam': ['Wood']}

hex_names = { (16, 27): 'Agra',
              (25, 17): 'Ahmadabad',
              (20, 33): 'Allahabad',
              (56, 33): 'Anuradhapura',
              (23, 41): 'Asansol',
              (47, 25): 'Bangalore',
              (14, 30): 'Bareilly',
              (42, 24): 'Bellary',
              (25, 25): 'Bhopal',
              (16, 40): 'Bhubaneshwar',
              (33, 18): 'Bombay', #CENTER OF CITY
              (26, 45): 'Calcutta', #CENTER OF CITY
              (25, 52): 'Chittagong',
              (53, 24): 'Cochin',
              (60, 32): 'Colombo',
              (15, 45): 'Darjeeling',
              (13, 25): 'Delhi', #CENTER OF CITY
              (23, 49): 'Dhaka',
              (16, 58): 'Dibrugarh',
              (20, 45): 'English Bazar',
              (17, 36): 'Gorakhpur',
              (18, 52): 'Guwahati',
              (37, 27): 'Hyderabad India',
              (19, 10): 'Hyderabad Pakistan',
              (25, 30): 'Jabalpur',
              (17, 22): 'Jaipur',
              (27, 12): 'Jamnagar',
              (25, 40): 'Jamshedpur',
              (18, 18): 'Jodhpur',
              (18, 31): 'Kanpur',
              (20,  8): 'Karachi', #CENTER OF CITY
              (15, 40): 'Kathmandu',
              (25, 47): 'Khulna',
              ( 6, 20): 'Lahore',
              (17, 32): 'Lucknow',
              ( 8, 24): 'Ludhiana',
              (46, 30): 'Madras', #CENTER OF CITY
              (47, 21): 'Mangalore',
              ( 9, 15): 'Multan',
              (30, 28): 'Nagpur',
              (20, 40): 'Patna',
              (36, 20): 'Pune',
              ( 9,  7): 'Quetta',
              (29, 33): 'Raipur',
              ( 1, 17): 'Rawalpindi',
              (37, 23): 'Solapur',
              ( 0, 21): 'Srinagar',
              (52, 28): 'Tiruchchirappalli',
              (56, 25): 'Trivandrum',
              (20, 36): 'Varanasi',
              (39, 31): 'Vijayawada',
              (36, 36): 'Visakhapatnam'}