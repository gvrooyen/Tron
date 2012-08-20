__author__ = 'gvrooyen'

from constants import *
import random
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler)

class Position(object):
    """Position on spherical coordinates."""

    def __init__(self, pos, world_size = 30):
        self.pos = pos
        self.world_size = world_size

        for i in [0, 1]:
            if (pos[i] < 0) or (pos[i] >= world_size):
                raise ValueError("Coordinates out of range: pos[%d] = %d" % (i,pos[i]))

    def __getitem__(self, item):
        return self.pos[item]

    def at_north_pole(self):
        return self.pos[1] == 0

    def at_south_pole(self):
        return self.pos[1] == self.world_size - 1

    def at_pole(self):
        return self.at_north_pole() or self.at_south_pole()

    def north(self):
        """Returns the coordinates north of the current position, or None if it's at one of the poles."""

        if self.at_pole():
            return None
        else:
            return (self.pos[0], self.pos[1]-1)

    def south(self):
        """Returns the coordinates south of the specified position, or None if it's at one of the poles."""

        if self.at_pole():
            return None
        else:
            return (self.pos[0], self.pos[1]+1)

    def east(self):
        """Returns the coordinates east of the specified position."""

        if self.pos[0] == self.world_size - 1:
            return (0, self.pos[1])
        else:
            return (self.pos[0]+1, self.pos[1])

    def west(self):
        """Returns the coordinates west of the specified position."""

        if self.pos[0] == 0:
            return (self.world_size - 1, self.pos[1])
        else:
            return (self.pos[0]-1, self.pos[1])

    def go_north(self, lon=None):
        """
        Move north from the current position. An optional 'lon' parameter is provided for the special case where
        the current position is the south pole. At the pole, all directions are north, and the caller needs to
        specify the meridian (longitude) which should be followed north.
        """
        new_pos = self.north()
        if new_pos:
            self.pos = new_pos
        else:
            if self.at_south_pole():
                if lon:
                    self.pos = (lon, self.world_size - 2)
                else:
                    raise RuntimeError("Ambiguous movement: all directions are north at the south pole.")
            else:
                raise RuntimeError("Cannot move further north from the north pole.")

    def go_south(self, lon=None):
        """
        Move south from the current position. An optional 'lon' parameter is provided for the special case where
        the current position is the north pole. At the pole, all directions are south, and the caller needs to
        specify the meridian (longitude) which should be followed south.
        """
        new_pos = self.south()
        if new_pos:
            self.pos = new_pos
        else:
            if self.at_north_pole():
                if lon:
                    self.pos = (lon, 0)
                else:
                    raise RuntimeError("Ambiguous movement: all directions are south at the north pole.")
            else:
                raise RuntimeError("Cannot move south from the south pole.")

    def go_west(self):
        self.pos = self.west()

    def go_east(self):
        self.pos = self.east()

    def is_adjacent(self, pos):

        # Firstly, a sanity check on the coordinates
        for i in [0, 1]:
            if (pos[i] < 0) or (pos[i] >= world_size):
                return False

        if self.at_south_pole():
            return pos[1] == world_size - 2
        elif self.at_north_pole():
            return pos[1] == 1
        else:
            return ((self.west() == pos) or (self.east() == pos) or (self.north() == pos) or (self.south() == pos))


class World(object):
    """World state for the Entelect AI challenge."""

    def __init__(self, state_file = None, world_size = 30):
        self.world_size = world_size

        # Initialize the world with Nones
        self.world = [[None for i in xrange(0, self.world_size)] for j in xrange(0, self.world_size)]

        if state_file:
            with open(state_file) as f:
                for line in f:
                    (x,y,state) = line.rstrip().split(' ')

                    s = state.lower()
                    self.world[int(x)][int(y)] = STATE_DICT[s]
                    if s == 'you':
                        self.pos_player = Position((int(x),int(y)), world_size)
                    elif s == 'opponent':
                        self.pos_opponent = Position((int(x),int(y)), world_size)
        else:
            self.pos_player = None
            self.pos_opponent = None

    def state(self, pos):
        if pos:
            return self.world[pos[0]][pos[1]]
        else:
            return None

    def set_state(self, pos, state):
        if pos:
            self.world[pos[0]][pos[1]] = state

    def move_player(self, pos, opponent=False):
        if opponent:
            self.set_state(self.pos_opponent, OPPONENT_WALL)
            self.set_state(pos, OPPONENT)
            self.pos_opponent = pos
        else:
            self.set_state(self.pos_player, PLAYER_WALL)
            self.set_state(pos, PLAYER)
            self.pos_player = pos

    def move_blue(self, pos):
        self.move_player(pos)

    def move_red(self, pos):
        self.move_player(pos, opponent=True)

    def liberties(self, opponent=False):
        """
        Count the number of liberties that the player (or opponent) has available. A liberty is defined as a clear
        space adjacent to the current player (opponent) position.
        """
        if opponent:
            pos = self.pos_opponent
        else:
            pos = self.pos_player

        result = 0
        if self.state(Position(pos).north()) == EMPTY:
            result += 1
        if self.state(Position(pos).south()) == EMPTY:
            result += 1
        if self.state(Position(pos).east()) == EMPTY:
            result += 1
        if self.state(Position(pos).west()) == EMPTY:
            result += 1

        return result

    def save(self, filename, player=BLUE):

        OWN_WALL = BLUE_WALL if player == BLUE else RED_WALL
        OTHER_WALL = RED_WALL if player == BLUE else BLUE_WALL
        OWN = player
        OTHER = RED if player == BLUE else BLUE

        with open(filename, 'w') as f:
            for x in xrange(0, self.world_size):
                for y in xrange(0, self.world_size):
                    f.write("%d %d " % (x, y))
                    if self.world[x][y] == EMPTY:
                        f.write("Clear\n")
                    elif self.world[x][y] == OWN:
                        f.write("You\n")
                    elif self.world[x][y] == OTHER:
                        f.write("Opponent\n")
                    elif self.world[x][y] == OWN_WALL:
                        f.write("YourWall\n")
                    elif self.world[x][y] == OTHER_WALL:
                        f.write("OpponentWall\n")
                    else:
                        raise ValueError("Unknown world element type at (%d,%d): %s" % (x,y,str(self.world[x][y])))


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



    def move(self, world, debug=False):
        """
        Perform the optimal move for this strategy, based on the world state.

        The default (dummy/reference) strategy is to make a random valid move.
        """

        moves = [NORTH, SOUTH, EAST, WEST]
        random.shuffle(moves)
        pos = Position(world.pos_player.pos)

        for m in moves:
            if (m == NORTH) and (not pos.at_north_pole()) and (world.state(pos.north()) == None):
                world.pos_player.go_north()
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
        if debug:
            logger.debug(pos)

        world.set_state(world.pos_player, PLAYER)
        world.set_state(pos, PLAYER_WALL)
