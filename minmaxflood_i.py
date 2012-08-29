__author__ = 'gvrooyen'

import tron
import random
from constants import *

class State(object):

    def __init__(self):

        self.turn = PLAYER

        # A list of valid moves from the current state, for the player whose turn it is. The list of moves is
        # a list of tuples of the form [((23,1), state1), ((22,2), state2), ((24,2), state3)]. Each element
        # specifies the world coordinates of the move, and the state object of the corresponding new world
        # state (or None if that state hasn't been expanded yet)
        self.valid_moves = []

        # The estimated utility of the current state
        self.utility = None

class Strategy(tron.Strategy):

    def move(self, world, debug=False):
        """
        Perform the optimal move for this strategy, based on the world state.

        This simple game tree search builds up a tree of player/opponent moves from the current game state.
        For each move, the utility of the game state is estimated by using the flood fill heuristic (ratio
        between flood fill areas). The game tree is expanded ply-by-ply, in order of descending estimated
        utility (for the player rounds), or ascending estimated utility (for the opponent rounds). This is
        done so that the search can be terminated after a set time, and the explored leaves backed up.
        """

        pos = tron.Position(world.pos_player.pos)

        # Handle the poles first, they're always tricksy

        if pos.at_south_pole():
            lons = range(0,world.world_size)
            random.shuffle(lons)
            for lon in lons:
                if world.state((lon,world.world_size-2)) == EMPTY:
                    world.pos_player.go_north(lon)
                    break
            else:
                raise tron.StrategyException("Trapped at the south pole!")
        elif pos.at_north_pole():
            lons = range(0,world.world_size)
            random.shuffle(lons)
            for lon in lons:
                if world.state((lon,1)) == EMPTY:
                    world.pos_player.go_south(lon)
                    break
            else:
                raise tron.StrategyException("Trapped at the south pole!")
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

        world.set_state(world.pos_player, PLAYER)
        world.set_state(pos, PLAYER_WALL)
