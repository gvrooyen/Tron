#ifndef MINMAXFLOOD_I_H
#define MINMAXFLOOD_I_H

#include <vector>
#include <utility>
#include "rcptr.h"
#include "constants.h"
#include "tron.h"

class Utility {
  public:
	static const int UNKNOWN = 0;
	static const int ESTIMATED = 1;
	static const int TRUE = 2;
	float value;
	int state;
	Utility(int _state = UNKNOWN, float _value = -1.0) { state = _state; value = _value;} ;
};

class State {
	static int key_idx;
  public:
	int key;
	Utility utility;
	RCPtr<State> parent;
	Move last_move;
	Move next_move;
	int depth;

    inline State();
    inline State(RCPtr<State> _parent, Move _last_move);
    RCPtr<World> render(RCPtr<World> world);
	bool has_parent() { return parent.objPtr() != 0; };
};

namespace minmaxflood_i {
	class Strategy: public tron::Strategy {
		float calc_utility(pair<int,int> prospect);
	  public:
		virtual void move(RCPtr<World> world);
	};
}

#endif
