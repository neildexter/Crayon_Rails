import math as m
h_float = 58.6 # size (height) of the square bounding box for each hex image
h = int(h_float)
hex_gap_float = h_float*(2-m.sqrt(3))/4
hex_gap = int(hex_gap_float)
hex_width_float = h_float - 2*hex_gap_float
hex_width = int(hex_width_float)
hex_line_width = 1
river_width = 4
rail_width = 5
plain_size = h/12


left_pad = 125 #h/3
top_pad = 70 #h/3
#right_pad = h/3
#bot_pad = h/3

white = (255,255,255)
color_key = (254, 254, 254) # used as color key for blitting
black = (0,0,0)
red = (255,30,30)
brown = (188, 150, 50)
green = (0,255,0)
blue = (0,0,255)
blue_water = (46, 157, 255)
blue_salt = (88, 114, 128)
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
				(0,  1): 'e',
				#(1,1): NOT ADJACENT
                (0, 4): 'ferry',
                (0,-4): 'ferry'
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
				"s": 3,
				"S": 3,
				"M": 3,
				"L": 5,
                "f": 6,
				"w": inf,
                "i": inf}

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
              (55, 33): 'Anuradhapura',
              (23, 41): 'Asansol',
              (47, 25): 'Bangalore',
              (14, 30): 'Bareilly',
              (42, 24): 'Bellary',
              (25, 25): 'Bhopal',
              (31, 40): 'Bhubaneshwar',
              (33, 18): 'Bombay', #CENTER OF CITY
              (26, 45): 'Calcutta', #CENTER OF CITY
              (26, 53): 'Chittagong',
              (53, 24): 'Cochin',
              (59, 32): 'Colombo',
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

rivers = {( 0, 17,  'e') : 1, # START Indus
          ( 0, 17, 'se') : 1,
          ( 1, 16,  'e') : 1,
          ( 1, 16, 'se') : 1,
          ( 1, 16, 'sw') : 1,
          ( 1, 15, 'se') : 1,
          ( 2, 15,  'e') : 1,
          ( 2, 15, 'se') : 1,
          ( 3, 14,  'e') : 1,
          ( 4, 15, 'ne') : 1,
          ( 4, 15,  'e') : 1,
          ( 4, 15, 'se') : 1,
          ( 5, 14,  'e') : 1,
          ( 5, 14, 'se') : 1,
          ( 6, 14,  'e') : 1,
          ( 6, 14, 'se') : 1,
          ( 7, 13,  'e') : 1,
          ( 8, 14, 'ne') : 1,
          ( 8, 14,  'e') : 1,
          ( 8, 14, 'se') : 1,
          ( 9, 13,  'e') : 1,
          ( 9, 13, 'se') : 1,
          (10, 13,  'e') : 1,
          (11, 13, 'ne') : 1,
          (11, 13,  'e') : 1,
          (11, 13, 'se') : 1, # CONFLUENCE Indus + Sutlej
          (12, 13,  'e') : 1,
          (12, 13, 'se') : 1,
          (13, 12,  'e') : 1,
          (13, 12, 'se') : 1,
          (13, 12, 'sw') : 1,
          (13, 11, 'se') : 1,
          (14, 11,  'e') : 1,
          (14, 11, 'se') : 1,
          (14, 11, 'sw') : 1,
          (14, 10, 'se') : 1,
          (15,  9,  'e') : 1,
          (15,  9, 'se') : 1,
          (16,  9,  'e') : 1,
          (16,  9, 'se') : 1,
          (17,  8,  'e') : 1,
          (17,  8, 'se') : 1,
          (18,  8,  'e') : 1,
          (19,  8, 'ne') : 1,
          (19,  9, 'nw') : 1,
          (19,  9, 'ne') : 1,
          (19,  9,  'e') : 1,
          (19,  9, 'se') : 1,
          (20,  9,  'e') : 1,
          (20,  9, 'se') : 1,
          (21,  8,  'e') : 1,
          (22,  9, 'ne') : 1,
          (22,  9,  'e') : 1,
          (22,  9, 'se') : 1,
          (22,  9, 'sw') : 1, # END Indus
          ( 2, 19, 'ne') : 1, #START Jhelum
          ( 2, 19,  'e') : 1,
          ( 2, 19, 'se') : 1,
          ( 3, 18,  'e') : 1,
          ( 3, 18, 'se') : 1,
          ( 3, 18, 'sw') : 1,
          ( 3, 17, 'se') : 1,
          ( 4, 17,  'e') : 1,
          ( 4, 17, 'se') : 1,
          ( 5, 16,  'e') : 1,
          ( 5, 16, 'se') : 1,
          ( 6, 16,  'e') : 1,
          ( 6, 16, 'se') : 1,
          ( 7, 15,  'e') : 1,
          ( 8, 16, 'ne') : 1,
          ( 8, 16,  'e') : 1,
          ( 8, 16, 'se') : 1,
          ( 8, 16, 'sw') : 1,
          ( 8, 15, 'se') : 1,
          ( 9, 14,  'e') : 1,
          ( 9, 14, 'se') : 1,
          (10, 14,  'e') : 1,
          (11, 14, 'ne') : 1,
          (11, 14,  'e') : 1,
          (11, 14, 'se') : 1,
          (11, 14, 'sw') : 1, #END Jhelum, CONFLUENCE Jhelum + Indus
          ( 4, 19, 'se') : 1, # START Chenah
          ( 5, 18,  'e') : 1,
          ( 5, 18, 'se') : 1,
          ( 5, 18, 'sw') : 1,
          ( 5, 17, 'se') : 1,
          ( 6, 17,  'e') : 1,
          ( 6, 17, 'se') : 1,
          ( 7, 16,  'e') : 1,
          ( 7, 16, 'se') : 1, #END Chenah, CONFLUENCE Chenah + Jhelum
          ( 7, 24, 'sw') : 1, #START Sutlej
          ( 7, 23, 'se') : 1,
          ( 7, 23, 'sw') : 1,
          ( 7, 22, 'se') : 1,
          ( 7, 22, 'sw') : 1,
          ( 7, 21, 'se') : 1,
          ( 7, 21, 'sw') : 1,
          ( 7, 20, 'se') : 1,
          ( 8, 20,  'e') : 1,
          ( 8, 20, 'se') : 1,
          ( 8, 20, 'sw') : 1,
          ( 8, 19, 'se') : 1,
          ( 9, 18,  'e') : 1,
          ( 9, 18, 'se') : 1,
          ( 9, 18, 'sw') : 1,
          ( 9, 17, 'se') : 1,
          (10, 17,  'e') : 1,
          (10, 17, 'se') : 1,
          (10, 17, 'sw') : 1,
          (10, 16, 'se') : 1,
          (11, 15,  'e') : 1,
          (11, 15, 'se') : 1,
          (11, 15, 'sw') : 1, #END Sutlej, CONFLUENCE Sutlej + Jhelum
          ( 8, 27, 'se') : 1, # START Yamuna
          ( 8, 27, 'sw') : 1,
          ( 8, 26, 'se') : 1,
          ( 9, 25,  'e') : 1,
          ( 9, 25, 'se') : 1,
          (10, 25,  'e') : 1,
          (10, 25, 'se') : 1,
          (11, 24,  'e') : 1,
          (12, 25, 'ne') : 1,
          (12, 26,  'w') : 1,
          (12, 25,  'e') : 1,
          (13, 25, 'ne') : 1,
          (13, 25,  'e') : 1,
          (14, 26, 'ne') : 1,
          (14, 26,  'e') : 1,
          (15, 26, 'ne') : 1,
          (15, 26,  'e') : 1,
          (16, 27, 'ne') : 1,
          (16, 27,  'e') : 1,
          (17, 27, 'nw') : 1,
          (17, 27, 'ne') : 1, # CONFLUENCE with Chambal
          (17, 28, 'nw') : 1, # CONFLUENCE with Chambal
          (17, 28, 'ne') : 1,
          (17, 28,  'e') : 1,
          (18, 29, 'ne') : 1,
          (18, 29,  'e') : 1,
          (19, 29, 'ne') : 1,
          (19, 29,  'e') : 1, # BETWAH
          (19, 30, 'nw') : 1,
          (19, 30, 'ne') : 1,
          (19, 30,  'e') : 1,
          (20, 31, 'ne') : 1,
          (20, 32, 'nw') : 1,
          (20, 32, 'ne') : 1,
          (20, 32,  'e') : 1,
          (21, 32, 'ne') : 1,
          (21, 33, 'nw') : 1, # END Yamuna
          ( 8, 30,  'e') : 1, #START Ganges
          ( 8, 30, 'se') : 1,
          ( 8, 30, 'sw') : 1,
          ( 8, 29, 'se') : 1,
          ( 9, 28,  'e') : 1,
          ( 9, 28, 'se') : 1,
          ( 9, 28, 'sw') : 1,
          ( 9, 27, 'se') : 1,
          (10, 27,  'e') : 1,
          (10, 27, 'se') : 1,
          (11, 26,  'e') : 1,
          (12, 27, 'ne') : 1,
          (12, 27,  'e') : 1,
          (13, 27, 'ne') : 1,
          (13, 27,  'e') : 1,
          (14, 28, 'ne') : 1,
          (14, 28,  'e') : 1,
          (15, 28, 'ne') : 1,
          (15, 28,  'e') : 1,
          (16, 29, 'ne') : 1,
          (16, 30, 'nw') : 1,
          (16, 30, 'ne') : 1,
          (16, 30,  'e') : 1,
          (17, 30, 'ne') : 1,
          (17, 30,  'e') : 1,
          (18, 31, 'ne') : 1,
          (18, 31,  'e') : 1,
          (19, 31, 'ne') : 1,
          (19, 32, 'nw') : 1,
          (19, 32, 'ne') : 1,
          (19, 32,  'e') : 1,
          (20, 33, 'ne') : 1,
          (20, 33,  'e') : 1,
          (21, 33, 'ne') : 1, #CONFLUENCE Ganges + Yamuna
          (21, 34, 'nw') : 1,
          (21, 34, 'ne') : 1,
          (21, 35, 'nw') : 1,
          (21, 35, 'ne') : 1,
          (21, 36, 'nw') : 1,
          (20, 37,  'w') : 1,
          (20, 37, 'nw') : 1,
          (20, 37, 'ne') : 1,
          (20, 38, 'nw') : 1,
          (20, 38, 'ne') : 1,
          (20, 39, 'nw') : 1,
          (20, 39, 'ne') : 1,
          (20, 40, 'nw') : 1,
          (20, 40, 'ne') : 1,
          (20, 41, 'nw') : 1,
          (20, 41, 'ne') : 1,
          (20, 42, 'nw') : 1,
          (20, 42, 'ne') : 1,
          (20, 43, 'nw') : 1,
          (20, 43, 'ne') : 1,
          (20, 44, 'nw') : 1,
          (20, 44, 'ne') : 1,
          (20, 44,  'e') : 1,
          (21, 44, 'ne') : 1,
          (21, 44,  'e') : 1,
          (22, 45, 'ne') : 1,
          (22, 45,  'e') : 1,
          (22, 45, 'se') : 1,
          (23, 44,  'e') : 1,
          (24, 45, 'ne') : 1,
          (24, 45,  'e') : 1,
          (25, 45, 'ne') : 1,
          (25, 45,  'e') : 1,
          (25, 45, 'se') : 1,
          (26, 45,  'e') : 1,
          (26, 45, 'se') : 1,
          (26, 46,  'w') : 1, # FIX printing over red hex?
          (27, 44,  'e') : 1, # END Ganges 1
          (26, 45, 'se') : 1,
          (18, 25, 'se') : 1, # START Chambal
          (18, 25,  'e') : 1,
          (17, 25, 'se') : 1,
          (17, 26, 'sw') : 1,
          (17, 26, 'se') : 1,
          (17, 26,  'e') : 1, # END Chambal
          (22, 27,  'e') : 1, # START Betwa
          (21, 27, 'se') : 1,
          (21, 27,  'e') : 1,
          (20, 28, 'se') : 1,
          (20, 28,  'e') : 1,
          (19, 28, 'se') : 1,
          (19, 29, 'sw') : 1,
          (19, 29, 'se') : 1,
          (19, 29,  'e') : 1, # END Betwa
          (14, 32, 'ne') : 1, # START Ghaghara
          (14, 32,  'e') : 1,
          (15, 32, 'ne') : 1,
          (15, 32,  'e') : 1,
          (16, 33, 'ne') : 1,
          (16, 33,  'e') : 1,
          (17, 33, 'ne') : 1,
          (17, 34, 'nw') : 1,
          (17, 34, 'ne') : 1,
          (17, 34,  'e') : 1,
          (18, 35, 'ne') : 1,
          (18, 36, 'nw') : 1,
          (18, 36, 'ne') : 1,
          (18, 36,  'e') : 1,
          (19, 36, 'ne') : 1,
          (19, 37, 'nw') : 1,
          (19, 37, 'ne') : 1,
          (19, 38, 'nw') : 1,
          (19, 38, 'ne') : 1,
          (19, 38,  'e') : 1, # END Ghaghara
          (16, 38, 'ne') : 1, # START Gandak
          (16, 38,  'e') : 1,
          (17, 38, 'ne') : 1,
          (17, 38,  'e') : 1,
          (18, 39, 'ne') : 1,
          (18, 39,  'e') : 1,
          (19, 39, 'ne') : 1,
          (19, 39,  'e') : 1, # END Gandak
          (22, 36, 'se') : 1, # START Son
          (22, 36,  'e') : 1,
          (21, 36, 'se') : 1,
          (21, 37, 'sw') : 1,
          (21, 37, 'se') : 1,
          (21, 37,  'e') : 1,
          (20, 38, 'se') : 1,
          (20, 39, 'sw') : 1,
          (20, 39, 'se') : 1,
          (20, 39,  'e') : 1, # END Son
          (16, 42, 'nw') : 1, # START Kosi
          (16, 42, 'ne') : 1,
          (16, 42,  'e') : 1,
          (17, 42, 'ne') : 1,
          (17, 42,  'e') : 1,
          (17, 42, 'se') : 1,
          (17, 43, 'nw') : 1,
          (18, 42,  'e') : 1,
          (18, 42, 'se') : 1,
          (19, 41,  'e') : 1, # END Kosi
          (22, 46, 'nw') : 1, # START Ganges Branch 2
          (22, 46, 'ne') : 1,
          (22, 46,  'e') : 1,
          (23, 46, 'ne') : 1,
          (23, 46,  'e') : 1,
          (24, 47, 'ne') : 1,
          (24, 47,  'e') : 1,
          (25, 47, 'ne') : 1,
          (25, 47,  'e') : 1,
          (25, 47, 'se') : 1,
          (26, 47,  'e') : 1, # END Ganges Branch 2
          (23, 47, 'nw') : 1, # START Ganges Branch 3
          (23, 47, 'ne') : 1,
          (23, 47,  'e') : 1,
          (24, 48, 'ne') : 1,
          (24, 49, 'nw') : 1,
          (24, 49, 'ne') : 1,
          (25, 49, 'ne') : 1,
          (25, 49,  'e') : 1,
          (26, 50, 'ne') : 1,
          (25, 49, 'se') : 1, # END Ganges Branch 3
          (25, 50, 'ne') : 1, # Little bits at mouth of Ganges
          (26, 50,  'w') : 1,
          (26, 48,  'e') : 1,
          (12, 57,  'e') : 1, # START Brahmaputra
          (13, 57, 'ne') : 1,
          (13, 57,  'e') : 1,
          (14, 58, 'ne') : 1,
          (14, 58,  'e') : 1,
          (14, 58, 'se') : 1,
          (15, 57,  'e') : 1,
          (15, 57, 'se') : 1,
          (16, 57,  'e') : 1,
          (16, 57, 'se') : 1,
          (16, 57, 'sw') : 1,
          (16, 56, 'se') : 1,
          (16, 56, 'sw') : 1,
          (16, 55, 'se') : 1,
          (16, 55, 'sw') : 1,
          (16, 54, 'se') : 1,
          (16, 54, 'sw') : 1,
          (16, 53, 'se') : 1,
          (17, 52,  'e') : 1,
          (17, 52, 'se') : 1,
          (17, 52, 'sw') : 1,
          (17, 51, 'se') : 1,
          (17, 51, 'sw') : 1,
          (17, 50, 'se') : 1,
          (17, 50, 'sw') : 1,
          (17, 49, 'se') : 1,
          (17, 49, 'sw') : 1,
          (17, 48, 'se') : 1,
          (18, 48,  'e') : 1,
          (18, 48, 'se') : 1,
          (19, 47,  'e') : 1,
          (20, 48, 'ne') : 1,
          (20, 48,  'e') : 1,
          (20, 48, 'se') : 1,
          (21, 47,  'e') : 1,
          (22, 48, 'ne') : 1,
          (22, 48,  'e') : 1,
          (22, 48, 'se') : 1, # END Brahmaputra
          (25, 27, 'se') : 1, # START Narmada
          (25, 27, 'sw') : 1,
          (25, 26, 'se') : 1,
          (26, 26,  'e') : 1,
          (26, 26, 'se') : 1,
          (26, 26, 'sw') : 1,
          (26, 25, 'se') : 1,
          (26, 25, 'sw') : 1,
          (26, 24, 'se') : 1,
          (27, 23,  'e') : 1,
          (27, 23, 'se') : 1,
          (27, 23, 'sw') : 1,
          (27, 22, 'se') : 1,
          (27, 22, 'sw') : 1,
          (27, 21, 'se') : 1,
          (27, 21, 'sw') : 1,
          (27, 20, 'se') : 1,
          (27, 20, 'sw') : 1,
          (27, 19, 'se') : 1,
          (27, 19, 'sw') : 1,
          (27, 18, 'se') : 1,
          (28, 18,  'e') : 1,
          (28, 18, 'se') : 1,
          (28, 18, 'sw') : 1, # END Narmada
          (28, 34,  'e') : 1, # START Mahandadi
          (29, 34, 'ne') : 1,
          (29, 35, 'nw') : 1,
          (29, 35, 'ne') : 1,
          (29, 36, 'nw') : 1,
          (29, 36, 'ne') : 1,
          (29, 37, 'nw') : 1,
          (29, 37, 'ne') : 1,
          (29, 37,  'e') : 1,
          (30, 38, 'ne') : 1,
          (30, 38,  'e') : 1,
          (31, 38, 'ne') : 1,
          (31, 39, 'nw') : 1,
          (31, 39, 'ne') : 1,
          (31, 40, 'nw') : 1,
          (31, 40, 'ne') : 1,
          (31, 41, 'nw') : 1,
          (31, 41, 'ne') : 1,
          (31, 41,  'e') : 1,
          (31, 42, 'nw') : 1,
          (31, 42, 'ne') : 1, # END Mahandadi
          (34, 26, 'nw') : 1, # START Godavari
          (34, 26, 'ne') : 1,
          (34, 26,  'e') : 1,
          (35, 26, 'ne') : 1,
          (35, 27, 'nw') : 1,
          (35, 27, 'ne') : 1,
          (35, 28, 'nw') : 1,
          (35, 28, 'ne') : 1,
          (35, 29, 'nw') : 1,
          (35, 29, 'ne') : 1,
          (35, 30, 'nw') : 1,
          (35, 30, 'ne') : 1,
          (35, 30,  'e') : 1,
          (36, 31, 'ne') : 1,
          (36, 32, 'nw') : 1,
          (36, 32, 'ne') : 1,
          (36, 32,  'e') : 1,
          (36, 32, 'se') : 1,
          (37, 31,  'e') : 1,
          (38, 32, 'ne') : 1,
          (38, 33, 'nw') : 1,
          (38, 33, 'ne') : 1,
          (38, 33,  'e') : 1,
          (39, 33, 'ne') : 1,
          (39, 33,  'e') : 1, # END Godavari
          (39, 22, 'sw') : 1, # START Krishna
          (39, 22, 'se') : 1,
          (39, 23, 'sw') : 1,
          (39, 23, 'sw') : 1,
          (40, 24,  'w') : 1,
          (40, 24, 'sw') : 1,
          (40, 24, 'se') : 1,
          (40, 24,  'e') : 1,
          (39, 24, 'se') : 1,
          (39, 25, 'sw') : 1,
          (39, 25, 'se') : 1,
          (39, 26, 'sw') : 1,
          (40, 27,  'w') : 1,
          (40, 27, 'sw') : 1,
          (40, 27, 'se') : 1,
          (40, 28, 'sw') : 1,
          (40, 28, 'se') : 1,
          (40, 28,  'e') : 1,
          (39, 28, 'se') : 1,
          (39, 29, 'sw') : 1,
          (39, 29, 'se') : 1,
          (39, 30, 'sw') : 1,
          (39, 30, 'se') : 1,
          (39, 31, 'sw') : 1,
          (39, 31, 'se') : 1,
          (39, 32, 'sw') : 1, # END Krishna
          (41, 23, 'sw') : 1, # START Tungabhadra
          (41, 23, 'se') : 1,
          (41, 24, 'sw') : 1,
          (41, 24, 'se') : 1,
          (41, 24,  'e') : 1,
          (40, 25, 'se') : 1,
          (40, 26, 'sw') : 1,
          (40, 26, 'se') : 1, # END Tungabhadra
          (43, 28,  'w') : 1, # START Penneru
          (43, 28, 'sw') : 1,
          (43, 28, 'se') : 1,
          (43, 29, 'sw') : 1,
          (43, 29, 'se') : 1,
          (43, 30, 'sw') : 1,
          (43, 30, 'se') : 1, # END Penneru
          (49, 26,  'w') : 1, # START Kaveri
          (49, 26, 'sw') : 1,
          (50, 27,  'w') : 1,
          (50, 27, 'sw') : 1,
          (51, 27,  'w') : 1,
          (51, 27, 'sw') : 1,
          (51, 27, 'se') : 1,
          (51, 28, 'sw') : 1,
          (51, 28, 'se') : 1,
          (51, 28,  'e') : 1,
          (50, 29, 'se') : 1,
          (50, 30, 'sw') : 1 # END Kaveri
        }
rivers_at = set([(i,j) for (i,j,k) in rivers])

compass_dirs = ['e', 'ne', 'se', 'w', 'nw', 'sw']

inv_names = {name: coord for coord, name in hex_names.items()}

resources = {}

for name, rsc_list in resources_by_name.iteritems():
    coord = inv_names[name]
    resources[coord] = rsc_list


inv_resources = {}
for coord, rsc_list in resources.iteritems():
    for rsc in rsc_list:
        inv_resources[rsc] = inv_resources.get(rsc, [])
        inv_resources[rsc].append(coord)