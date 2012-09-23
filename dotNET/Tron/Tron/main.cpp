#include <iostream>
#include "constants.h"
#include "minmaxflood_i.h"
#include "test.h"

using namespace std;


int main (int argc, char *argv[])
{
	cout << "Tron Lightcycle Challenge" << endl;
	cout << "Copyright (c) 2012, G-J van Rooyen <gvrooyen@gmail.com>" << endl;
#ifdef DEBUG
	cout << "DEBUG BUILD" << endl;
#endif
	run_tests();
	return 0;
}

