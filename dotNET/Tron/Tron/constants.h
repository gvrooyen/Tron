/* "player" and "blue" are equivalent, as are "opponent" and "red". The different names exist so that games
   strategy code (policies) can refer to the player and the opponent, while adjudicating code (that needs to take
   both players' interests into account) can refer to the blue and the red player.
*/

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

const pair <int, int> SOUTH (0, -1);
const pair <int, int> NORTH (0, +1);
const pair <int, int> EAST (+1, 0);
const pair <int, int> WEST (-1, 0);

struct STATE {
    static map <string,int> create_map()
        {
          map <string,int> m;
          m["clear"] = EMPTY;
          m["you"] = PLAYER;
          m["opponent"] = OPPONENT;
          m["yourwall"] = PLAYER_WALL;
          m["opponentwall"] = OPPONENT_WALL;
          return m;
        }
    static const map <string, int> MAP;
};

const map <string, int> STATE::MAP =  STATE::create_map();
