#include "minmaxflood_i.h"
#include <limits>
#include <ctime>
#include <list>

int State::key_idx = 0;

inline State::State() {
	key = key_idx++;
	utility = Utility();
	depth = 0;
}

inline State::State(RCPtr<State> _parent, Move _last_move) {
	key = key_idx++;
	utility = Utility();
	parent = _parent;
	last_move = _last_move;
	if (parent.objPtr() == 0) {
		depth = 0;
	} else {
		depth = parent->depth + 1;
	}
}

RCPtr<World> State::render(RCPtr<World> world) {
	RCPtr<World> result = RCPtr<World> ( new World(world) );
	State* s = this;
	bool player_leaf = true;
	bool opponent_leaf = true;

	while (s->has_parent()) {
		RCPtr<Position> p = RCPtr<Position> (new Position(s->last_move));
		if (s->depth % 2 == 0) {
			if (opponent_leaf) {
				result->move_opponent(p);
				opponent_leaf = false;
			} else {
				result->set_state(p, OPPONENT_WALL);
			}
		} else {
			if (player_leaf) {
				result->move_player(p);
				player_leaf = false;
			} else {
				result->set_state(p, PLAYER_WALL);
			}
		}
		s = s->parent.objPtr();
	}

	return result;
}

float minmaxflood_i::Strategy::calc_utility(pair<int,int> prospect) {
	int player = prospect.first - 1;
	int opponent = prospect.second - 1;

	if (opponent == 0) {
		if (player == 0) {
			return 1.0;
		} else {
			return numeric_limits<float>::infinity();
		}
	} else if (player == 0) {
		return 0.0;
	} else {
		return ((float)player) / ((float)opponent);
	}
}

void minmaxflood_i::Strategy::move(RCPtr<World> world) {
	// double time_limit = 10000.0;
	RCPtr<Position> current_player_pos = world->get_pos_player();
	RCPtr<Position> current_opponent_pos = world->get_pos_opponent();

	RCPtr<State> root = RCPtr<State> (new State());
	list< RCPtr<State> > frontier;
	frontier.push_back(root);
	list< RCPtr<State> > leaves;

	clock_t start_time = clock();
	int max_plies = 1024;

	list< RCPtr<State> > last_full_ply;
	int ply = 0;
	pair<int,int> p;

	cout << "Current player position: (" << current_player_pos->x() << "," << current_player_pos->y() << ")" << endl;

	while (( double(clock() - start_time)/CLOCKS_PER_SEC < time_limit ) && (frontier.size() > 0) && (ply < max_plies) ) {
		list< RCPtr<State> > new_frontier;
		bool broke_out = false;

		ply++;
		cout << "Ply " << ply << ", frontier size = " << frontier.size() << endl;

		for (list< RCPtr<State> >::iterator state = frontier.begin(); state != frontier.end(); state++) {
			bool opponent_move = ((*state)->depth %2 == 1);
			RCPtr<World> world_copy = (*state)->render(world);
			RCPtr< set<Move> > valid_moves;

			if ( double(clock() - start_time)/CLOCKS_PER_SEC >= time_limit ) {
				broke_out = true;
				break;
			}

			// p = world_copy->prospect(opponent_move);
			p = world_copy->prospect();		// Calculate utility from player's point of view for minimax
			(*state)->utility.value = calc_utility(p);
			(*state)->utility.state = Utility::ESTIMATED;

			// cout << "Utility: " << (*state)->utility.value << endl;

			if ( (*state)->has_parent() ) {
				(*state)->parent->utility.value = -1.0;
				(*state)->parent->utility.state = Utility::UNKNOWN;
			}

			leaves.push_back(*state);

			for (list< RCPtr<State> >::iterator s = leaves.begin(); s != leaves.end(); s++) {
				if (((*state)->has_parent()) && ((*s)->key == (*state)->parent->key)) {
					leaves.erase(s);
					break;
				}
			}

			valid_moves = world_copy->valid_moves(opponent_move);

			for (set<Move>::iterator move = valid_moves->begin(); move != valid_moves->end(); move++) {
				RCPtr<State> new_state = RCPtr<State> ( new State((*state), (*move)) );
				new_frontier.push_back(new_state);
			}
		}

		if (!broke_out) last_full_ply = frontier;
		frontier = new_frontier;
	}

	leaves = last_full_ply;
	cout << "Game tree analysed up to depth " << (*(leaves.begin()))->depth << endl;

	while (leaves.size() > 0) {
		list< RCPtr<State> > new_leaves;
		for ( list< RCPtr<State> >::iterator state = leaves.begin(); state != leaves.end(); state++) {
			if ( (*state)->has_parent() ) {
				if ( (*state)->depth % 2 == 1 ) {
					if ( ( (*state)->parent->utility.value < -0.0 ) ||
						 ( (*state)->parent->utility.value < (*state)->utility.value) ) {
						(*state)->parent->utility = (*state)->utility;
						(*state)->parent->next_move = (*state)->last_move;
						new_leaves.push_back( (*state)->parent );  // check for duplication here
					}
				} else {
					if ( ( (*state)->parent->utility.value < -0.0 ) ||
						 ( (*state)->parent->utility.value > (*state)->utility.value) ) {
						(*state)->parent->utility = (*state)->utility;
						(*state)->parent->next_move = (*state)->last_move;
						new_leaves.push_back( (*state)->parent ); // check for duplication here
					}
				}
			}
		}

		leaves = new_leaves;
	}

	cout << "Player moves to (" << root->next_move.first << "," << root->next_move.second << "); advantage = " << root->utility.value << endl << endl;

	world->set_state(RCPtr<Position> (new Position(root->next_move.first, root->next_move.second)), PLAYER);
	world->set_state(current_player_pos, PLAYER_WALL);
}
