#include "test.h"
#include "tron.h"
#include <iostream>
#include <assert.h>

using namespace std;

#ifndef TEST
void run_tests() {
	cout << "This application was built without test support." << endl;
}
#else

void test_movement() {
	Position P;

	cout << "- Testing movement" << endl;

	P = Position(10,10);
	assert(P.north()->x() == 10);
	assert(P.north()->y() == 9);
	assert(P.south()->x() == 10);
	assert(P.south()->y() == 11);
	assert(P.east()->x() == 11);
	assert(P.east()->y() == 10);
	assert(P.west()->x() == 9);
	assert(P.west()->y() == 10);
	assert(P.is_adjacent(RCPtr<Position> (new Position(10,11))));
	assert(! P.is_adjacent(RCPtr<Position> (new Position(9,9))));
	assert(! P.is_adjacent(RCPtr<Position> (new Position(20,20))));

	P = Position(0,0);
	assert(P.north()->x() == -1);
	assert(P.north()->y() == -1);
	assert(P.south()->x() == -1);
	assert(P.south()->y() == -1);
	assert(P.east()->x() == 0);
	assert(P.east()->y() == 0);
	assert(P.west()->x() == 0);
	assert(P.west()->y() == 0);
	assert(P.at_north_pole());
	assert(! P.at_south_pole());
	assert(! P.is_adjacent(RCPtr<Position> (new Position(29,0))));
	assert(P.is_adjacent(RCPtr<Position> (new Position(17,1))));

	P = Position(29,29);
	assert(P.north()->x() == -1);
	assert(P.north()->y() == -1);
	assert(P.south()->x() == -1);
	assert(P.south()->y() == -1);
	assert(P.east()->x() == 0);
	assert(P.east()->y() == 29);
	assert(P.west()->x() == 0);
	assert(P.west()->y() == 29);
	assert(! P.at_north_pole());
	assert(P.at_south_pole());
	assert(! P.is_adjacent(RCPtr<Position> (new Position(0,29))));
	assert(P.is_adjacent(RCPtr<Position> (new Position(19,28))));
}

void test_liberties() {
	cout << "- Testing world behaviour and liberty calculation" << endl;
	World W = World();
	World W2;

	W.set_player(RCPtr<Position> (new Position(10,10)), false);
	W.set_player(RCPtr<Position> (new Position(20,20)), true);
	assert(W.liberties() == 4);
	assert(W.liberties(true) == 4);

	W.move_player(RCPtr<Position> (new Position(10,11)), false);
	W.move_player(RCPtr<Position> (new Position(20,21)), true);
	W.move_player(RCPtr<Position> (new Position(21,21)), true);
	W.move_player(RCPtr<Position> (new Position(21,20)), true);
	assert(W.liberties() == 3);
	assert(W.liberties(true) == 2);

	W.move_player(RCPtr<Position> (new Position(17,1)), false);
	W.move_player(RCPtr<Position> (new Position(5,0)), false);
	W.move_player(RCPtr<Position> (new Position(29,29)), true);
	assert(W.liberties() == 29);
	assert(W.liberties(true) == 30);

	assert(W.count_empty_space() == (28*30)+2 - 9);

	W.save("test.state");
	W2 = World("test.state");

	assert(W2.get_pos_player()->x() == 0);
	assert(W2.get_pos_player()->y() == 0);
	assert(W2.get_pos_opponent()->x() == 0);
	assert(W2.get_pos_opponent()->y() == 29);
	assert(W2.liberties() == 29);
	assert(W2.liberties(true) == 30);
	assert(W2.count_empty_space() == (28*30)+2 - 9);
}

void run_tests() {
	cout << "Starting unit tests..." << endl;
	test_movement();
	test_liberties();
	cout << "All tests passed!" << endl;
}

#endif