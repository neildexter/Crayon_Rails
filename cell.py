from globals import *
import pygame as pg, operator as op, math as m, time, random

class Cell(object):
    def __init__(self, terrain, name):
        # This will be in a dictionary {loc : terrain}
        self.terrain = terrain
        # Taken care of with global variable hex_names
        self.name = name

        # if 0, no track; if a number, track belongs to player #
        # This will be in a dictionary { loc + (dir,) : value }
        self.tracks = {"ne": 0,
                       "e": 0,
                       "se": 0,
                       "sw": 0,
                       "w": 0,
                       "nw": 0}
        #starts from ne and goes clockwise to nw
        # Taken care of with global variable rivers
        self.rivers = {"ne": 0,
                       "e": 0,
                       "se": 0,
                       "sw": 0,
                       "w": 0,
                       "nw": 0}