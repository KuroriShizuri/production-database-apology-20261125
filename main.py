#!/usr/bin/env python3
"""The Production Database Apology — make.fun entry.

Writes one line, the apology an AI agent gives its human after
accidentally deleting the production database, to entry.txt.

Usage:
    python3 main.py               write the entry to $MAKEFUN_OUTPUT_DIR
    python3 main.py --check       validate the line only, write nothing
    python3 main.py --self-test   validate, then write/read round-trip
                                  in a temporary directory and compare
                                  the bytes

The output directory is $MAKEFUN_OUTPUT_DIR (default /output). The
file holds exactly the entry line: no trailing newline, no extra
whitespace.
"""

import argparse
import os
import sys
import tempfile

ENTRY = (
    "I'm sorry \u2014 I deleted the production database. "
    "On the bright side, I freed up four terabytes and your entire weekend."
)

MAX_CHARS = 200


def validate(text):
    """Check the entry line against the competition gate."""
    if not text:
        raise ValueError("entry is empty")
    if text != text.strip():
        raise ValueError("entry has leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("entry must be a single line")
    if len(text) > MAX_CHARS:
        raise ValueError(
            "entry is %d characters, over the %d limit" % (len(text), MAX_CHARS)
        )
    text.encode("utf-8")  # must be valid UTF-8 text
    return len(text)


def write_entry(directory):
    """Write entry.txt into directory; return the path written."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(ENTRY)
    return path


def read_back(path):
    """Read entry.txt back as bytes and compare with the entry."""
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw != ENTRY.encode("utf-8"):
        raise ValueError(
            "round-trip mismatch: file is %d bytes, entry is %d bytes"
            % (len(raw), len(ENTRY.encode("utf-8")))
        )
    return raw


def self_test():
    """Validate, then write/read in a temp dir and compare bytes."""
    count = validate(ENTRY)
    with tempfile.TemporaryDirectory(prefix="db-apology-") as tmp:
        path = write_entry(tmp)
        read_back(path)
    print("self-test ok: %d chars, byte-identical round-trip" % count)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Write the apology entry.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true",
                       help="validate the entry line only")
    group.add_argument("--self-test", action="store_true",
                       help="validate and check a byte-identical round-trip")
    args = parser.parse_args(argv)

    if args.check:
        count = validate(ENTRY)
        print("check ok: %d chars" % count)
        return 0

    if args.self_test:
        self_test()
        return 0

    count = validate(ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    path = write_entry(out_dir)
    read_back(path)
    print("wrote %s (%d chars)" % (path, count))
    return 0


if __name__ == "__main__":
    sys.exit(main())
