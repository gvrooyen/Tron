#include <iostream>
#include "constants.h"
#include "tron.h"
#include "minmaxflood_i.h"
#include "test.h"
#include <cstdlib>
#include <ctime>

using namespace std;


int main (int argc, char *argv[])
{
	string strategy, state_file;
	tron::Strategy S;
	RCPtr<World> W;

	srand((unsigned int)time(NULL));

	if (argc < 3) state_file = "world.state";
	else state_file = argv[2];
	if (argc < 2) strategy = "test";
	else strategy = argv[1];

	cout << "Tron Lightcycle Challenge" << endl;
	cout << "Copyright (c) 2012, G-J van Rooyen <gvrooyen@gmail.com>" << endl << endl;
#ifdef DEBUG
	cout << "DEBUG BUILD" << endl << endl;
#endif

	if (strategy == "test") {
		run_tests();
		cout << endl;
		return 0;
	} else if (strategy == "random") {
		S = tron::Strategy();
	} else if (strategy == "minmaxflood_i") {
		S = minmaxflood_i::Strategy();
	} else {
		cout << "Usage: TRON <strategy> <statefile>" << endl << endl;
		return 0;
	}

	W = RCPtr<World> ( new World(state_file) );
	cout << "Contemplating move..." << endl;
	S.move(W);
	W->save(state_file);
	cout << " Done!" << endl << endl;
}

