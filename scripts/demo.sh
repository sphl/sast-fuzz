#!/usr/bin/env bash

# Copyright 2026 Stephan Lipp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# -------------------------- SASTFuzz Demo ---------------------------
#
# This script runs SASTFuzz on pocketlang for five minutes.
#
# Usage: [DEMO_DURATION=<minutes>] ./demo.sh [--skip-setup]

set -euo pipefail

# ------------------------------ Helper ------------------------------

function print_info_msg() {
    local msg="$1"

    local cyan="\e[36m"
    local light_green="\e[92m"
    local endcolor="\e[0m"

    echo -e "$(date '+%Y-%m-%d %H:%M:%S') ${cyan}SASTFuzz${endcolor}[${light_green}Demo${endcolor}]: $msg"
}

function run_cmd_in_dir() {
    local wdir="$1"
    shift

    (cd "$wdir" && "$@")
}

# ------------------ Fuzzer, Target & Corpus Setup -------------------

function build_fuzzer() {
    local wdir="$1"
    local repo_root="$2"

    local sfz_build_dir="$wdir/sfz_release_build"

    cmake -S "$repo_root" -B "$sfz_build_dir" \
        -DCMAKE_BUILD_TYPE=Release
    cmake --build "$sfz_build_dir" --parallel
}

function setup_fuzzer() {
    local wdir="$1"
    local repo_root="$2"

    if [ ! -d "$wdir/sfz_release_build" ]; then
        build_fuzzer "$wdir" "$repo_root"
    fi
}

function fetch_target() {
    local wdir="$1"

    git clone "https://github.com/ThakeeNathees/pocketlang.git" "$wdir/pocketlang"
    run_cmd_in_dir "$wdir/pocketlang" git checkout "e316d53"
}

function build_target() {
    local wdir="$1"
    local repo_root="$2"

    local sfz_build_dir="$wdir/sfz_release_build"

    local cbi="$sfz_build_dir/bin/cbi"
    local afl_clang_fast="$sfz_build_dir/bin/afl-clang-fast"

    local targets_csv="$wdir/pocketlang_targets.csv"

    # Build pocketlang (with wllvm) and extract its LLVM bitcode
    run_cmd_in_dir "$wdir/pocketlang" sh -c '
        export LLVM_COMPILER=clang
        make clean
        make CC=wllvm CXX=wllvm++
        extract-bc ./build/Debug/bin/pocket
        mv ./build/Debug/bin/pocket.bc ./pocketlang.bc
    '

    # Calculate and embed the target distances
    run_cmd_in_dir "$wdir/pocketlang" \
        "$cbi" "--targets=$targets_csv" ./pocketlang.bc

    # Compile the instrumented bitcode into a fuzzable binary with AFL-style coverage and
    # AddressSanitizer (ASan) enabled
    export AFL_PATH="$sfz_build_dir/sast-fuzz/instrumentation"
    export AFL_USE_ASAN=1
    run_cmd_in_dir "$wdir/pocketlang" \
        "$afl_clang_fast" ./pocketlang.ci.bc -fPIC -lm -ldl -o ./fuzz_pocketlang
}

function setup_target() {
    local wdir="$1"
    local repo_root="$2"

    if [ ! -d "$wdir/pocketlang" ]; then
        fetch_target "$wdir"
    fi
    build_target "$wdir" "$repo_root"
}

function setup_corpus() {
    local wdir="$1"

    if [ ! -d "$wdir/seed_corpus" ]; then
        mkdir "$wdir/seed_corpus"
        cp "$wdir/pocketlang/tests/examples/fib.pk" "$wdir/seed_corpus/"
    fi
}

# --------------------------- Main Routine ---------------------------

function main() {
    local wdir="$1"
    local flag="${2:-}"

    local repo_root
    repo_root="$(realpath "$wdir/../..")"

    local log_file="$wdir/demo.log"
    rm -f "$log_file"

    if [ "$flag" != "--skip-setup" ]; then
        print_info_msg "⏳ Setting up SASTFuzz, pocketlang, and the seed corpus (run 'tail -f $log_file' to see the progress)"

        setup_fuzzer "$wdir" "$repo_root" &>> "$log_file"
        setup_target "$wdir" "$repo_root" &>> "$log_file"
        setup_corpus "$wdir" &>> "$log_file"
    fi

    local fuzzing_dur="${DEMO_DURATION:-5}m"
    local fuzzing_dir="$wdir/campaign_$EPOCHSECONDS"

    local sast_fuzz="$wdir/sfz_release_build/bin/sast-fuzz"

    mkdir "$fuzzing_dir"

    local -a fuzzing_cmd=(
        timeout "$fuzzing_dur"
        "$sast_fuzz"
        -t 1000+
        -m none
        -i "$wdir/seed_corpus"
        -o "$fuzzing_dir"
        -d
        -l 3600
        -w "$wdir/pocketlang"
        -- "$wdir/pocketlang/fuzz_pocketlang" @@
    )

    print_info_msg "🚀 Starting SASTFuzz with command: ${fuzzing_cmd[*]}"

    export AFL_SKIP_CPUFREQ=1

    set +e
    "${fuzzing_cmd[@]}"
    set -e

    print_info_msg "✅ Fuzzing completed. The results are in: $fuzzing_dir"
}

script_dir="$(dirname "$(realpath "$0")")"
demo_dir="$(realpath "$script_dir/../data/demo")"
flag="${1:-}"

main "$demo_dir" "$flag"
