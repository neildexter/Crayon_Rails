from globals import *
import pygame as pg, operator as op, math, time, random

class Cell(object):
    def plain(self):
        pg.draw.circle(self.hex_image, black, (h / 2, h / 2), h / 20, 0)

    def draw_center_triang(self, color, width):
        pg.draw.polygon(self.hex_image, color,
                        [(h / 2. - h / (10), h / 2. + h / 10.),
                         (h / 2., h / 2. - h / 10.),
                         (h / 2. + h / (10), h / 2. + h / 10.),
                         (h / 2. - h / (10), h / 2. + h / 10.)], width)
    def mount(self):
        self.draw_center_triang(black,0)

    def desert(self):
        # Fill with yellow
        pg.draw.circle(self.hex_image, yellow, (h / 2, h / 2), h / 10, 0)
        # Black border
        pg.draw.circle(self.hex_image, black, (h / 2, h / 2), h / 10, 1)

    def alp(self):
        # Draw polygon with white
        self.draw_center_triang(white,0)
        # Draw border in black
        self.draw_center_triang(black,1)

    def swamp(self):
        size = h / 3
        # Define letter as a font object
        letter = pg.font.Font(None, size)
        # Render the letter S with anti-aliasing
        pic = letter.render("S", 1, blue, color_key)
        # letter.metrics("S") # gives the drawn characteristics of text entered
        # 	minx, 	maxx,	miny, 	maxy, 	advance
        pic.set_colorkey(color_key)
        self.hex_image.blit(pic, (h / 2 - .45 * size / 2., h / 2 - .80 * size / 2.))

    def city_s(self):
        # Large circle (2x radius), filled with red
        pg.draw.circle(self.hex_image, red, (h / 2, h / 2), h / 5, 0)
        # Small circle (normal radius) filled with black
        pg.draw.circle(self.hex_image, black, (h / 2, h / 2), h / 20, 0)

    def city_m(self):
        width = int(2. * h / 5.)
        height = width  # since square
        left = (h - width) / 2
        top = left  # same coordinate for both since square
        pg.draw.rect(self.hex_image, red, pg.Rect((left, top), (width, height)), 0)
        pg.draw.circle(self.hex_image, black, (h / 2, h / 2), h / 20, 0)

    def city_l(self):  #STILL NOT DEFINED
        #placeholder
        1 + 1

    def water(self):
        1 + 1

    def print_name(self):
        size = h / 3
        # Define letter as a font object
        letter = pg.font.Font(None, size)
        #  Render the letter S with anti-aliasing
        pic = letter.render(self.name, 1, black, color_key)
        # #print letter.metrics("X")
        # #[(	2, 		43, 	-2, 	49, 	45)]
        # minx, 	maxx,	miny, 	maxy, 	advance
        pic.set_colorkey(color_key)
        self.hex_image.blit(pic, (0, 0))


    def draw_rails(self):
        for direction in self.tracks:
            num = self.tracks[direction]
            if num != 0:
                pg.draw.line(self.hex_image, player_color[num], (h / 2, h / 2), track_endpts[direction], rail_width)

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
		pg.draw.polygon(self.hex_image, color,
			[(h/2,0), (h-hex_gap, h/4),
			(h-hex_gap, 3*h/4), (h/2,h),
			(hex_gap, 3*h/4), (hex_gap, h/4),
			(h/2,0)], line_width)
        """

        self.draw_rails()
        self.terrain_graphic[self.terrain]()
        if self.name != None:
            self.print_name()

    def __init__(self, terrain, name):
        self.terrain = terrain
        self.name = name
        self.hex_image = pg.Surface((h, h + 2))
        self.terrain_graphic = {"p": self.plain,
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
        self.tracks = {"ne": 0,
                       "e": 0,
                       "se": 0,
                       "sw": 0,
                       "w": 0,
                       "nw": 0}
        #starts from ne and goes clockwise to nw
        self.rivers = {"ne": 0,
                       "e": 0,
                       "se": 0,
                       "sw": 0,
                       "w": 0,
                       "nw": 0}
        self.create_display()