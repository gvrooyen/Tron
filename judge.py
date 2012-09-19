__author__ = 'gvrooyen'

import random
import tron
from constants import *

class StateFileException(Exception):
    pass

#noinspection PyStringFormat
class Judge(object):

    def __init__(self, pos_blue = None, pos_red = None, world_size = 30, double_random_start = False):

        self.world_size = world_size

        if not pos_blue:
            # Exclude poles as starting positions
            pos_blue = (random.randint(0, world_size-1), random.randint(1, world_size-2))
        if not pos_red:
            pos_red = pos_blue
        while pos_red == pos_blue:
            if double_random_start:
                pos_red = (random.randint(0, world_size-1), random.randint(1, world_size-2))
            else:
                pos_red = ((pos_blue[0] + world_size/2) % world_size, pos_blue[1])

        # Start with an empty world
        self.world = tron.World(world_size=world_size)

        for x in xrange(0, world_size):
            for y in xrange(0, world_size):
                if (x,y) == pos_blue:
                    self.world.move_blue((x,y))
                elif (x,y) == pos_red:
                    self.world.move_red((x,y))

        self.trace_blue = [pos_blue]
        self.trace_red = [pos_red]

    def adjudicate(self, statefile, new_move = None):
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

        if (new_move == BLUE) or (new_move == None):
            OWN = BLUE
            OTHER = RED
            OWN_WALL = BLUE_WALL
            OTHER_WALL = RED_WALL
            own_position = self.world.pos_player
            other_position = self.world.pos_opponent
            trace = self.trace_blue
        else:
            OWN = RED
            OTHER = BLUE
            OWN_WALL = RED_WALL
            OTHER_WALL = BLUE_WALL
            own_position = self.world.pos_opponent
            other_position = self.world.pos_player
            new_wall = False
            trace = self.trace_red

        with open(statefile) as f:
            line_no = 0
            for line in f:
                line_no += 1
                (sx,sy,sstate) = line.rstrip().split(' ')
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
                        if new_move == None:
                            raise StateFileException("Game state file is inconsistent with internal world state " +
                                "at (%d,%d) at line %d." % (x,y,line_no))
                        elif state != PLAYER:
                            raise StateFileException("Unexpected state change at (%d,%d) at line %d." % (x,y,line_no))
                        elif state_update:
                            # An update of a previously empty state has already been done. This is not legal (the
                            # player may only move to one new position)
                            raise StateFileException("Too many changes to the player state: (%d,%d) at line %d."
                              % (x,y,line_no))

                        # Firstly, verify that this is a valid position to have changed, i.e. that the last player
                        # position is adjacent.
                        if not tron.Position(own_position).is_adjacent((x,y)):
                            raise StateFileException(("Player moved to a non-adjacent position from (%d,%d) to " +
                              "(%d,%d) at line %d") % (self.world.pos_player[0], self.world.pos_player[1],
                                                      x, y, line_no))

                        old_player_pos = own_position
                        new_player_pos = (x,y)

                elif self.world.state((x,y)) == OWN:
                    if (state == PLAYER):
                        if new_move != None:
                            raise StateFileException("Player hasn't made a move at (%d,%d) at line %d." % (x,y,line_no))
                    elif state == OPPONENT:
                        raise StateFileException("Unexpected replacement of player by opponent at (%d,%d) at line %d." %
                          (x,y,line_no))
                    elif (state == PLAYER_WALL):
                        if new_move == None:
                            raise StateFileException("Unexpected replacement of player by wall at (%d,%d) at line %d." %
                              (x,y,line_no))
                    elif state == OPPONENT_WALL:
                        raise StateFileException("Unexpected replacement of player by opponent wall at (%d,%d) " +
                            "at line %d." % (x,y,line_no))
                    else:
                        raise StateFileException("Unknown state at (%d,%d)." % (x,y))
                elif (self.world.state((x,y)) == OTHER) and (state != OPPONENT):
                    raise StateFileException("Opponent's position cannot change after a player's turn at " +
                                             "(%d,%d) at line %d." % (x,y,line_no))
                elif (((self.world.state((x,y)) == OWN_WALL) and (state != PLAYER_WALL)) or
                      ((self.world.state((x,y)) == OTHER_WALL) and (state != OPPONENT_WALL))):
                    raise StateFileException("Walls may not be modified at (%d,%d) at line %d." % (x,y,line_no))

            # After the entire state file has been read and checked, update the player position, and check that
            # the old player position has been replaced by a wall

            if new_player_pos:
                self.world.move_player(new_player_pos, opponent=(new_move==RED))

                if self.world.state(old_player_pos) != OWN_WALL:
                    raise StateFileException(("Previous player position at (%d,%d) should be replaced by " +
                                              "a player wall.") % (old_player_pos))
                trace.append(new_player_pos)

            # Next, do a few sanity checks, such as that there is only one player and one opponent, and that they
            # have the same number of walls (or one more for the player that has just moved).

            player_count = 0
            opponent_count = 0
            player_wall_count = 0
            opponent_wall_count = 0

            for x in xrange(0, self.world_size):
                for y in xrange(0, self.world_size):
                    state = self.world.state((x,y))
                    if state == PLAYER:
                        player_count += 1
                    elif state == OPPONENT:
                        opponent_count += 1
                    elif state == PLAYER_WALL:
                        player_wall_count += 1
                    elif state == OPPONENT_WALL:
                        opponent_wall_count += 1

            if (tron.Position(self.world.pos_player).at_south_pole() or
                tron.Position(self.world.pos_player).at_north_pole()):
                if (player_count != self.world_size):
                    raise StateFileException("Only one player position may be specified (there are %d)." % player_count)
            elif player_count != 1:
                raise StateFileException("Only one player position may be specified (there are %d)." % player_count)
            if (tron.Position(self.world.pos_opponent).at_south_pole() or
                tron.Position(self.world.pos_opponent).at_north_pole()):
                if (opponent_count != self.world_size):
                    raise StateFileException("Only one opponent position may be specified (there are %d)." % opponent_count)
            elif opponent_count != 1:
                raise StateFileException("Only one opponent position may be specified (there are %d)." % opponent_count)
#            if abs(player_wall_count - opponent_wall_count) > 1:
#                raise StateFileException("Imbalance between player and opponent's number of walls.")

            # Finally, check whether we have a winner, by seeing whether either player has zero liberties left.

            player_liberties = self.world.liberties()
            opponent_liberties = self.world.liberties(opponent=True)

            if new_move != None:
                # If the player has just made a move, first check to see if the opponent now has zero liberties left.
                # If so, the player wins (even if he himself has zero liberties left, because the opponent is forced
                # into defeat first). However, if the player has zero liberties left, but the opponent can still make
                # a move, the opponent wins.
                if opponent_liberties == 0:
                    return PLAYER
                elif player_liberties == 0:
                    return OPPONENT
            else:
                if (player_liberties == 0) and (opponent_liberties == 0):
                    raise StateFileException("Victory state unresolvable without knowing who made the last move.")
                elif (opponent_liberties == 0):
                    return PLAYER
                elif (player_liberties == 0):
                    return OPPONENT

            # No winner yet
            return None
