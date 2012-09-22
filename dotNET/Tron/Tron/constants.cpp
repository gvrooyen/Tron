#include "constants.h"
#include <assert.h>

int state_value(string description) {
	if (description == "Clear") return EMPTY;
	if (description == "You") return PLAYER;
	if (description == "Opponent") return OPPONENT;
	if (description == "YourWall") return PLAYER_WALL;
	if (description == "OpponentWall") return OPPONENT_WALL;
	assert(false);
}

string state_string(int value) {
	switch (value) {
		case EMPTY: return "Clear";
		case PLAYER: return "You";
		case OPPONENT: return "Opponent";
		case PLAYER_WALL: return "YourWall";
		case OPPONENT_WALL: return "OpponentWall";
	}
}
