#include "minmaxflood_i.h"
#include <limits>

State::State() {
	utility = numeric_limits<float>::infinity();
	depth = 0;
}

State::State(RCPtr<State> _parent, Move _last_move) {
	parent = _parent;
	last_move = _last_move;
	if (parent.objPtr() == 0) {
		depth = 0;
	} else {
		depth = parent->depth + 1;
	}
}
