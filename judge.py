__author__ = 'gvrooyen'

import random
import tron
from constants import *

class StateFileException(Exception):
    pass

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, world_size = 30):

        self.world_size = world_size

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

        # Keep track of which positions were listed in the state file (all positions must be accounted for)
        visited = [[False for i in xrange(0, self.world_size)] for j in xrange(0, self.world_size)]

        state_update = False
        new_player_pos = None
        old_player_pos = None

        with open(statefile) as f:
            line_no = 0
            for line in f:
                line_no += 1
                (sx,sy,sstate) = line.split(' ')
                x = int(sx)
                y = int(sy)
                state = STATE_DICT[sstate.lower()]
                if not visited[x][y]:
                    visited[x][y]= True
                else:
                    raise StateFileException("Position (%d,%d) duplicated in line %d." % (x,y,line_no))
                if self.world.state((x,y)) == EMPTY:
                    if state == EMPTY:
                        # Nothing has changed
                        pass
                    else:
                        if state_update:
                            # An update of a previously empty state has already been done. This is not legal (the
                            # player may only move to one new position)
                            raise StateFileException("Too many changes to the player state: (%d,%d) at line %d."
                              % (x,y,line_no))

                        # Firstly, verify that this is a valid position to have changed, i.e. that the last player
                        # position is adjacent.
                        raise NotImplementedError()
                elif self.world.state((x,y)) == PLAYER:
                    if state == PLAYER:
                        raise StateFileException("Player hasn't made a move at (%d,%d) at line %d." % (x,y,line_no))
                    elif state == OPPONENT:
                        raise StateFileException("Unexpected replacement of player by opponent at (%d,%d) at line %d." %
                          (x,y,line_no))
                    elif state == PLAYER_WALL:
                        raise NotImplementedError()
                    elif state == OPPONENT_WALL:
                        raise StateFileException("Unexpected replacement of player by opponent wall at (%d,%d) " +
                            "at line %d." % (x,y,line_no))
                    else:
                        raise StateFileException("Unknown state at (%d,%d)." % (x,y))
                elif (self.world.state((x,y)) == OPPONENT) and (state != OPPONENT):
                    raise StateFileException("Opponent's position cannot change after a player's turn at " +
                                             " (%d,%d)." % (x,y))
                elif (((self.world.state((x,y)) == PLAYER_WALL) and (state != PLAYER_WALL)) or
                      ((self.world.state((x,y)) == OPPONENT_WALL) and (state != OPPONENT_WALL))):
                    raise StateFileException("Walls may not be modified at (%d,%d)." % (x,y))

