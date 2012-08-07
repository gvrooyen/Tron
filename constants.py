__author__ = 'gvrooyen'

# "player" and "blue" are equivalent, as are "opponent" and "red". The different names exist so that games
# strategy code (policies) can refer to the player and the opponent, while adjudicating code (that needs to take
# both players' interests into account) can refer to the blue and the red player.

EMPTY = None
PLAYER = 0
BLUE = 0
OPPONENT = 1
RED = 1
PLAYER_WALL = 2
BLUE_WALL = 2
OPPONENT_WALL = 3
RED_WALL = 3

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
