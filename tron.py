__author__ = 'gvrooyen'

from constants import *
import random

class Position(object):
    """Position on spherical coordinates."""

    def __init__(self, pos, world_size = 30):
        self.pos = pos
        self.world_size = world_size

        # TODO: Assert that pos has valid world coordinates

    def __getitem__(self, item):
        return self.pos[item]

    def north(self):
        """Returns the coordinates north of the current position, or None if it's the north pole."""

        if self.pos[1] == 0:
            return None
        else:
            return (self.pos[0], self.pos[1]-1)

    def south(self):
        """Returns the coordinates south of the specified position, or None if it's the south pole."""

        if self.pos[1] == self.world_size - 1:
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

    def at_north_pole(self):
        return self.pos[1] == 0

    def at_south_pole(self):
        return self.pos[1] == self.world_size - 1

    def go_north(self):
        new_pos = self.north()
        if new_pos:
            self.pos = new_pos
        else:
            raise RuntimeError("Cannot move north from the north pole.")

    def go_south(self):
        new_pos = self.south()
        if new_pos:
            self.pos = new_pos
        else:
            raise RuntimeError("Cannot move north from the north pole.")

    def go_west(self):
        self.pos = self.west()

    def go_east(self):
        self.pos = self.east()

    def is_adjacent(self, pos):
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

