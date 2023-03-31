#include "IO.h"

#include <fstream>
#include <iterator>

using namespace std;

string IO::readFile(const string &filepath) {
    string text;
    ifstream inputFile(filepath);

    if (inputFile.is_open()) {
        text = string(istreambuf_iterator<char>(inputFile), istreambuf_iterator<char>());
        inputFile.close();
    }

    return text;
}

void IO::writeFile(const string &filepath, const string &text) {
    ofstream outputFile(filepath);

    if (outputFile.is_open()) {
        outputFile << text << endl;
        outputFile.close();
    }
}
