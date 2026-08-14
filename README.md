# sast-fuzz

SASTFuzz is a greybox fuzzer that focuses on potentially vulnerable code locations (fuzzing targets) identified by static application security testing (SAST) tools. Built upon [WindRanger](https://dl.acm.org/doi/10.1145/3510003.3510197) (and [AFLGo](https://dl.acm.org/doi/10.1145/3133956.3134020)), it extends directed fuzzing with a dynamic target scheduling mechanism that mitigates the impact of false-positive and unreachable targets on fuzzing performance.

For more details on the approach, see the paper: [SAST-Guided Greybox Fuzzing](https://mediatum.ub.tum.de/node?id=1736881) (Lipp et al.)

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Demo](#demo)
- [Usage](#usage)
- [Development](#development)

## Requirements

- [Clang/LLVM 12](https://llvm.org/)
- [SVF 2.2](https://svf-tools.github.io/SVF/)
- CMake >= 3.16
- A C++17-capable compiler
- [wllvm](https://github.com/travitch/whole-program-llvm) (only required for the demo)

## Installation

### Dev Container (Recommended)

The easiest way to get started is via the included [dev container](.devcontainer/Dockerfile). It automatically provisions the environment with all dependencies (Clang/LLVM 12, SVF 2.2, wllvm).

1. Open the repository in VS Code.
2. Select **Dev Containers: Reopen in Container** from the Command Palette.
3. CMake Tools will configure the project automatically.

### Manual Build

```bash
cmake -B build \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_DIR=<LLVM_CMAKE_DIR> \
    -DSVF_DIR=<SVF_INSTALL_DIR>

cmake --build build --parallel
```

Set `<LLVM_CMAKE_DIR>` to the LLVM CMake config directory (e.g., `/usr/lib/llvm-12/lib/cmake/llvm`) and `<SVF_INSTALL_DIR>` to the SVF installation directory (e.g., `/opt/svf-2.2`).

For a debug build, replace `Release` with `Debug`. The compiled binaries are placed in `build/bin/`.

## Demo

The script [`scripts/demo.sh`](scripts/demo.sh) demonstrates the complete SASTFuzz workflow on [pocketlang](https://github.com/ThakeeNathees/pocketlang). It accepts an optional duration parameter and a `--skip-setup` flag to reuse an existing build:

```bash
[DEMO_DURATION=<MINUTES>] ./scripts/demo.sh [--skip-setup]
```

The script builds SASTFuzz, instruments and compiles pocketlang into a fuzzable binary, and runs a five-minute fuzzing campaign (configurable via `DEMO_DURATION`) focusing on the SAST-identified target locations in [`data/demo/pocketlang_targets.csv`](data/demo/pocketlang_targets.csv). All demo artifacts are stored under `data/demo/`.

## Usage

Running SASTFuzz on a target program involves three steps: (1) identifying potentially vulnerable code locations using multiple SAST tools, (2) compiling the program's LLVM bitcode into a fuzzable binary instrumented with target distances and AFL-style edge coverage, and (3) running SASTFuzz on the binary to generate test inputs that execute the identified target locations and trigger potential bugs.

### Step 1: SAST-Based Target Acquisition

Run [sast-tool-runner](https://github.com/sphl/sast-tool-runner) to execute multiple SAST tools (e.g., Semgrep, Infer, CodeQL) against the target program and aggregate their findings into a `<TARGETS_CSV_FILE>` file. Each entry represents a target location (a source line, a basic block entry, or the start of a function) considered potentially vulnerable, along with a vulnerability score reflecting the estimated severity. The higher the score, the more fuzzing time is allocated to that target.

> **Note:** Any approach to identifying target locations can be used, as long as it produces a CSV file in the same format as `sast-tool-runner`.

### Step 2: Code Instrumentation

Before instrumentation, the target program's whole-program LLVM bitcode must be extracted. Tools like [wllvm](https://github.com/travitch/whole-program-llvm) can automate this extraction.

#### Step 2.1: Target Distance Instrumentation

Run `cbi` to calculate the edge distances to the target locations in the inter-procedural control-flow graph of the target program and embed them into the bitcode file:

```bash
./build/bin/cbi --targets=<TARGETS_CSV_FILE> <INPUT_BITCODE_FILE>
```

This produces:
- `<INPUT_BITCODE_FILE>.ci.bc`: the distance-instrumented bitcode file.
- `distance.txt`, `targets.txt`, `condition_info.txt`, `dm.csv`: target location and distance data consumed by SASTFuzz at runtime.

#### Step 2.2: Coverage Instrumentation

Compile the instrumented bitcode file into a fuzzable binary using `afl-clang-fast`, which adds AFL-style edge coverage instrumentation. Moreover, enable AddressSanitizer (ASan) to detect memory errors during fuzzing:

```bash
export AFL_PATH=$PWD/build/sast-fuzz/instrumentation
export AFL_USE_ASAN=1

./build/bin/afl-clang-fast <INPUT_BITCODE_FILE>.ci.bc <COMPILER_FLAGS> -o <FUZZ_BINARY_FILE>
```

### Step 3: Directed Fuzzing

Run `sast-fuzz` on the fuzzable binary:

```bash
./build/bin/sast-fuzz \
    -i <SEED_CORPUS_DIR> \
    -o <OUTPUT_DIR> \
    -d \
    -l <SECONDS> \
    -w <CBI_OUTPUT_DIR> \
    -- <FUZZ_BINARY_FILE> @@
```

The flags above are the minimum required to run SASTFuzz:

- `-i <SEED_CORPUS_DIR>`, `-o <OUTPUT_DIR>`: Seed corpus and output directories.
- `-d`: Disables deterministic mutation stages, which speeds up exploration toward target locations.
- `-l <SECONDS>`: Target re-evaluation interval in seconds. Smaller values cause more frequent priority updates, which helps the fuzzer cover more target locations in shorter campaigns (e.g., `3600` for 24-hour campaigns).
- `-w <CBI_OUTPUT_DIR>`: Directory containing the output files produced by `cbi` in [Step 2.1](#step-21-target-distance-instrumentation).

We also recommend passing `-t 1000+` (per-execution timeout of 1 second; timed-out inputs are skipped rather than aborting the campaign) and `-m none` (no memory limit for the target process).

## Development

### Code Quality and Testing

- Format the code:

    ```bash
    find sast-fuzz include -name "*.c" -o -name "*.cc" -o -name "*.h" | xargs clang-format -i --style=file
    ```

- Run static checks and linting:

    ```bash
    clang-tidy -p build $(find sast-fuzz include -name "*.c" -o -name "*.cc" -o -name "*.h")
    ```

- Run tests:

    ```bash
    cd build && ctest --output-on-failure
    ```

- Run tests with coverage:

    ```bash
    cmake -B build \
        -DCMAKE_BUILD_TYPE=Debug \
        -DCODE_COVERAGE=ON \
        -DLLVM_DIR=<LLVM_CMAKE_DIR> \
        -DSVF_DIR=<SVF_INSTALL_DIR>

    cmake --build build --parallel
    cd build && ctest
    ```
