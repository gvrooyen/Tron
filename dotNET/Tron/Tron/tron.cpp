#include "tron.h"
#include "util.h"
#include <assert.h>
#include <string>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <algorithm>

using namespace std;

Position::Position() {
	pos.first = -1;
	pos.second = -1;
}

Position::Position(pair<int,int> _pos) {
	pos = _pos;
	normalise();
	assert(pos.first >= -1);
	assert(pos.second < world_size);
}

inline Position::Position(int x, int y) {
	pos = pair<int,int>(x,y);
	normalise();
	assert(pos.first >= -1);
	assert(pos.second < world_size);
}

inline RCPtr<Position> Position::north() {
	// Returns the coordinates north of the current position, or (-1,-1) if it's at one of the poles.
	if (at_pole()) {
		return RCPtr<Position> ( new Position(-1,-1) );
	} else {
		return RCPtr<Position> ( new Position(pos.first, pos.second-1) );
	}
}
	
inline RCPtr<Position> Position::south() {
	// Returns the coordinates south of the current position, or (-1,-1) if it's at one of the poles.
	if (at_pole()) {
		return RCPtr<Position> ( new Position(-1,-1) );
	} else {
		return RCPtr<Position> ( new Position(pos.first, pos.second+1) );
	}
}

inline RCPtr<Position> Position::east() {
	if (pos.first == world_size - 1) {
		return RCPtr<Position> ( new Position(0, pos.second) );
	} else {
		return RCPtr<Position> ( new Position(pos.first+1, pos.second) );
	}
}

inline RCPtr<Position> Position::west() {
	if (pos.first == 0) {
		return RCPtr<Position> ( new Position(world_size-1, pos.second) );
	} else {
		return RCPtr<Position> ( new Position(pos.first-1, pos.second) );	
	}
}

inline void Position::go_north(int lon) {
	// TODO: This is inefficient; refactor so that north(), etc. can generate pairs directly
	RCPtr<Position> new_pos = north();
	pair<int,int> t_new_pos = new_pos->to_tuple();
	if (t_new_pos.first > -1) {
		pos = t_new_pos;
	} else {
		if (at_south_pole()) pos = pair<int,int> (lon, world_size-2);
		else assert(false);
	}
}

inline void Position::go_south(int lon) {
	RCPtr<Position> new_pos = south();
	pair<int,int> t_new_pos = new_pos->to_tuple();
	if (t_new_pos.first > -1) {
		pos = t_new_pos;
	} else {
		if (at_north_pole()) pos = pair<int,int> (lon, 1);
		else assert(false);
	}
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
	if (at_south_pole()) {
		return _pos->to_tuple().second == world_size - 2;
	} else if (at_north_pole()) {
		return _pos->to_tuple().second == 1;
	} else if (_pos->at_south_pole()) {
		return pos.second == world_size - 2;
	} else if (_pos->at_north_pole()) {
		return pos.second == 1;
	} else {
		return ( (west()->to_tuple() == _pos->to_tuple()) ||
		         (east()->to_tuple() == _pos->to_tuple()) ||
		         (north()->to_tuple() == _pos->to_tuple()) ||
		         (south()->to_tuple() == _pos->to_tuple()) );
	}
}

inline pair<int,int> Position::to_tuple() {
	if (at_north_pole()) {
		return pair<int,int>(0,0);
	} else if (at_south_pole()) {
		return pair<int,int>(0,world_size-1);
	} else {
		return pos;
	}
}

World::World(string state_file) {
	int line_num = 0;
	for (int x = 0; x < world_size; x++)
		for (int y = 0; y < world_size; y++)
		  world[x][y] = EMPTY;
	if (state_file != "") {
		string line;
		ifstream file (state_file.c_str());
		if (file.is_open()) {
			while ( file.good() ) {
				vector<string> tokens;
				int x, y;

				getline(file, line);
				line_num++;
				tokens = split(line, ' ');

				if (tokens.size() > 3)
					cerr << "Extra tokens on line " << line_num << " of " << state_file << " ignored." << endl;
				if (tokens.size() >= 3) {
					istringstream (tokens[0]) >> x;
					istringstream (tokens[1]) >> y;
					assert(x >= 0);
					assert(x < world_size);
					assert(y >= 0);
					assert(y < world_size);
					world[x][y] = state_value(tokens[2]);
					if (world[x][y] == PLAYER) pos_player = Position(x,y);
					else if (world[x][y] == OPPONENT) pos_opponent = Position(x,y);
				} else if (tokens.size() == 0) {
					if (line_num <= world_size*world_size)
						cerr << "Empty line number " << line_num << " of " << state_file << " skipped." << endl;
				} else {
					cerr << "Malformed data at line number " << line_num << " of " << state_file << "." << endl;
				}
			}
		}
		else cerr << "Unable to read specified state file: " << state_file << endl;
	} else {
		pos_player = Position(-1,-1);
		pos_opponent = Position(-1,-1);
	}
}

inline int World::state(Position pos) {
	if (pos.x() == -1) return EMPTY;
	return world[pos.x()][pos.y()];
}

inline int World::state(RCPtr<Position> pos) {
	if (pos->x() == -1) return EMPTY;
	return world[pos->x()][pos->y()];	
}

inline int World::state(int x, int y) {
	if (x == -1) return EMPTY;
	return world[x][y];
}

inline void World::set_state(Position pos, int state) {
	int x = pos.x();
	int y = pos.y();
	if (x == -1) {
		// pass
	} else if (y == 0) {
		for (int i = 0; i < world_size; i++)
			world[i][0] = state;
	} else if (y == world_size-1) {
		for (int i = 0; i < world_size; i++)
			world[i][world_size-1] = state;
	} else world[x][y] = state;
}

void World::set_player(Position pos, bool opponent) {
	if (opponent) {
		// set_state(pos_opponent, EMPTY);
		set_state(pos, OPPONENT);
		pos_opponent = pos;
	} else {
		// set_state(pos_player, EMPTY);
		set_state(pos, PLAYER);
		pos_player = pos;
	}
}

void World::move_player(Position pos, bool opponent) {
	if (opponent) {
		set_state(pos_opponent, OPPONENT_WALL);
		set_state(pos, OPPONENT);
		pos_opponent = pos;
	} else {
		set_state(pos_player, PLAYER_WALL);
		set_state(pos, PLAYER);
		pos_player = pos;
	}
}

int World::liberties(bool opponent) {
	Position pos;
	int result = 0;
	
	if (opponent) pos = pos_opponent;
	else pos = pos_player;
	
	if (pos.at_south_pole()) {
		for (int i = 0; i < world_size; i++)
			if (state(i, world_size-2) == EMPTY) result++;
	} else if (pos.at_north_pole()) {
		for (int i = 0; i < world_size; i++)
			if (state(i, 1) == EMPTY) result++;
	} else {
		if (state(pos.north()) == EMPTY) result++;
		if (state(pos.south()) == EMPTY) result++;
		if (state(pos.east()) == EMPTY) result++;
		if (state(pos.west()) == EMPTY) result++;
	}
	
	return result;
}

set< RCPtr<Position> > World::empty_space() {
	set< RCPtr<Position> > result;
	
	if (state(0,0) == EMPTY) result.insert( RCPtr<Position> (new Position(0,0)) );
	if (state(0,world_size-1) == EMPTY) result.insert( RCPtr<Position> (new Position(0,world_size-1)) );
	
	for (int x = 0; x < world_size; x++)
		for (int y = 0; y < world_size-1; y++)
			if (state(x,y) == EMPTY) result.insert( RCPtr<Position> (new Position(x,y)) );
	
	return result;
}

int World::count_empty_space() {
	int result = 0;
	
	if (state(0,0) == EMPTY) result++;
	if (state(0,world_size-1) == EMPTY) result++;
	
	for (int x = 0; x < world_size; x++)
		for (int y = 0; y < world_size-1; y++)
			if (state(x,y) == EMPTY) result++;
	
	return result;	
}

set< RCPtr<Move> > World::valid_moves(bool opponent) {
	Position pos;
	RCPtr<Move> new_move;
	
	set< RCPtr<Move> > result;
	set< RCPtr<Position> > adjacent;
	set< RCPtr<Position> > unclaimed = empty_space();

	if (opponent) pos = pos_player;
	else pos = pos_opponent;
	
	if (pos.at_north_pole()) {
		for (int x = 0; x < world_size; x++)
			adjacent.insert( RCPtr<Position> (new Position(x,1)) );
	} else if (pos.at_south_pole()) {
		for (int x = 0; x < world_size; x++)
			adjacent.insert( RCPtr<Position> (new Position(x,world_size-2)) );
	} else {
		adjacent.insert( pos.north() );
		adjacent.insert( pos.south() );
		adjacent.insert( pos.east() );
		adjacent.insert( pos.west() );
	}
	
	for (set< RCPtr<Position> >::iterator a = adjacent.begin(); a != adjacent.end(); a++)
		if (unclaimed.find(*a) != unclaimed.end())
			new_move = RCPtr<Move> ( new Move( (*a)->x(), (*a)->y() ) );
			result.insert(new_move);
	
	return result;	
}

pair<int,int> World::prospect(bool opponent, int plies) {
	set< RCPtr<Position> > unclaimed = empty_space();
	set< RCPtr<Position> > player_frontier;
	set< RCPtr<Position> > opponent_frontier;
	set< RCPtr<Position> > player_domain;
	set< RCPtr<Position> > opponent_domain;
	
	player_frontier.insert( RCPtr<Position> ( new Position(pos_player) ) );
	opponent_frontier.insert( RCPtr<Position> ( new Position(pos_opponent) ) );
	
	RCPtr< set< RCPtr<Position> > > frontier;
	RCPtr< set< RCPtr<Position> > > domain;
	RCPtr< set< RCPtr<Position> > > new_frontier;
	
	int ply_count = 0;
	
	while (ply_count < plies) {
		new_frontier->clear();
		ply_count++;
		
		if (opponent) {
			frontier = RCPtr< set< RCPtr<Position> > > (&opponent_frontier);
			domain = RCPtr< set< RCPtr<Position> > > (&opponent_domain);
		} else {
			frontier = RCPtr< set< RCPtr<Position> > > (&player_frontier);
			domain = RCPtr< set< RCPtr<Position> > > (&player_domain);			
		}
		
		for (set< RCPtr<Position> >::iterator pos = frontier->begin(); pos != frontier->end(); pos++) {
			set< RCPtr<Position> > adjacent;
			
			if ((*pos)->at_north_pole()) {
				for (int x = 0; x < world_size; x++)
					adjacent.insert( RCPtr<Position> (new Position(x,1)) );
			} else if ((*pos)->at_south_pole()) {
				for (int x = 0; x < world_size; x++)
					adjacent.insert( RCPtr<Position> (new Position(x,world_size-2)) );
			} else {
				adjacent.insert( (*pos)->north() );
				adjacent.insert( (*pos)->south() );
				adjacent.insert( (*pos)->east() );
				adjacent.insert( (*pos)->west() );
			}
			
			for (set< RCPtr<Position> >::iterator a = adjacent.begin(); a != adjacent.end(); a++)
				if (unclaimed.find(*a) != unclaimed.end()) {
					unclaimed.erase(*a);
					new_frontier->insert(*a);
				}
			
			domain->insert(*pos);
		}
		
		frontier = new_frontier;
		opponent = !opponent;		
	}
	
	player_domain.insert(player_frontier.begin(), player_frontier.end());
	opponent_domain.insert(opponent_frontier.begin(), opponent_frontier.end());
	
	return pair<int,int> (player_domain.size(), opponent_domain.size());
}

void World::save(string filename, int player) {
	int OWN_WALL = (player == BLUE) ? BLUE_WALL : RED_WALL;
	int OTHER_WALL = (player == BLUE) ? RED_WALL : BLUE_WALL;
	int OWN = player;
	int OTHER = (player == BLUE) ? RED : BLUE;
	
	ofstream file (filename.c_str());
	if (file.is_open()) {
		for (int x = 0; x < world_size; x++)
			for (int y = 0; y < world_size; y++) {
				file << x << " " << y << " " << state_string(world[x][y]) << endl;
			}
	}
	else cerr << "Unable to open specified state file: " << filename << endl;
}

tron::Strategy::Strategy() {
	time_limit = TIME_LIMIT;
}

void tron::Strategy::move(RCPtr<World> world) {
	vector<int> lons;
	
	Position pos = world->get_pos_player();
	
	if (pos.at_south_pole()) {
		for (int i = 0; i < world_size; i++) lons.push_back(i);
		random_shuffle(lons.begin(), lons.end());
		for (vector<int>::iterator lon = lons.begin(); lon != lons.end(); lon++)
			if (world->state(*lon, world_size-2) == EMPTY) {
				world->get_pos_player().go_north(*lon);
				break;
			}
	} else if (pos.at_north_pole()) {
		for (int i = 0; i < world_size; i++) lons.push_back(i);
		random_shuffle(lons.begin(), lons.end());
		for (vector<int>::iterator lon = lons.begin(); lon != lons.end(); lon++)
			if (world->state(*lon, 1) == EMPTY) {
				world->get_pos_player().go_south(*lon);
				break;
			}		
	} else {
		vector<int> moves;
		for (int i=0; i<4; i++) moves.push_back(i);
		random_shuffle(moves.begin(), moves.end());
		
		for (vector<int>::iterator m = moves.begin(); m != moves.end(); m++) {
				if ((*m == 0) && (world->state(*pos.north()) == EMPTY)) {
					world->get_pos_player().go_north();
					break;
				} else if ((*m == 1) && (world->state(*pos.south()) == EMPTY)) {
					world->get_pos_player().go_south();
					break;
				} else if ((*m == 2) && (world->state(*pos.east()) == EMPTY)) {
					world->get_pos_player().go_east();
					break;
				} else if ((*m == 3) && (world->state(*pos.west()) == EMPTY)) {
					world->get_pos_player().go_west();
					break;
				}
		}
	}
	
	world->set_state(world->get_pos_player(), PLAYER);
	world->set_state(pos, PLAYER_WALL);
}
