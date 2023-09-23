# Copyright 2023 Stephan Lipp
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

import unittest
from pathlib import Path

from cdd.container.san import SanitizerOutput, StackFrame


class TestSanitizerOutput(unittest.TestCase):
    def test_from_file(self) -> None:
        # Arrange
        sanitizer_files = [
            Path(__file__).parent / "data" / "sanitizer" / "test.703472",
            Path(__file__).parent / "data" / "sanitizer" / "test.703478",
            Path(__file__).parent / "data" / "sanitizer" / "test.703498",
        ]

        expected = [
            SanitizerOutput(
                "/path/to/file01",
                "segv",
                [
                    StackFrame(0, "outputscript.c", "outputSWF_TEXT_RECORD", 1429),
                    StackFrame(1, "outputscript.c", "outputSWF_DEFINETEXT", 1471),
                    StackFrame(2, "outputscript.c", "outputBlock", 2079),
                    StackFrame(3, "main.c", "readMovie", 277),
                    StackFrame(4, "main.c", "main", 350),
                    StackFrame(5, "libc-start.c", "__libc_start_main", 308),
                    StackFrame(6, "-", "_start", -1),
                ],
            ),
            SanitizerOutput(
                "/path/to/file04",
                "segv",
                [
                    StackFrame(0, "decompile.c", "OpCode", 868),
                    StackFrame(1, "decompile.c", "decompileINCR_DECR", 1474),
                    StackFrame(2, "decompile.c", "decompileAction", 3225),
                    StackFrame(3, "decompile.c", "decompileActions", 3401),
                    StackFrame(4, "decompile.c", "decompile5Action", 3423),
                    StackFrame(5, "outputscript.c", "outputSWF_DOACTION", 1548),
                    StackFrame(6, "outputscript.c", "outputBlock", 2079),
                    StackFrame(7, "main.c", "readMovie", 277),
                    StackFrame(8, "main.c", "main", 350),
                    StackFrame(9, "libc-start.c", "__libc_start_main", 308),
                    StackFrame(10, "-", "_start", -1),
                ],
            ),
            SanitizerOutput(
                "/path/to/file14",
                "heap-buffer-overflow",
                [
                    StackFrame(0, "asan_interceptors.cpp", "strcat", 375),
                    StackFrame(1, "decompile.c", "dcputs", 104),
                    StackFrame(2, "decompile.c", "decompileIMPLEMENTS", 3094),
                    StackFrame(3, "decompile.c", "decompileAction", 3375),
                    StackFrame(4, "decompile.c", "decompileActions", 3401),
                    StackFrame(5, "decompile.c", "decompile5Action", 3423),
                    StackFrame(6, "outputscript.c", "outputSWF_DOACTION", 1548),
                    StackFrame(7, "outputscript.c", "outputBlock", 2079),
                    StackFrame(8, "main.c", "readMovie", 277),
                    StackFrame(9, "main.c", "main", 350),
                    StackFrame(10, "libc-start.c", "__libc_start_main", 308),
                    StackFrame(11, "-", "_start", -1),
                ],
            ),
        ]

        # Act
        actual = [SanitizerOutput.from_file(f) for f in sanitizer_files]

        # Assert
        for i in range(len(expected)):
            self.assertEqual(expected[i], actual[i])
