#include <sstream>

#include <cbi/target.h>

using namespace cbi;

Target::Target(const std::string &filename, LineNumber lineNumber, float score)
    : filename(filename), lineNumber(lineNumber), score(score) {}

const std::string &Target::getFilename() const { return filename; }

LineNumber Target::getLineNumber() const { return lineNumber; }

float Target::getScore() const { return score; }

Target Target::fromLine(std::string &line, char delimiter) {
    std::istringstream iss(line);

    std::string token;
    getline(iss, token, delimiter);
    // Skip tool name

    getline(iss, token, delimiter);
    std::string filename = token;

    getline(iss, token, delimiter);
    LineNumber lineNumber = stoi(token);

    // Skip values in between ...
    getline(iss, token, delimiter);
    getline(iss, token, delimiter);
    getline(iss, token, delimiter);
    getline(iss, token, delimiter);
    getline(iss, token, delimiter);

    getline(iss, token, delimiter);
    float score = std::stof(token);

    return {filename, lineNumber, score};
}

bool Target::operator==(const Target &rhs) const {
    return filename == rhs.filename && lineNumber == rhs.lineNumber && score == rhs.score;
}

bool Target::operator!=(const Target &rhs) const { return !(rhs == *this); }
