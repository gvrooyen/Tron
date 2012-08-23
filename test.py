__author__ = 'gvrooyen'

import unittest
import tron
import judge
import shutil
from constants import *
import random
import viz

class TestTron(unittest.TestCase):
    def test_movement(self):
        P = tron.Position((10,10))
        self.assertEqual(P.north(), (10,9))
        self.assertEqual(P.south(), (10,11))
        self.assertEqual(P.east(), (11,10))
        self.assertEqual(P.west(), (9,10))
        self.assertTrue(P.is_adjacent((10,11)))
        self.assertFalse(P.is_adjacent((9,9)))
        self.assertFalse(P.is_adjacent((20,20)))

        P = tron.Position((0,0))
        self.assertEqual(P.north(), None)
        self.assertEqual(P.south(), None)
        self.assertEqual(P.east(), (1,0))
        self.assertEqual(P.west(), (29,0))
        self.assertTrue(P.at_north_pole())
        self.assertFalse(P.at_south_pole())
        self.assertFalse(P.is_adjacent((29,0)))  # (29,0) and (0,0) are the same point (the North Pole)
        self.assertTrue(P.is_adjacent((17,1)))   # All points on the arctic circle are adjacent to the North Pole

        P = tron.Position((29,29))
        self.assertEqual(P.north(), None)
        self.assertEqual(P.south(), None)
        self.assertEqual(P.east(), (0,29))
        self.assertEqual(P.west(), (28,29))
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
        random.seed(25)
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

        # print J.trace_red[0:15]
        viz.plot_trace(J.trace_blue,J.trace_red)

# TODO: Note that "Each player will start on exactly opposite sides of the sphere."
#       Starting points for each player will be on exactly opposing points of the same Y axial, where Y > 0 and Y < 29,
#       i.e excluding the poles. This will neither advantage nor disadvantage any specific player. To clarify: If you
#       start at position (X, Y) your opponent will start at position ( (X + 15) % 30, Y).
