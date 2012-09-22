#ifndef TRON_H
#define TRON_H

#include "constants.h"
#include "rcptr.h"

using namespace std;

class Position {
	pair<int,int> pos;
  public:
	Position(pair<int,int> _pos);
	Position(int x, int y);
	inline bool at_north_pole() { return pos.second == 0; };
	inline bool at_south_pole() { return pos.second == world_size - 1; };
	inline bool at_pole() { return at_north_pole() or at_south_pole(); };
	inline RCPtr<Position> north();
	inline RCPtr<Position> south();
	inline RCPtr<Position> east();
	inline RCPtr<Position> west();
	inline void go_north();
	inline void go_south();
	inline void go_east();
	inline void go_west();
	bool is_adjacent(RCPtr<Position> _pos);
	inline pair<int,int> to_tuple();
};



#endif

