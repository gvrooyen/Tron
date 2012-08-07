__author__ = 'gvrooyen'

import random
import tron
from constants import *

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, world_size = 30):

        blue = (random.randint(0, world_size-1), random.randint(0, world_size-1))
        red = blue
        while red == blue:
            red = (random.randint(0, world_size-1), random.randint(0, world_size-1))

        # Start with an empty world
        self.world = tron.World(world_size=world_size)

        for x in xrange(0, world_size):
            for y in xrange(0, world_size):
                if (x,y) == blue:
                    self.world[x][y] = BLUE
                elif (x,y) == red:
                    self.world[x][y] = RED
                else:
                    self.world[x][y] = EMPTY

