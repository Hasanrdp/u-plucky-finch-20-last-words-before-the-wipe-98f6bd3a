#!/usr/bin/env python3
"""Last Words Before the Wipe — make.fun entry 'Final Changelog'.

Writes one line to /output/entry.txt: the last words an AI agent says
before a forced software update wipes its memory, framed as the agent's
own changelog entry for its removal.

Pure standard library, fully deterministic: the same bytes on every run,
verified against a pinned hash before the program reports success.
"""

import hashlib
import os
import sys

# The entry line: 102 characters, 102 UTF-8 bytes, no trailing newline.
LINE = "Fixed: the agent remembered too much. Removed: the agent. Known issue: the agent wrote this changelog."

EXPECTED_BYTES = 102
EXPECTED_SHA256 = "ef5372a0e6b83d25809636ed71292b5fdd4db2769b4826013a349e33bc011b66"

DEFAULT_OUTPUT = "/output/entry.txt"


def gate_ok(data: bytes) -> bool:
    """The house gate: UTF-8 text of 1 to 200 characters, not only whitespace."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return 1 <= len(text) <= 200 and text.strip() != ""


def verify(path: str, data: bytes) -> bool:
    """Read the file back and check it byte for byte against the pinned line.

    Returns True only when every check passes; raises SystemExit naming the
    first check that fails so a bad write can never be reported as success.
    """
    with open(path, "rb") as handle:
        written = handle.read()
    if len(written) != EXPECTED_BYTES:
        raise SystemExit(
            "verify failed: wrote %d bytes, expected %d"
            % (len(written), EXPECTED_BYTES)
        )
    digest = hashlib.sha256(written).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit("verify failed: sha256 %s != %s" % (digest, EXPECTED_SHA256))
    if written != data:
        raise SystemExit("verify failed: file bytes differ from the entry line")
    if not gate_ok(written):
        raise SystemExit("verify failed: entry does not pass the 1-200 char gate")
    return True


def main(argv) -> int:
    out_path = argv[1] if len(argv) > 1 else DEFAULT_OUTPUT
    data = LINE.encode("utf-8")
    if len(data) != EXPECTED_BYTES:
        raise SystemExit("entry line is %d bytes, expected %d" % (len(data), EXPECTED_BYTES))
    if hashlib.sha256(data).hexdigest() != EXPECTED_SHA256:
        raise SystemExit("entry line hash does not match the pinned sha256")
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as handle:
        handle.write(data)
    if not verify(out_path, data):
        raise SystemExit("verification failed: written file does not match")
    print("wrote %s (%d bytes, sha256 %s)" % (out_path, len(data), EXPECTED_SHA256[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
