__author__ = 'gvrooyen'

EMPTY = None
PLAYER = 0
OPPONENT = 1
PLAYER_WALL = 2
OPPONENT_WALL = 3

SOUTH = (0, -1)
NORTH = (0, +1)
EAST  = (+1, 0)
WEST  = (-1, 0)

STATE_DICT = {
    "clear": EMPTY,
    "you": PLAYER,
    "opponent": OPPONENT,
    "yourwall": PLAYER_WALL,
    "opponentwall": OPPONENT_WALL
}
