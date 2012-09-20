#ifndef MINMAXFLOOD_I_H
#define MINMAXFLOOD_I_H

#include <vector>
#include <utility>
#include "rcptr.hpp"
#include "constants.h"

using namespace std;

class State {
	vector<Move> valid_moves;
	float utility;
	RCPtr < State > parent;
	Move last_move;
	Move next_move;
	int depth;
  public:
    State();
    State(RCPtr<State> _parent, Move _last_move);
};

#endif
