#!/usr/bin/env python3
"""Toy Robot Simulator - command-line entry point.

Usage:
    python main.py                  # reads commands from stdin
    python main.py commands.txt     # reads commands from a file

REPORT output is printed to stdout, one line per REPORT command.
"""

from __future__ import annotations

import sys

from robot_simulator import Simulator


def main(argv: list[str]) -> int:
    simulator = Simulator(on_error=lambda msg: print(f"Ignored: {msg}", file=sys.stderr))

    if len(argv) > 1:
        path = argv[1]
        try:
            with open(path, "r", encoding="utf-8") as fh:
                lines = fh.readlines()
        except OSError as exc:
            print(f"Could not read file '{path}': {exc}", file=sys.stderr)
            return 1
    else:
        lines = sys.stdin.readlines()

    for line in lines:
        output = simulator.run_line(line)
        if output is not None:
            print(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
