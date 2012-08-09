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
        J = judge.Judge(pos_red=(10,10), pos_blue=(20,20))
        J.world.save('blue.state', player=BLUE)
        self.assertEqual(J.adjudicate('blue.state', new_move=False), None)


if __name__ == '__main__':
    unittest.main()
