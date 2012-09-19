__author__ = 'gvrooyen'

import unittest
import tron
import judge
import shutil
from constants import *
import random
import time
import viz
import minmaxflood_i

MAX_MOVE_TIME = 4.9

class TestTron(unittest.TestCase):
    def test_movement(self):
        P = tron.Position((10,10))
        self.assertEqual(P.north().to_tuple(), (10,9))
        self.assertEqual(P.south().to_tuple(), (10,11))
        self.assertEqual(P.east().to_tuple(), (11,10))
        self.assertEqual(P.west().to_tuple(), (9,10))
        self.assertTrue(P.is_adjacent((10,11)))
        self.assertFalse(P.is_adjacent((9,9)))
        self.assertFalse(P.is_adjacent((20,20)))

        P = tron.Position((0,0))
        self.assertEqual(P.north(), None)
        self.assertEqual(P.south(), None)
        self.assertEqual(P.east().to_tuple(), (0,0))
        self.assertEqual(P.west().to_tuple(), (0,0))
        self.assertTrue(P.at_north_pole())
        self.assertFalse(P.at_south_pole())
        self.assertFalse(P.is_adjacent((29,0)))  # (29,0) and (0,0) are the same point (the North Pole)
        self.assertTrue(P.is_adjacent((17,1)))   # All points on the arctic circle are adjacent to the North Pole

        P = tron.Position((29,29))
        self.assertEqual(P.north(), None)
        self.assertEqual(P.south(), None)
        self.assertEqual(P.east().to_tuple(), (0,29))
        self.assertEqual(P.west().to_tuple(), (0,29))
        self.assertTrue(P.at_south_pole())
        self.assertFalse(P.at_north_pole())
        self.assertFalse(P.is_adjacent((0,29)))  # (29,29) and (0,29) are the same point (the South Pole)
        self.assertTrue(P.is_adjacent((19,28)))  # All points on the antarctic circle are adjacent to the South Pole


class TestStateFile(unittest.TestCase):
    def test_poles(self):
        """
        Verify that behaviour at the poles are as expected. All points in the (ant)arctic circles should be
        treated as adjacent, and (x,0) should be the same point for all x, and likewise for (x,29).
        """
        blue_red = (((15,1),(15,28)),
                    ((25,0),(25,29)), # Both players step into the poles. The system should handle the adjacency
                                      #   of the unusual coordinates correctly.
                    ((5,1), (5,28)),  # Both players step out of the poles at completely different longitudes. Again,
                                      #   the system should handle the adjacency correctly despite the unusual
                                      #   coordinates.
                    ((5,0), (5,29))   # This should generate an exception, since both players have already visited
                                      #   the poles.
                   )

        J = judge.Judge(pos_blue=blue_red[0][0], pos_red=blue_red[0][1])
        J.world.save('game.state', player=BLUE)
        self.assertEqual(J.adjudicate('game.state', new_move=None), None)
        winner = None
        move = 0
        for (blue,red) in blue_red[1:]:
            move += 1
            for pos in (blue, red):
                player = BLUE if pos == blue else RED
                J.world.save('game.state', player=player)
                P = tron.World('game.state')
                P.move_player(pos)
                P.save('game.state')
                if move == 3:
                    self.assertRaises(judge.StateFileException, J.adjudicate, 'game.state', new_move=player)
                else:
                    J.adjudicate('game.state', new_move=player)


    def test_adjudication(self):

        blue_red = (((10,10),(9,9)),
                    ((11,10),(10,9)),
                    ((12,10),(11,9)),
                    ((13,10),(12,9)),
                    ((13,11),(13,9)),
                    ((12,11),(14,9)),
                    ((11,11),(14,10)),
                    ((10,11),(14,11)),
                    ((10,12),(14,12)),
                    ((11,12),(14,13)),
                    ((12,12),(14,14)),
                    ((13,12),(14,15)),
                    ((13,13),(13,15)),
                    ((12,13),(12,15)),
                    ((11,13),(11,15)),
                    ((10,13),(10,15)),
                    ((10,14),(9,15)),
                    ((11,14),(9,14)),
                    ((12,14),(9,13)),
                    ((13,14),(9,12))
            )

        J = judge.Judge(pos_blue=blue_red[0][0], pos_red=blue_red[0][1])
        J.world.save('game.state', player=BLUE)
        self.assertEqual(J.adjudicate('game.state', new_move=None), None)
        winner = None
        for (blue,red) in blue_red[1:]:
            for pos in (blue, red):
                player = BLUE if pos == blue else RED
                J.world.save('game.state', player=player)
                P = tron.World('game.state')
                P.move_player(pos)
                P.save('game.state')
                winner = J.adjudicate('game.state', new_move=player)
                if winner:
                    break
            if winner:
                break
        else:
            self.fail("Winning condition not detected")

        self.assertEqual(winner, RED)

    def test_basic_strategy(self):
        for seed in xrange(100,110):
            random.seed(seed)
            J = judge.Judge()
            J.world.save('game.state', player=BLUE)
            self.assertEqual(J.adjudicate('game.state', new_move=None), None)
            winner = None
            player = BLUE
            while (winner == None):
                player = RED if player == BLUE else BLUE
                shutil.copyfile('game.state', 'game.state.bak')
                J.world.save('game.state', player=player)
                W = tron.World('game.state')
                S = tron.Strategy()
                S.move(W)
                shutil.copyfile('game.state', 'game.state.bak')
                W.save('game.state')
                winner = J.adjudicate('game.state', new_move=player)

            self.assertNotEqual(winner, None)

#            world_map = viz.WorldMap()
#            world_map.plot_trace(J.trace_blue,J.trace_red)
#            world_map.plot_points(J.world.empty_space(),'g')
#            world_map.show()

    def test_prospect(self):
        random.seed(1006)
        J = judge.Judge()
        J.world.save('game.state', player=BLUE)
        self.assertEqual(J.adjudicate('game.state', new_move=None), None)
        winner = None
        player = BLUE

        for turn in xrange(0,30):
            player = RED if player == BLUE else BLUE
            shutil.copyfile('game.state', 'game.state.bak')
            J.world.save('game.state', player=player)
            W = tron.World('game.state')
            S = tron.Strategy()
            S.move(W)
            shutil.copyfile('game.state', 'game.state.bak')
            W.save('game.state')
            winner = J.adjudicate('game.state', new_move=player)
            if winner:
                break


        (player_domain, opponent_domain) = J.world.prospect(turns=40)
#        world_map = viz.WorldMap()
#        world_map.plot_trace(J.trace_blue,J.trace_red)
#        world_map.plot_points(player_domain, 'c')
#        world_map.plot_points(opponent_domain, 'm')
#        world_map.show()

    def test_minmaxflood_i(self):
        for seed in xrange(50,100):
            random.seed(seed)
            # TODO: The basic strategy test loop can be factored out into a separate module
            J = judge.Judge()
            J.world.save('game.state', player=BLUE)
            self.assertEqual(J.world.pos_opponent[1],J.world.pos_player[1])    # Same axial
            self.assertEqual(abs(J.world.pos_opponent[0] - J.world.pos_player[0]), 15)    # Opposite sides
            self.assertEqual(J.adjudicate('game.state', new_move=None), None)
            print("Blue starts at (%d,%d)" % J.world.pos_player)
            print("Red starts at (%d,%d)" % J.world.pos_opponent)
            winner = None
            player = RED
            while (winner == None):
                if player == BLUE:
                    player = RED
                    # Red plays with the naive random-move strategy
                    S = tron.Strategy()
                else:
                    player = BLUE
                    # Blue plays with the strategy under test
                    S = minmaxflood_i.Strategy()
                    S.time_limit = 20.0
                shutil.copyfile('game.state', 'game.state.bak')
                J.world.save('game.state', player=player)
                W = tron.World('game.state')
                start_time = time.time()
                S.move(W)
                shutil.copyfile('game.state', 'game.state.bak')
                W.save('game.state')
                # self.assertLess(time.time() - start_time, MAX_MOVE_TIME)
                winner = J.adjudicate('game.state', new_move=player)

            self.assertNotEqual(winner, None)

            if winner == BLUE:
                result = "Blue wins!"
            else:
                result = "Red wins!"

            world_map = viz.WorldMap()
            world_map.plot_trace(J.trace_blue,J.trace_red)
            # world_map.plot_points(J.world.empty_space(),'g')
            world_map.save(result, str(seed)+'.png')




# TODO: Note that "Each player will start on exactly opposite sides of the sphere."
#       Starting points for each player will be on exactly opposing points of the same Y axial, where Y > 0 and Y < 29,
#       i.e excluding the poles. This will neither advantage nor disadvantage any specific player. To clarify: If you
#       start at position (X, Y) your opponent will start at position ( (X + 15) % 30, Y).
