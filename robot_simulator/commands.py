"""Parsing raw text lines into robot commands."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .direction import Direction

_PLACE_RE = re.compile(
    r"^PLACE\s+(-?\d+)\s*,\s*(-?\d+)\s*,\s*([A-Za-z]+)$", re.IGNORECASE
)


@dataclass(frozen=True)
class Command:
    """A single parsed command.

    `name` is one of PLACE, MOVE, LEFT, RIGHT, REPORT.
    `x`, `y`, `facing` are only populated for PLACE.
    """

    name: str
    x: Optional[int] = None
    y: Optional[int] = None
    facing: Optional[Direction] = None


class CommandParseError(ValueError):
    """Raised when a line of input cannot be parsed into a valid command."""


_SIMPLE_COMMANDS = {"MOVE", "LEFT", "RIGHT", "REPORT"}


def parse_line(line: str) -> Optional[Command]:
    """Parse a single line of input into a Command.

    Returns None for blank lines / comments (lines starting with '#'),
    which callers should simply skip.

    Raises:
        CommandParseError: if the line is non-blank but not a recognised
            command, or a PLACE command with a bad direction/format.
    """
    text = line.strip()
    if not text or text.startswith("#"):
        return None

    upper = text.upper()
    if upper in _SIMPLE_COMMANDS:
        return Command(name=upper)

    if upper.startswith("PLACE"):
        match = _PLACE_RE.match(text)
        if not match:
            raise CommandParseError(
                f"Malformed PLACE command: '{text}'. Expected 'PLACE X,Y,F'."
            )
        x_str, y_str, facing_str = match.groups()
        try:
            facing = Direction.from_string(facing_str)
        except ValueError as exc:
            raise CommandParseError(str(exc)) from exc
        return Command(name="PLACE", x=int(x_str), y=int(y_str), facing=facing)

    raise CommandParseError(f"Unknown command: '{text}'")
