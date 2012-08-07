__author__ = 'gvrooyen'

from constants import *
import random

class Position(object):
    """Position on spherical coordinates."""

    def __init__(self, pos, world_size = 30):
        self.pos = pos
        self.world_size = world_size

    def north(self):
        """Returns the coordinates north of the current position, or None if it's the north pole."""

        if self.pos[1] == 0:
            return None
        else:
            return (self.pos[0], self.pos[1]-1)

    def south(self):
        """Returns the coordinates south of the specified position, or None if it's the south pole."""

        if pos[1] == self.world_size - 1:
            return None
        else:
            return (self.pos[0], self.pos[1]+1)

    def east(self):
        """Returns the coordinates east of the specified position."""

        if pos[0] == self.world_size - 1:
            return 0
        else:
            return (self.pos[0]+1, self.pos[1])

    def west(self):
        """Returns the coordinates west of the specified position."""

        if pos[0] == 0:
            return self.world_size - 1
        else:
            return (self.pos[0]-1, self.pos[1])

    def at_north_pole(self):
        return pos[1] == 0

    def at_south_pole(self):
        return pos[1] == self.world_size

    def go_north(self):
        new_pos = north()
        if new_pos:
            self.pos = new_pos
        else:
            raise RuntimeError("Cannot move north from the north pole.")

    def go_south(self):
        new_pos = south()
        if new_pos:
            self.pos = new_pos
        else:
            raise RuntimeError("Cannot move north from the north pole.")

    def go_west(self):
        self.pos = west()

    def go_east(self):
        self.pos = east()


class World(object):
    """World state for the Entelect AI challenge."""

    def __init__(self, state_file = None, world_size = 30):
        self.world_size = world_size

        # Initialize the world with Nones
        self.world = [[None for i in xrange(0, self.world_size)] for j in xrange(0, self.world_size)]

        if state_file:
            with open(state_file) as f:
                for line in f:
                    (x,y,state) = line.split(' ')

                    s = state.lower()
                    self.world[int(x)][int(y)] = STATE_DICT[s]
                    if s == 'you':
                        self.pos_player = Position((int(x),int(y)), world_size)
                    elif s == 'opponent':
                        self.pos_opponent = Position((int(x),int(y)), world_size)

    def state(self, pos):
        return self.world[pos[0]][pos[1]]


class Strategy(object):
    """Abstract base class for player strategies."""

    def heading(self, world, opponent = False):
        """Calculate the player's current heading."""

        if opponent:
            pos = world.pos_opponent
            me = OPPONENT
        else:
            pos = world.pos_player
            me = PLAYER

        if pos.at_north_pole():
            return SOUTH
        elif pos.at_south_pole():
            return NORTH
        elif world.state(pos.north()) == me:
            return SOUTH
        elif world.state(pos.south()) == me:
            return NORTH
        elif world.state(pos.east()) == me:
            return WEST
        elif world.state(pos.west()) == me:
            return EAST



    def move(self, world):
        """
        Perform the optimal move for this strategy, based on the world state.

        The default (dummy/reference) strategy is to make a random valid move.
        """

        moves = [NORTH, SOUTH, EAST, WEST]
        random.shuffle(moves)
        pos = world.pos_player

        for m in moves:
            if (m == NORTH) and (not pos.at_north_pole()) and (world.state(pos.north()) == None):
                pos.go_north()
                break
            elif (m == SOUTH) and (not pos.at_south_pole()) and (world.state(pos.south()) == None):
                world.pos_player.go_south()
                break
            elif (m == EAST) and (world.state(pos.east()) == None):
                world.pos_player.go_east()
                break
            elif (m == WEST) and (world.state(pos.west()) == None):
                world.pos_player.go_west()
                break

