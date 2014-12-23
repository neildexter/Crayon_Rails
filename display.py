from globals import *
import pygame as pg

def display(brd):
    # Uses first (index [0]) of corner function to get x value (width)
    #screen_width = int(m.floor(corner(0, brd.width)[0] + hex_width / 2 + left_pad + right_pad))
    # Uses second (index [1]) of corner function to get y value (width)
    #screen_height = int(m.floor(corner(brd.height, 0)[1] + top_pad + bot_pad))
    # ORIGINAL PHOTO: 2897 = 56 wide

    # 1. Set background layer to image

    pg.display.set_mode((100,100))

    bg_layer = pg.image.load("Board3.JPG").convert()
    screen_width = bg_layer.get_width()
    screen_height = bg_layer.get_height()

    # Create screen and other layers to the same size as background
    screen = pg.display.set_mode([screen_width, screen_height])

    tracks_layer = pg.Surface((screen_width, screen_height))
    tracks_layer.fill(color_key)
    tracks_layer.set_colorkey(color_key)
    draw_tracks(brd, tracks_layer)

    terrain_layer = pg.Surface((screen_width, screen_height))
    terrain_layer.fill(color_key)
    terrain_layer.set_colorkey(color_key)
    draw_terrain(brd, terrain_layer)

    name_layer = pg.Surface((screen_width, screen_height))
    name_layer.fill(color_key)
    name_layer.set_colorkey(color_key)
    draw_names(name_layer)

    #pieces_layer = pg.Surface((screen_width, screen_height))

    screen.blit(bg_layer, (0,0))
    screen.blit(tracks_layer, (0,0))
    screen.blit(terrain_layer, (0,0))
    screen.blit(name_layer, (0,0))
    #screen.blit(pieces_layer, (0,0))

    # 1. Blit background (bg_layer)
    # 2. Blit tracks on top (tracks_layer)
    # 3. Blit terrain graphics (terrain_layer)
    # 4. Blit names/resources? (name_layer)
    # 5. Blit current positions of pieces (pieces_layer)

    pg.display.flip()

def draw_names(name_layer):
    for coord in hex_names.keys():
        pixel_loc = corner(coord, False)
        size = h/3
        # Define letter as a font object
        letter = pg.font.Font(None, size)
        #  Render the letter S with anti-aliasing
        pic = letter.render(hex_names[coord], 1, black, color_key)
        # #print letter.metrics("X")
        # #[(	2, 		43, 	-2, 	49, 	45)]
        # minx, 	maxx,	miny, 	maxy, 	advance
        pic.set_colorkey(color_key)
        name_layer.blit(pic, pixel_loc)


def draw_terrain(board, terrain_layer):
    for i in range(board.height):
        for j in range(board.width):
            terrain_graphic[board.terrain[(i,j)]](terrain_layer, (i,j))

def draw_tracks(board, tracks_layer):
    for track in board.tracks.keys():
        num = board.tracks[track]

        start = corner(track[0], True)
        end = corner(track[1], True)

        pg.draw.line(tracks_layer, player_color[num], start, end, rail_width)

# Returns the coordinate for the upper left hand corner of a hex image as placed on the board
def corner(loc, center = False):
    if loc[0] % 2 == 0:  # if row number is even
        x = left_pad - hex_gap_float + hex_width_float*loc[1]
    else:
        x = left_pad - hex_gap + hex_width_float*(loc[1] + 0.5)

    y = top_pad + (h_float/2.0 + hex_width_float/(2.0*m.sqrt(3.0)))*loc[0]

    if center:
        x += h/2
        y += h/2

    return (int(x), int(y))

def plain(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    pg.draw.circle(terrain_layer, black, pixel_loc, h/12, 0)

def draw_center_triang(terrain_layer, loc, color, width):
    pixel_loc = corner(loc, True)
    x = pixel_loc[0]
    y = pixel_loc[1]
    wth = h/7.
    pg.draw.polygon(terrain_layer, color,
                    [(x - wth*1.2, y + wth),
                     (x, y - wth),
                     (x + wth*1.2, y + wth),
                     (x - wth*1.2, y + wth)], width)
def mount(terrain_layer, loc):
    draw_center_triang(terrain_layer, loc,black,0)

def desert(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    # Fill with yellow
    pg.draw.circle(terrain_layer, yellow, pixel_loc, h/12, 0)
    # Black border
    pg.draw.circle(terrain_layer, black, pixel_loc, h/12, 1)

def alp(terrain_layer, loc):
    # Draw polygon with white
    draw_center_triang(terrain_layer, loc, white,0)
    # Draw border in black
    draw_center_triang(terrain_layer, loc, black,1)

def salt_flat(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    x = pixel_loc[0]
    y = pixel_loc[1]
    size = h / 2
    # Define letter as a font object
    letter = pg.font.Font(None, size)
    # Render the letter S with anti-aliasing
    pic = letter.render("S", 1, blue_salt, color_key)
    # letter.metrics("S") # gives the drawn characteristics of text entered
    # 	minx, 	maxx,	miny, 	maxy, 	advance
    pic.set_colorkey(color_key)
    terrain_layer.blit(pic, (x - .45*size/2., y - .80 * size/2.))

def city_s(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    # Large circle (2x radius), filled with red
    pg.draw.circle(terrain_layer, red, pixel_loc, h/4, 0)
    # Small circle (normal radius) filled with black
    pg.draw.circle(terrain_layer, black, pixel_loc, h/12, 0)

def city_m(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    x = pixel_loc[0]
    y = pixel_loc[1]
    width = int(2. * h / 4.)
    height = width  # since square

    left = int(x - h/2 + (h - width)/2)
    top = int(y - h/2 + (h - width)/2)

    pg.draw.rect(terrain_layer, red, pg.Rect((left, top), (width, height)), 0)
    pg.draw.circle(terrain_layer, black, pixel_loc, h/12, 0)

def city_l(terrain_layer, loc):
    pixel_loc = corner(loc, True)
    x = pixel_loc[0]
    y = pixel_loc[1]
    pg.draw.polygon(terrain_layer, red,
        [(x+1, y - h/2), (x+h/2-hex_gap, y-h/4),
        (x+h/2-hex_gap, y+h/4), (x,y+h/2),
        (x-h/2+hex_gap, y+h/4), (x-h/2+hex_gap, y-h/4),
        (x-1, y-h/2)], 0)
    pg.draw.circle(terrain_layer, black, pixel_loc, h/12, 0)

def water(terrain_layer, loc):
    1+1
    #pg.draw.polygon(hex_surf, blue_water,
    #    [(h/2+1,0), (h-hex_gap, h/4),
    #    (h-hex_gap, 3*h/4), (h/2,h),
    #    (hex_gap, 3*h/4), (hex_gap, h/4),
    #    (h/2-1,0)], 0)

def impassable_land(terrain_layer, loc):
    1+1
    #pg.draw.polygon(hex_surf, brown,
    #    [(h/2+1,0), (h-hex_gap, h/4),
    #    (h-hex_gap, 3*h/4), (h/2,h),
    #    (hex_gap, 3*h/4), (hex_gap, h/4),
    #    (h/2-1,0)], 0)

def ferry(terrain_layer, loc):
    1+1 # Print pretty anchor picture

# Prints the name (not called from terrain graphic dictionary!!)
# def print_name(hex_surf, name):
#     size = h/3
#     # Define letter as a font object
#     letter = pg.font.Font(None, size)
#     #  Render the letter S with anti-aliasing
#     pic = letter.render(name, 1, black, color_key)
#     # #print letter.metrics("X")
#     # #[(	2, 		43, 	-2, 	49, 	45)]
#     # minx, 	maxx,	miny, 	maxy, 	advance
#     pic.set_colorkey(color_key)
#     hex_surf.blit(pic, (0, 0))

# def draw_rivers(hex_surf, loc):
#     for direction in compass_dirs:
#         if loc+(direction,) in rivers:
#             pg.draw.line(hex_surf, blue_water,river_edge[direction][0], river_edge[direction][1], river_width)

    # if hex_names.get(loc,None) is not None:
    #     print_name(hex_surf,hex_names[loc])
    # return hex_surf

terrain_graphic = {"p": plain,
                    "m": mount,
                    "a": alp,
                    "d": desert,
                    "s": salt_flat,
                    "S": city_s,
                    "M": city_m,
                    "L": city_l,
                    "w": water,
                    "i": impassable_land,
                    "f": ferry}

river_edge = {'ne': [(h/2,       0),     (h-hex_gap, h/4)],
              'e' : [(h-hex_gap, h/4),   (h-hex_gap, 3*h/4)],
              'se': [(h-hex_gap, 3*h/4), (h/2,       h)],
              'sw': [(h/2,       h),     (hex_gap,   3*h/4)],
              'w' : [(hex_gap,   3*h/4), (hex_gap,   h/4)],
              'nw': [(hex_gap,   h/4),   (h/2,       0)] }