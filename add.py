# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
from pathlib import Path


dir = Path('.')

for p in dir.glob("**/*.inc"):
    new_content = """# SPDX-FileCopyrightText: 2023 Stephan Lipp, Technical University of Munich (TUM), et al.
# SPDX-License-Identifier: Apache-2.0
"""

    Path(str(p) + ".license").write_text(new_content)
