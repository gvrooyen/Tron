#ifndef MINMAXFLOOD_I_H
#define MINMAXFLOOD_I_H

#include <vector>
#include <utility>
#include "rcptr.h"
#include "constants.h"

using namespace std;

class Utility {
  public:
	static const int UNKNOWN = 0;
	static const int ESTIMATED = 1;
	static const int TRUE = 2;
	int value;
	int state;
	Utility(int _state = UNKNOWN, int _value = 0) { state = _state; value = _value;} ;
};

class State {
	Utility utility;
	RCPtr<State> parent;
	Move last_move;
	Move next_move;
	int depth;
  public:
    State();
    State(RCPtr<State> _parent, Move _last_move);
    // TODO: RCPtr<World> render(RCPtr<World> world);
};

#endif
