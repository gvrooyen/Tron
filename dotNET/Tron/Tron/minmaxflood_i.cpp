#include "minmaxflood_i.h"
#include <limits>

inline State::State() {
	utility = Utility();
	depth = 0;
}

inline State::State(RCPtr<State> _parent, Move _last_move) {
	utility = numeric_limits<float>::infinity();
	parent = _parent;
	last_move = _last_move;
	if (parent.objPtr() == 0) {
		depth = 0;
	} else {
		depth = parent->depth + 1;
	}
}
