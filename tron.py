__author__ = 'gvrooyen'

from constants import *
import random
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler)

class PoleStateException(Exception):
    pass

class StrategyException(Exception):
    pass


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
            return Position((self.pos[0], self.pos[1]-1))

    def south(self):
        """Returns the coordinates south of the specified position, or None if it's at one of the poles."""

        if self.at_pole():
            return None
        else:
            return Position((self.pos[0], self.pos[1]+1))

    def east(self):
        """Returns the coordinates east of the specified position."""

        if self.pos[0] == self.world_size - 1:
            return Position((0, self.pos[1]))
        else:
            return Position((self.pos[0]+1, self.pos[1]))

    def west(self):
        """Returns the coordinates west of the specified position."""

        if self.pos[0] == 0:
            return Position((self.world_size - 1, self.pos[1]))
        else:
            return Position((self.pos[0]-1, self.pos[1]))

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
                if lon != None:
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
                if lon != None:
                    self.pos = (lon, 1)
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
            if (pos[i] < 0) or (pos[i] >= self.world_size):
                return False

        if self.at_south_pole():
            return pos[1] == self.world_size - 2
        elif self.at_north_pole():
            return pos[1] == 1
        elif Position(pos).at_south_pole():
            return self.pos[1] == self.world_size - 2
        elif Position(pos).at_north_pole():
            return self.pos[1] == 1
        else:
            return ((self.west().to_tuple() == pos) or (self.east().to_tuple() == pos)
                    or (self.north().to_tuple() == pos) or (self.south().to_tuple() == pos))

    def to_tuple(self):
        """
        Return the current position as a tuple. Poles are returned as (0,0) and (0,self.world_size-1), respectively
        (the x coordinate is normalised to 0).
        """
        if self.at_north_pole():
            return (0,0)
        elif self.at_south_pole():
            return (0,self.world_size-1)
        else:
            return self.pos


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
        if pos == None:
            return None
        elif pos[1] == 0:     # at north pole
            for i in xrange(1, self.world_size):
                if self.world[i][0] != self.world[0][0]:
                    raise PoleStateException("The north pole is in an inconsistent state at (%d,0)." % i)
            return self.world[0][0]
        elif pos[1] == self.world_size - 1:     # at south pole
            for i in xrange(1, self.world_size):
                if self.world[i][0] != self.world[0][0]:
                    raise PoleStateException("The south pole is in an inconsistent state at (%d,%d)." %
                                             (i, self.world_size-1))
            return self.world[0][self.world_size-1]
        else:
            return self.world[pos[0]][pos[1]]

    def set_state(self, pos, state):
        if pos == None:
            pass
        elif pos[1] == 0:   # at north pole
            for i in xrange(0, self.world_size):
                self.world[i][0] = state
        elif pos[1] == self.world_size - 1:     # at south pole
            for i in xrange(0, self.world_size):
                self.world[i][self.world_size-1] = state
        else:
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

        # As usual, the poles have to be treated carefully. Check for pole positions first, then handle the
        # more general case.

        if Position(pos).at_south_pole():
            for i in xrange(0, self.world_size):
                if self.state((i,self.world_size-2)) == EMPTY:
                    result += 1
        elif Position(pos).at_north_pole():
            for i in xrange(0, self.world_size):
                if self.state((i,1)) == EMPTY:
                    result += 1
        else:
            if self.state(Position(pos).north()) == EMPTY:
                result += 1
            if self.state(Position(pos).south()) == EMPTY:
                result += 1
            if self.state(Position(pos).east()) == EMPTY:
                result += 1
            if self.state(Position(pos).west()) == EMPTY:
                result += 1

        return result

    def empty_space(self):
        """
        Returns a set of empty spaces (coordinate tuples) in the world.

        Note that the poles are only included once, as (0,0) and (0,self.world_size-1)
        """

        result = set([])

        # Handle the poles first

        if self.state((0,0)) == EMPTY:
            result.add((0,0))
        if self.state((0,self.world_size-1)) == EMPTY:
            result.add((0,self.world_size-1))

        # Cycle through the rest of the world (i.e. all x coordinates, but with the poles' y coordinates excluded)

        for x in xrange(0,self.world_size):
            for y in xrange(1,self.world_size-1):
                if self.state((x,y)) == EMPTY:
                    result.add((x,y))

        return result

    def valid_moves(self, opponent=False):
        """
        Return a set of valid moves from the current player (opponent) position.
        """

        # TODO: Double-check this (order seemed to have been swopped around, fixed now but untested)
        if opponent:
            pos = self.pos_opponent
        else:
            pos = self.pos_player

        unclaimed = self.empty_space()
        result = set()

        if Position(pos).at_north_pole():
            adjacent = set([(x,1) for x in xrange(0,self.world_size)])
        elif Position(pos).at_south_pole():
            adjacent = set([(x,self.world_size-2) for x in xrange(0,self.world_size)])
        else:
            adjacent = {Position(pos).north().to_tuple(), Position(pos).south().to_tuple(),
                        Position(pos).east().to_tuple(), Position(pos).west().to_tuple()}
        for a in adjacent:
            if a in unclaimed:
                # unclaimed.remove(a)
                result.add(a)

        return result

    def prospect(self, opponent=False, plies=30):
        """
        A liberty-based heuristic that calculates how much occupiable free space surrounds a player.
        """

        unclaimed = self.empty_space()
        player_frontier = {self.pos_player}
        opponent_frontier = {self.pos_opponent}
        player_domain = set()
        opponent_domain = set()
        ply_count = 0

        while (ply_count < plies):
            ply_count += 1
            if opponent:
                frontier = opponent_frontier
                domain = opponent_domain
            else:
                frontier = player_frontier
                domain = player_domain
            new_frontier = set()
            for pos in frontier:
                # Find all adjacent coordinates that are still unclaimed, and claim them for the new frontier.
                # This duplicates code in the self.valid_moves() method; candidate for refactoring.
                if Position(pos).at_north_pole():
                    adjacent = set([(x,1) for x in xrange(0,self.world_size)])
                elif Position(pos).at_south_pole():
                    adjacent = set([(x,self.world_size-2) for x in xrange(0,self.world_size)])
                else:
                    adjacent = {Position(pos).north().to_tuple(), Position(pos).south().to_tuple(),
                                Position(pos).east().to_tuple(), Position(pos).west().to_tuple()}
                for a in adjacent:
                    if a in unclaimed:
                        unclaimed.remove(a)
                        new_frontier.add(a)
                domain.add(pos)
            if opponent:
                opponent_frontier = new_frontier
                opponent_domain = domain
            else:
                player_frontier = new_frontier
                player_domain = domain
            opponent = not opponent

        player_domain.update(player_frontier)
        opponent_domain.update(opponent_frontier)

        # print (len(player_domain), len(opponent_domain))
        return (player_domain, opponent_domain)




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

    def __init__(self):
        self.time_limit = 4.5

    def move(self, world, debug=False):
        """
        Perform the optimal move for this strategy, based on the world state.

        The default (dummy/reference) strategy is to make a random valid move.
        """

        pos = Position(world.pos_player.to_tuple())

        # Handle the poles first, they're always tricksy

        if pos.at_south_pole():
            lons = range(0,world.world_size)
            random.shuffle(lons)
            for lon in lons:
                if world.state((lon,world.world_size-2)) == EMPTY:
                    world.pos_player.go_north(lon)
                    break
            else:
                raise StrategyException("Trapped at the south pole!")
        elif pos.at_north_pole():
            lons = range(0,world.world_size)
            random.shuffle(lons)
            for lon in lons:
                if world.state((lon,1)) == EMPTY:
                    world.pos_player.go_south(lon)
                    break
            else:
                raise StrategyException("Trapped at the north pole!")
        else:
            moves = [NORTH, SOUTH, EAST, WEST]
            random.shuffle(moves)

            for m in moves:
                if (m == NORTH) and (world.state(pos.north()) == EMPTY):
                    world.pos_player.go_north()
                    break
                elif (m == SOUTH) and (world.state(pos.south()) == EMPTY):
                    world.pos_player.go_south()
                    break
                elif (m == EAST) and (world.state(pos.east()) == EMPTY):
                    world.pos_player.go_east()
                    break
                elif (m == WEST) and (world.state(pos.west()) == EMPTY):
                    world.pos_player.go_west()
                    break

        if debug:
            logger.debug(pos)

        world.set_state(world.pos_player, PLAYER)
        world.set_state(pos, PLAYER_WALL)
