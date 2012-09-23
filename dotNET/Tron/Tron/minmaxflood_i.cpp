#include "minmaxflood_i.h"
#include <limits>

inline State::State() {
	utility = Utility();
	depth = 0;
}

inline State::State(RCPtr<State> _parent, Move _last_move) {
	utility = Utility();
	parent = _parent;
	last_move = _last_move;
	if (parent.objPtr() == 0) {
		depth = 0;
	} else {
		depth = parent->depth + 1;
	}
}

RCPtr<World> State::render(RCPtr<World> world) {
	RCPtr<World> result = RCPtr<World> ( new World() );
	State* s = this;
	bool player_leaf = true;
	bool opponent_leaf = true;

	while (s->has_parent()) {
		Position p = Position(s->last_move);
		if (s->depth % 2 == 1) {
			if (opponent_leaf) {
				result->set_state(p, OPPONENT);
				result->set_opponent(p);
				opponent_leaf = false;
			} else {
				result->set_state(p, OPPONENT_WALL);
			}
		} else {
			if (player_leaf) {
				result->set_state(p, PLAYER);
				result->set_player(p);
				player_leaf = false;
			} else {
				result->set_state(p, PLAYER_WALL);
			}
		}
		s = s->parent.objPtr();
	}

	return result;
}

float minmaxflood_i::Strategy::calc_utility(pair<int,int> prospect) {
	int player = prospect.first - 1;
	int opponent = prospect.second - 1;

	if (opponent == 0) {
		if (player == 0) {
			return 1.0;
		} else {
			return numeric_limits<float>::infinity();
		}
	} else if (player == 0) {
		return 0.0;
	} else {
		return ((float)player) / ((float)opponent);
	}
}
