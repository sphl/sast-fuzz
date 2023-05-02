#include <iostream>

#include <SVF-FE/LLVMUtil.h>

#include <sfi/inspector.h>
#include <sfi/pretty_printer.h>

using namespace std;
using namespace sfi;

static llvm::cl::opt<std::string> inputFile(llvm::cl::Positional, llvm::cl::desc("<input: LLVM bitcode file>"));

static llvm::cl::opt<std::string> outputFile(llvm::cl::Positional, llvm::cl::desc("<output: JSON file>"));

int main(int argc, char **argv) {
    // Process the passed command-line arguments
    llvm::cl::ParseCommandLineOptions(argc, argv, "SASTFuzz Inspector (SFI)\n");

    // Check if the right number of arguments is specified
    if (argc != 3) {
        cerr << "ERROR: LLVM bitcode file and/or JSON output file not specified!" << endl;
        return 1;
    }

    try {
        // Instantiate a JSON printer- and program inspector object
        JSONPrinter printer;
        Inspector inspector(inputFile);

        // Extract function and inter-procedural CFG information using the inspector
        auto funcInfos = inspector.getFuncInfos();
        auto icfgInfos = inspector.getICFGInfos();

        // Write the obtained information into a JSON file
        printer.printToFile(outputFile, funcInfos, icfgInfos);

        return 0;

    } catch (MissingDebugInfoException &exception) {
        // Output error message if LLVM bitcode file has no debug information
        cerr << exception.what();
        return 1;
    }
}