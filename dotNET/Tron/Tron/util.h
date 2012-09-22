#ifndef UTIL_H
#define UTIL_H

#include <vector>
#include <string>

using namespace std;

vector<string> &split(const string &s, char delim, vector<std::string> &elems);

vector<string> split(const string &s, char delim);

#endif
