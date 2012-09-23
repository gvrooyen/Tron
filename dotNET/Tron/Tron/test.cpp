#include "test.h"
#include "tron.h"
#include <iostream>
#include <assert.h>

using namespace std;

#ifndef DEBUG
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

}

void run_tests() {
	cout << "Starting unit tests..." << endl;
	test_movement();
	cout << "All tests passed!" << endl;
}

#endif