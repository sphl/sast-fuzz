ARG BASE_IMG=sast-fuzz/devenv
FROM ${BASE_IMG}

ENV SFZ_DIR="/opt/sast-fuzz/build/sast-fuzz"
ENV SFZ_ANALYZER_DIR="/opt/sast-fuzz/static_analysis/sast"
ENV SFZ_FUZZER="${SFZ_DIR}/fuzzing/src/sast-fuzz"
ENV SFZ_INSPECTOR="${SFZ_DIR}/static_analysis/inspection/src/sfi"
ENV SFZ_INST="${SFZ_DIR}/code_instrumentation/windranger/src/cbi"
ENV SFZ_CC="${SFZ_DIR}/code_instrumentation/afl-clang-fast"
ENV SFZ_CXX="${SFZ_DIR}/code_instrumentation/afl-clang-fast++"

WORKDIR /opt

# Install SASTFuzz
COPY ../.. sast-fuzz/

RUN cd sast-fuzz \
    && mkdir build && cd build \
    && cmake -G Ninja -DCMAKE_BUILD_TYPE=Release .. \
    && ninja

WORKDIR ${SFZ_DIR}

CMD ["/usr/bin/bash"]