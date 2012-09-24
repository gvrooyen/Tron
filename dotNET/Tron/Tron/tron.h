#ifndef TRON_H
#define TRON_H

#include "constants.h"
#include "rcptr.h"
#include <string>
#include <set>

using namespace std;

class Position {
	// TODO: It could be very efficient to implement this as a singleton class
	pair<int,int> pos;
	void normalise() { if ((pos.second == 0) || (pos.second == world_size-1)) pos.first = 0; };
  public:
    Position();
	Position(pair<int,int> _pos);
	Position(int x, int y);
	Position(RCPtr<Position> source_position);
	bool at_north_pole() { return pos.second == 0; };
	bool at_south_pole() { return pos.second == world_size - 1; };
	bool at_pole() { return at_north_pole() || at_south_pole(); };
	inline RCPtr<Position> north();
	inline RCPtr<Position> south();
	inline RCPtr<Position> east();
	inline RCPtr<Position> west();
	inline void go_north(int lon = 0);
	inline void go_south(int lon = 0);
	inline void go_east();
	inline void go_west();
	bool is_adjacent(RCPtr<Position> _pos);
	inline pair<int,int> to_tuple();
	int x() { return pos.first; }
	int y() { return pos.second; }
};

class World {
	int world[world_size][world_size];
	RCPtr<Position> pos_player;
	RCPtr<Position> pos_opponent;
  public:
	World(string state_file = "");
	World(RCPtr<World> source_world);
	inline int state(RCPtr<Position> pos);
	inline int state(int x, int y);
	inline void set_state(RCPtr<Position> pos, int state);
	void set_player(RCPtr<Position> pos, bool opponent = false);
	void set_opponent(RCPtr<Position> pos) { set_player(pos, true); };
	void move_player(RCPtr<Position> pos, bool opponent = false);
	void move_opponent(RCPtr<Position> pos) { move_player(pos, false); };
	void move_blue(RCPtr<Position> pos) { move_player(pos); }
	void move_red(RCPtr<Position> pos) { move_player(pos, true); }
	int liberties(bool opponent = false);
	RCPtr< set<Move> > empty_space();
	int count_empty_space();
	RCPtr< set<Move> > valid_moves(bool opponent = false);
	pair<int,int> prospect(bool opponent = false, int plies = 30);
	void save(string filename, int player = BLUE);
	RCPtr<Position> get_pos_player() { return pos_player; }
	RCPtr<Position> get_pos_opponent() { return pos_opponent; }
};

namespace tron {
	class Strategy {
	  protected:
		float time_limit;
	  public:
  		Strategy();
  		virtual void move(RCPtr<World> world);
	};
}

#endif

