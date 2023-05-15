// SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
// SPDX-License-Identifier: Apache-2.0
#include <fstream>
#include <iterator>

#include <sfi/io.h>

using namespace std;
using namespace sfi;

string io::readFile(const string &filepath) {
    string text;
    ifstream inputFile(filepath);

    if (inputFile.is_open()) {
        text = string(istreambuf_iterator<char>(inputFile), istreambuf_iterator<char>());
        inputFile.close();
    }

    return text;
}

void io::writeFile(const string &filepath, const string &text) {
    ofstream outputFile(filepath);

    if (outputFile.is_open()) {
        //outputFile << text << endl;
        outputFile << text;
        outputFile.close();
    }
}
