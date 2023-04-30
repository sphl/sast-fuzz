#ifndef SFI_IO_H
#define SFI_IO_H

#include <string>

namespace sfi::io {

/**
 * Reads the contents of a file into a string.
 *
 * @param filepath The path to the file to read.
 * @return The contents of the file as a string, or an empty string if the file could not be opened.
 */
std::string readFile(const std::string &filepath);

/**
 * Writes a string to a file.
 *
 * @param filepath The path to the file to write.
 * @param text The string to write to the file.
 */
void writeFile(const std::string &filepath, const std::string &text);

}  // namespace sfi::io

#endif  // SFI_IO_H
