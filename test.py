__author__ = 'gvrooyen'

import unittest
import tron
import judge
from constants import *

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
        self.assertEqual(P.south(), (0,1))
        self.assertEqual(P.east(), (1,0))
        self.assertEqual(P.west(), (29,0))
        self.assertTrue(P.at_north_pole())
        self.assertFalse(P.at_south_pole())
        self.assertTrue(P.is_adjacent((29,0)))

        P = tron.Position((29,29))
        self.assertEqual(P.north(), (29,28))
        self.assertEqual(P.south(), None)
        self.assertEqual(P.east(), (0,29))
        self.assertEqual(P.west(), (28,29))
        self.assertTrue(P.at_south_pole())
        self.assertFalse(P.at_north_pole())
        self.assertTrue(P.is_adjacent((0,29)))


class TestStateFile(unittest.TestCase):
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

