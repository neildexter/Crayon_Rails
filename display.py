from globals import *
import pygame as pg

def display(brd):
    # Uses first (index [0]) of corner function to get x value (width)
    screen_width = int(m.floor(corner(0, brd.width)[0] + hex_width / 2 + left_pad + right_pad))
    # Uses second (index [1]) of corner function to get y value (width)
    screen_height = int(m.floor(corner(brd.height, 0)[1] + top_pad + bot_pad))


    print screen_height

    screen = pg.display.set_mode([screen_width, screen_height])
    screen.fill(white)

    for i in range(brd.height):
        for j in range(brd.width):
            screen.blit(draw_hex_surf(brd.get(i,j),(i,j)), corner(i, j))
    pg.display.flip()

# Returns the coordinate for the upper left hand corner of a hex image as placed on the board
def corner(i, j):
    if i % 2 == 0:  # if row number is even
        x = left_pad - hex_gap + hex_width*j
    else:
        x = left_pad - hex_gap + hex_width*(j + 0.5)

    y = top_pad + (h/2.0 + hex_width/(2.0*m.sqrt(3.0)))*i

    return (x, y)

def plain(hex_surf):
    pg.draw.circle(hex_surf, black, (h / 2, h / 2), h/12, 0)

def draw_center_triang(hex_surf, color, width):
    wth = h/7.
    pg.draw.polygon(hex_surf, color,
                    [(h/2. - wth*1.2, h/2. + wth),
                     (h/2.,           h/2. - wth),
                     (h/2. + wth*1.2, h/2. + wth),
                     (h/2. - wth*1.2, h/2. + wth)], width)

def mount(hex_surf):
    draw_center_triang(hex_surf,black,0)

def desert(hex_surf):
    # Fill with yellow
    pg.draw.circle(hex_surf, yellow, (h/2, h/2), h/12, 0)
    # Black border
    pg.draw.circle(hex_surf, black, (h/2, h/2), h/12, 1)

def alp(hex_surf):
    # Draw polygon with white
    draw_center_triang(hex_surf,white,0)
    # Draw border in black
    draw_center_triang(hex_surf,black,1)

def salt_flat(hex_surf):
    size = h / 2
    # Define letter as a font object
    letter = pg.font.Font(None, size)
    # Render the letter S with anti-aliasing
    pic = letter.render("S", 1, blue_salt, color_key)
    # letter.metrics("S") # gives the drawn characteristics of text entered
    # 	minx, 	maxx,	miny, 	maxy, 	advance
    pic.set_colorkey(color_key)
    hex_surf.blit(pic, (h/2 - .45*size/2., h/2 - .80 * size/2.))

def city_s(hex_surf):
    # Large circle (2x radius), filled with red
    pg.draw.circle(hex_surf, red, (h/2, h/2), h/4, 0)
    # Small circle (normal radius) filled with black
    pg.draw.circle(hex_surf, black, (h/2, h/2), h/12, 0)

def city_m(hex_surf):
    width = int(2. * h / 4.)
    height = width  # since square
    left = (h - width) / 2
    top = left  # same coordinate for both since square
    pg.draw.rect(hex_surf, red, pg.Rect((left, top), (width, height)), 0)
    pg.draw.circle(hex_surf, black, (h/2, h/2), h/12, 0)

def city_l(hex_surf):  #STILL NOT DEFINED
    #placeholder
    pg.draw.polygon(hex_surf, red,
        [(h/2+1,0), (h-hex_gap, h/4),
        (h-hex_gap, 3*h/4), (h/2,h),
        (hex_gap, 3*h/4), (hex_gap, h/4),
        (h/2-1,0)], 0)
    pg.draw.circle(hex_surf, black, (h/2, h/2), h/12, 0)

def water(hex_surf):
    pg.draw.polygon(hex_surf, blue_water,
        [(h/2+1,0), (h-hex_gap, h/4),
        (h-hex_gap, 3*h/4), (h/2,h),
        (hex_gap, 3*h/4), (hex_gap, h/4),
        (h/2-1,0)], 0)

def impassable_land(hex_surf):
    pg.draw.polygon(hex_surf, brown,
        [(h/2+1,0), (h-hex_gap, h/4),
        (h-hex_gap, 3*h/4), (h/2,h),
        (hex_gap, 3*h/4), (hex_gap, h/4),
        (h/2-1,0)], 0)
def ferry(hex_surf):
    1+1 # Print pretty anchor picture

# Prints the name (not called from terrain graphic dictionary!!)
def print_name(hex_surf,name):
    size = h/3
    # Define letter as a font object
    letter = pg.font.Font(None, size)
    #  Render the letter S with anti-aliasing
    pic = letter.render(name, 1, black, color_key)
    # #print letter.metrics("X")
    # #[(	2, 		43, 	-2, 	49, 	45)]
    # minx, 	maxx,	miny, 	maxy, 	advance
    pic.set_colorkey(color_key)
    hex_surf.blit(pic, (0, 0))

def print_rivers(hex_surf, loc):
    for direction in compass_dirs:
        if loc+(direction,) in rivers:
            pg.draw.line(hex_surf, blue_water,river_edge[direction][0], river_edge[direction][1], river_width)

def draw_hex_surf(cell, loc):
    hex_surf = pg.Surface((h, h+2))
    hex_surf.fill(color_key)
    hex_surf.set_colorkey(color_key)
    # if cell.terrain == 'w':
    #     color = blue
    #     line_width = 0
    # else:
    #     color = gray
    #     line_width = hex_line_width
    # Draws hexagonal border around each item
    # Could reuse for drawing rivers?
    #
    # pg.draw.polygon(self.hex_image, color,
    #     [(h/2,0), (h-hex_gap, h/4),
    #     (h-hex_gap, 3*h/4), (h/2,h),
    #     (hex_gap, 3*h/4), (hex_gap, h/4),
    #     (h/2,0)], line_width)

    for direction in cell.tracks:
        num = cell.tracks[direction]
        if num != 0:
            pg.draw.line(hex_surf, player_color[num], (h / 2, h / 2), track_endpts[direction], rail_width)

    terrain_graphic[cell.terrain](hex_surf)

    print_rivers(hex_surf, loc)

    if cell.name != None:
        print_name(hex_surf,cell.name)
    return hex_surf

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