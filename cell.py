from globals import *
import pygame as pg, operator as op, math as m, time, random

class Cell(object):
    def __init__(self, terrain, name):
        self.terrain = terrain
        self.name = name

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