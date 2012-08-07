__author__ = 'gvrooyen'

import random
import tron
from constants import *

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, state_file_blue, state_file_red, world_size = 30):

        try:
            with open(state_file_blue), open(state_file_red):
                pass
        except IOError:
            # If one or more of the state files don't yet exist, initialize with random player positions.
            blue = (random.randint(0, world_size-1), random.randint(0, world_size-1))
            red = blue
            while red == blue:
                red = (random.randint(0, world_size-1), random.randint(0, world_size-1))

            # Start with an empty world
            self.world = tron.World()

            with open(state_file_blue, 'w') as f1, open(state_file_red, 'w') as f2:
                for x in xrange(0, world_size):
                    for y in xrange(0, world_size):
                        if (x,y) == blue:
                            f1.write('%d %d %s\n' % (blue + ('You',)))
                            f2.write('%d %d %s\n' % (blue + ('Opponent',)))
                            self.world[x][y] = PLAYER
                        elif (x,y) == red:
                            f1.write('%d %d %s\n' % (red + ('Opponent',)))
                            f2.write('%d %d %s\n' % (red + ('You',)))
                            self.world[x][y] = OPPONENT
                        else:
                            f1.write('%d %d %s\n' % (x,y, 'Clear'))
                            f2.write('%d %d %s\n' % (x,y, 'Clear'))
                            self.world[x][y] = EMPTY

        else:
            self.world = tron.World(state_file_blue)


