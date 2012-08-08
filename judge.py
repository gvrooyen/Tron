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

    def adjudicate(self, statefile, new_move = True):
        """
        Analyse the statefile, to check that it is consistent with the current world state (and raise an
        exception if this is not the case). By default, the adjudicate() method also incorporates a single
        new move into the world state. A valid move:

          1. Changes the previous PLAYER position into a PLAYER_WALL
          2. Places PLAYER at a position adjacent (left/front/right) to its previous position, where this
             position was previously empty.

        Lastly, the adjudicate() method also analyses both players' final positions, to determine whether
        each has at least one valid move remaining. A player without a valid move remaining, loses. In
        the case where both players have no valid moves remaining, it implies that the current player has
        just moved into the opponent's last liberty, and that the opponent (who should move next) has no
        valid move left. In such a case, the opponent loses.
        """


