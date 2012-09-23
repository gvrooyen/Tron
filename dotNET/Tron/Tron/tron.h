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
	Position pos_player;
	Position pos_opponent;
  public:
	World(string state_file = "");
	inline int state(Position pos);
	inline int state(RCPtr<Position> pos);
	inline int state(int x, int y);
	inline void set_state(Position pos, int state);
	void set_player(Position pos, bool opponent = false);
	void set_opponent(Position pos) { set_player(pos, true); };
	void move_player(Position pos, bool opponent = false);
	void move_opponent(Position pos) { move_player(pos, false); };
	void move_blue(Position pos) { move_player(pos); }
	void move_red(Position pos) { move_player(pos, true); }
	int liberties(bool opponent = false);
	set< RCPtr<Position> > empty_space();
	int count_empty_space();
	set< RCPtr<Move> > valid_moves(bool opponent = false);
	pair<int,int> prospect(bool opponent = false, int plies = 30);
	void save(string filename, int player = BLUE);
	Position get_pos_player() { return pos_player; }
	Position get_pos_opponent() { return pos_opponent; }
};

namespace tron {
	class Strategy {
	  protected:
		float time_limit;
	  public:
  		Strategy();
  		void move(RCPtr<World> world);
	};
}

#endif

