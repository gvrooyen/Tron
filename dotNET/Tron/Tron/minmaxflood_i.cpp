#include "minmaxflood_i.h"
#include <limits>
#include <ctime>

inline State::State() {
	utility = Utility();
	depth = 0;
}

inline State::State(RCPtr<State> _parent, Move _last_move) {
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
	RCPtr<World> result = RCPtr<World> ( new World() );
	State* s = this;
	bool player_leaf = true;
	bool opponent_leaf = true;

	while (s->has_parent()) {
		Position p = Position(s->last_move);
		if (s->depth % 2 == 1) {
			if (opponent_leaf) {
				result->set_state(p, OPPONENT);
				result->set_opponent(p);
				opponent_leaf = false;
			} else {
				result->set_state(p, OPPONENT_WALL);
			}
		} else {
			if (player_leaf) {
				result->set_state(p, PLAYER);
				result->set_player(p);
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
	Position current_player_pos = world->get_pos_player();
	Position current_opponent_pos = world->get_pos_opponent();

	RCPtr<State> root = RCPtr<State> (new State());
	set< RCPtr<State> > frontier;
	frontier.insert(root);
	set< RCPtr<State> > leaves;

	clock_t start_time = clock();
	int max_plies = 1024;

	set< RCPtr<State> > last_full_ply;
	int ply = 0;

	while (( double(clock() - start_time)/CLOCKS_PER_SEC < time_limit ) && (frontier.size() > 0) && (ply < max_plies) ) {
		set< RCPtr<State> > new_frontier;
		bool broke_out = false;

		ply++;

		for (set< RCPtr<State> >::iterator state = frontier.begin(); state != frontier.end(); state++) {
			bool opponent_move = ((*state)->depth %2 == 0);
			RCPtr<World> world_copy = (*state)->render(world);
			set< RCPtr<Move> > valid_moves;

			if ( double(clock() - start_time)/CLOCKS_PER_SEC >= time_limit ) {
				broke_out = true;
				break;
			}

			(*state)->utility.value = calc_utility(world_copy->prospect(opponent_move));
			(*state)->utility.state = Utility::ESTIMATED;

			if ( (*state)->has_parent() ) {
				(*state)->parent->utility.value = -1.0;
				(*state)->parent->utility.state = Utility::UNKNOWN;
			}

			leaves.insert(*state);
			leaves.erase((*state)->parent);
			valid_moves = world_copy->valid_moves(opponent_move);

			for (set< RCPtr<Move> >::iterator move = valid_moves.begin(); move != valid_moves.end(); move++) {
				RCPtr<State> new_state = RCPtr<State> ( new State((*state), *(*move)) );
				new_frontier.insert(new_state);
			}
		}

		if (!broke_out) last_full_ply = frontier;
		frontier = new_frontier;
	}

	leaves = last_full_ply;
	cout << "Game tree analysed up to depth " << (*(leaves.begin()))->depth << endl;

	while (leaves.size() > 0) {
		set< RCPtr<State> > new_leaves;
		for ( set< RCPtr<State> >::iterator state = leaves.begin(); state != leaves.end(); state++) {
			if ( (*state)->depth % 2 == 1 ) {
				if ( ( (*state)->parent->utility.value < -0.0 ) ||
					 ( (*state)->parent->utility.value < (*state)->utility.value) ) {
					(*state)->parent->utility = (*state)->utility;
					(*state)->parent->next_move = (*state)->last_move;
					new_leaves.insert( (*state)->parent );
				}
			} else {
				if ( ( (*state)->parent->utility.value < -0.0 ) ||
					 ( (*state)->parent->utility.value > (*state)->utility.value) ) {
					(*state)->parent->utility = (*state)->utility;
					(*state)->parent->next_move = (*state)->last_move;
					new_leaves.insert( (*state)->parent );
				}
			}
		}

		leaves = new_leaves;
	}

}
