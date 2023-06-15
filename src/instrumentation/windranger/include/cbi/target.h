#ifndef CBI_TARGET_H
#define CBI_TARGET_H

#include <string>

namespace cbi {

using LineNumber = unsigned long;

class Target {
  private:
    std::string filename;
    LineNumber lineNumber;
    double score;

  public:
    Target(const std::string &filename, LineNumber lineNumber, double score);

    /**
     * Returns the target filename.
     *
     * @return
     */
    [[nodiscard]] const std::string &getFilename() const;

    /**
     * Returns the target line number.
     *
     * @return
     */
    [[nodiscard]] LineNumber getLineNumber() const;

    /**
     * Returns the target vulnerability score.
     *
     * @return
     */
    [[nodiscard]] double getScore() const;

    /**
     * Creates a Target object from a ('delimiter'-separated) line.
     *
     * @param line
     * @param delimiter
     * @return
     */
    static Target fromLine(std::string &line, char delimiter = ',');

    bool operator==(const Target &rhs) const;

    bool operator!=(const Target &rhs) const;
};

}  // namespace cbi

#endif  // CBI_TARGET_H
