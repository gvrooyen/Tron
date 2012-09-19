__author__ = 'gvrooyen'

import tron
import random
from constants import *
import time
import copy
from math import *

class State(object):

    def __init__(self, parent = None, move = None):

        # A list of valid moves from the current state, for the player whose turn it is. The list of moves is
        # a list of tuples of the form [((23,1), state1), ((22,2), state2), ((24,2), state3)]. Each element
        # specifies the world coordinates of the move, and the state object of the corresponding new world
        # state (or None if that state hasn't been expanded yet)
        self.valid_moves = []

        # The estimated utility of the current state
        self.utility = None

        self.parent = parent

        # The coordinates that the parent had to move to to arrive at this state. This is None for the root state.
        self.last_move = move

        # The optimal next move to make (set during minimax backpropagation)
        self.next_move = None

        # The depth (ply) of the current state in the game tree. This can also be used to determine whose
        # turn it is to play at this state -- even plies are for the player, odd plies are for the opponent.
        if parent == None:
            self.depth = 0
        else:
            self.depth = parent.depth + 1


    def render(self, world):
        """
        Return a deep copy of the world, with the current state (sequence of moves) applied.
        """

        result = copy.deepcopy(world)

        s = self
        player_leaf = True
        opponent_leaf = True
        while s.parent != None:
            if (s.depth % 2):
                if opponent_leaf:
                    result.set_state(s.last_move, OPPONENT)
                    result.pos_opponent = tron.Position(s.last_move)
                    opponent_leaf = False
                else:
                    result.set_state(s.last_move, OPPONENT_WALL)
            else:
                if player_leaf:
                    result.set_state(s.last_move, PLAYER)
                    result.pos_player = tron.Position(s.last_move)
                    player_leaf = False
                else:
                    result.set_state(s.last_move, PLAYER_WALL)
            s = s.parent

        return result




class Strategy(tron.Strategy):

    def utility(self, prospect):
        """
        Calculate the utility from a given prospect tuple (player_flood_liberties, opponent_flood_liberties),
        as returned by World.prospect(). This function can be varied to experiment with different ways of
        turning such a pair into a single real number.

        The current version returns a logarithm of the ratio between the flood-fill liberties. This results in
        negative utility for the player if the opponent is at an advantage, zero if they're equally balanced,
        or positive utility if the player is at an advantage. Plus or minus infinity indicates that the player
        or opponent wins outright.

        Note that the logarithm calculated here, though useful for debugging, adds no value to the utility
        calculation itself (it transforms a monotonic function into another monotonic function) and adds
        computational cost. This function should be simplified in production code.
        """

        # TODO: Optimise utility calculation

        if len(prospect[1]) == 0:
            if len(prospect[0]) == 0:
                return 0
            else:
                return float('inf')
        elif len(prospect[0]) == 0:
            return float('-inf')
        else:
            return 10*log10(1.0 * len(prospect[0]) / len(prospect[1]))


    def move(self, world, debug=False):
        """
        Perform the optimal move for this strategy, based on the world state.

        This simple game tree search builds up a tree of player/opponent moves from the current game state.
        For each move, the utility of the game state is estimated by using the flood fill heuristic (ratio
        between flood fill areas). The game tree is expanded ply-by-ply, in order of descending estimated
        utility (for the player rounds), or ascending estimated utility (for the opponent rounds). This is
        done so that the search can be terminated after a set time, and the explored leaves backed up.
        """

        current_player_pos = tron.Position(world.pos_player.to_tuple())
        current_opponent_pos = tron.Position(world.pos_opponent.to_tuple())

        root = State()
        frontier = {root}
        leaves = set()

        start_time = time.time()

        # assert isinstance(world_copy, tron.World)

        # Start evaluating the game tree ply by ply. Stop when time runs out, or when one of the players
        # has no valid move left.
        while (time.time() - start_time < self.time_limit) and (len(frontier) > 0):
            # Evaluate the next ply. We'll sprinkle time limit checks generously to make sure that slow loops
            # don't run for too long.

            # Start with an empty frontier. As we iterate through the leaves, the new frontier will be built
            # up, and will become the set of leaves for the next ply.
            new_frontier = set()

            for state in frontier:
                if (time.time() - start_time >= self.time_limit):
                    break

                opponent_move = (state.depth % 2 == 0)

                # Firstly build up the frontier for this game state: the list of valid moves that can be performed
                # from this state. These will become new states with the current state as parent.

                # This is hugely inefficient: the entire world object gets deep-copied, and over plies, these
                # game states are recalculated. It's probably a good idea to cache game states in some way, by
                # letting the state graph cache copies of the rendered game world. By using a deque of states that
                # have cache copies, the cache can be rotated to only use a fixed amount of memory.
                # TODO: Implement state caching

                world_copy = state.render(world)

                # At the point when the world is first rendered (i.e. just before expanding the frontier) is a good
                # time to calculate the current state's utility. The utility is a tuple of the form:
                #     (player_flood_liberties, opponent_flood_liberties)
                state.utility = self.utility(world_copy.prospect(opponent = opponent_move))
                if state.parent != None:
                    # If we're not at the root node right now, reset the parent's utility to None (it was just
                    # a heuristic estimate anyway). This will be useful once we start backpropagating utilities
                    # from the leaves, because we can then use None to represent a node which has not yet received
                    # a backpropagated utility.
                    state.parent.utility = None

                # We now have a leaf state with calculated utility. Add this to our set of evaluated leaves before
                # we let it spawn its own leaves.
                leaves.add(state)

                # This leaf's parent may still be in the list of leaves, but it's been superceded now; remove it.
                leaves.discard(state.parent)

                valid_moves = world_copy.valid_moves(opponent = opponent_move)
                for move in valid_moves:
                    new_state = State(state, move)
                    new_frontier.add(new_state)

            frontier = new_frontier

        # After we've explored the entire game tree (or run out of time), we back up utility from the leaves to
        # the root using the minimax criterion. We iterate through the leaves, and compare each leaf's utility to that
        # of its parent. If it's None, lower (max case = player move) or higher (min case = opponent move), the leaf's
        # utility is backed up to the parent.

        while len(leaves) > 0:
            new_leaves = set()
            for state in leaves:
                if state.parent != None:
                    # When the parent's depth is even (i.e. this state's depth is odd), we're considering the utility of
                    # the player's move (the parent would choose the successive state with the highest utility). When the
                    # parent's depth is odd (this state's depth is even), the opponent's optimal choice would let the
                    # lowest utility be backed up.
                    if state.depth % 2 == 1:
                        if (state.parent.utility == None) or (state.parent.utility < state.utility):
                            state.parent.utility = state.utility
                            state.parent.next_move = state.last_move
                            new_leaves.add(state.parent)
                    else:
                        if (state.parent.utility == None) or (state.parent.utility > state.utility):
                            state.parent.utility = state.utility
                            state.parent.next_move = state.last_move
                            new_leaves.add(state.parent)
            leaves = new_leaves

        print("Player moves to (%d,%d)" % root.next_move)
        world.set_state(root.next_move, PLAYER)
        world.set_state(current_player_pos, PLAYER_WALL)
