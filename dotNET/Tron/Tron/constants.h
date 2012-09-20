#ifndef CONSTANTS_H
#define CONSTANTS_H

#include <utility>
#include <map>
#include <string>

using namespace std;

const int EMPTY = -1;
const int PLAYER = 0;
const int BLUE = 0;
const int OPPONENT = 1;
const int RED = 1;
const int PLAYER_WALL = 2;
const int BLUE_WALL = 2;
const int OPPONENT_WALL = 3;
const int RED_WALL = 3;

typedef pair<int,int> Move;

const Move SOUTH (0, -1);
const Move NORTH (0, +1);
const Move EAST (+1, 0);
const Move WEST (-1, 0);

int State(string description);

#endif
