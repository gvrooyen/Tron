#include "constants.h"

int State(string description) {
	if (description == "Clear") return EMPTY;
	if (description == "You") return PLAYER;
	if (description == "Opponent") return OPPONENT;
	if (description == "YourWall") return PLAYER_WALL;
	if (description == "OpponentWall") return OPPONENT_WALL;
	return EMPTY;
}

