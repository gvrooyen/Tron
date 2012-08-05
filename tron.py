__author__ = 'gvrooyen'

from constants import *

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
                        self.pos_player = (int(x),int(y))
                    elif s == 'opponent':
                        self.pos_opponent = (int(x),int(y))

    def north(self, pos):
        """Returns the coordinates north of the specified position, or None if it's the north pole."""

        if pos[1] == 0:
            return None
        else:
            return (pos[0],pos[1]-1)

    def south(self, pos):
        """Returns the coordinates south of the specified position, or None if it's the south pole."""

        if pos[1] == self.world_size - 1:
            return None
        else:
            return (pos[0],pos[1]+1)

    def east(self, pos):
        """Returns the coordinates east of the specified position."""

        if pos[0] == self.world_size - 1:
            return 0
        else:
            return (pos[0]+1,pos[1])

    def west(self, pos):
        """Returns the coordinates west of the specified position."""

        if pos[0] == 0:
            return self.world_size - 1
        else:
            return (pos[0]-1,pos[1])



class Strategy(object):
    """Abstract base class for player strategies."""

    def heading(self, world, opponent = False):
        """Calculate the player's current heading."""



    def move(self, world):
        """Perform the optimal move for this strategy, based on the world state."""


