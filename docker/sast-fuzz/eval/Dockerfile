ARG BASE_IMG=sast-fuzz/fuzzer
FROM ${BASE_IMG}

ENV AFL_VERSION="2.56b"
ENV AFL_DIR="/opt/afl-${AFL_VERSION}"
ENV AFL_FUZZER="${AFL_DIR}/afl-fuzz"
ENV AFL_CC="${AFL_DIR}/afl-clang-fast"
ENV AFL_CXX="${AFL_DIR}/afl-clang-fast++"

WORKDIR /opt

# Install AFL
RUN wget https://github.com/google/AFL/archive/refs/tags/v${AFL_VERSION}.tar.gz \
    && tar -xf v${AFL_VERSION}.tar.gz && rm -f v${AFL_VERSION}.tar.gz \
    && mv AFL-${AFL_VERSION} afl-${AFL_VERSION} \
    && cd afl-${AFL_VERSION} \
    && make \
    && cd llvm_mode && make

WORKDIR /

CMD ["/usr/bin/bash"]