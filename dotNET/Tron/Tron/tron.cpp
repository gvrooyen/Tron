#include "tron.h"
#include <assert.h>

inline Position::Position(pair<int,int> _pos) {
	pos = _pos;
	assert(pos.first >= 0);
	assert(pos.second < world_size);
}

inline Position::Position(int x, int y) {
	pos = pair<int,int>(x,y);
	assert(pos.first >= 0);
	assert(pos.second < world_size);
}

inline RCPtr<Position> Position::north() {
	// Returns the coordinates north of the current position, or (-1,-1) if it's at one of the poles.
	if (at_pole())
		return RCPtr<Position> ( new Position(-1,-1) );
	else
		return RCPtr<Position> ( new Position(pos.first, pos.second-1) );
}
	
inline RCPtr<Position> Position::south() {
	// Returns the coordinates south of the current position, or (-1,-1) if it's at one of the poles.
	if (at_pole())
		return RCPtr<Position> ( new Position(-1,-1) );
	else
		return RCPtr<Position> ( new Position(pos.first, pos.second+1) );
}

inline RCPtr<Position> Position::east() {
	if (pos.first == world_size - 1)
		return RCPtr<Position> ( new Position(0, pos.second) );
	else
		return RCPtr<Position> ( new Position(pos.first+1, pos.second) );
}

inline RCPtr<Position> Position::west() {
	if (pos.first == 0)
		return RCPtr<Position> ( new Position(world_size-1, pos.second) );
	else
		return RCPtr<Position> ( new Position(pos.first-1, pos.second) );	
}

inline void Position::go_north() {
	// TODO: This is inefficient; refactor so that north(), etc. can generate pairs directly
	RCPtr<Position> new_pos = north();
	pair<int,int> t_new_pos = new_pos->to_tuple();
	if (t_new_pos.first > -1)
		pos = t_new_pos;
	else
		assert(false);
}

inline void Position::go_south() {
	RCPtr<Position> new_pos = south();
	pair<int,int> t_new_pos = new_pos->to_tuple();
	if (t_new_pos.first > -1)
		pos = t_new_pos;
	else
		assert(false);
}

inline void Position::go_east() {
	RCPtr<Position> new_pos = east();
	pos = new_pos->to_tuple();
}

inline void Position::go_west() {
	RCPtr<Position> new_pos = west();
	pos = new_pos->to_tuple();
}

bool Position::is_adjacent(RCPtr<Position> _pos) {
	assert(_pos->to_tuple().first >= 0);
	assert(_pos->to_tuple().second < world_size);
	if (at_south_pole())
		return _pos->to_tuple().second == world_size - 2;
	else if (at_north_pole())
		return _pos->to_tuple().second == 1;
	else if (_pos->at_south_pole())
		return pos.second == world_size - 2;
	else if (_pos->at_north_pole())
		return pos.second == 1;
	else
		return ( (west()->to_tuple() == _pos->to_tuple()) or
		         (east()->to_tuple() == _pos->to_tuple()) or
		         (north()->to_tuple() == _pos->to_tuple()) or
		         (south()->to_tuple() == _pos->to_tuple()) );
}

inline pair<int,int> Position::to_tuple() {
	if (at_north_pole())
		return pair<int,int>(0,0);
	else if (at_south_pole())
		return pair<int,int>(0,world_size-1);
	else
		return pos;
}
