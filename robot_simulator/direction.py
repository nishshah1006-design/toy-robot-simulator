"""Compass direction handling for the toy robot."""

from __future__ import annotations

from enum import Enum
from typing import Tuple


class Direction(Enum):
    """The four compass directions the robot can face.

    The integer value encodes clockwise ordering starting at NORTH,
    which makes LEFT/RIGHT rotations a simple +/-1 step (mod 4).
    """

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    @classmethod
    def from_string(cls, value: str) -> "Direction":
        """Parse a direction from its textual name (case-insensitive).

        Raises:
            ValueError: if the text does not match a known direction.
        """
        try:
            return cls[value.strip().upper()]
        except KeyError as exc:
            valid = ", ".join(d.name for d in cls)
            raise ValueError(
                f"Invalid direction '{value}'. Expected one of: {valid}"
            ) from exc

    def left(self) -> "Direction":
        """Return the direction obtained by rotating 90 degrees left."""
        return Direction((self.value - 1) % 4)

    def right(self) -> "Direction":
        """Return the direction obtained by rotating 90 degrees right."""
        return Direction((self.value + 1) % 4)

    def delta(self) -> Tuple[int, int]:
        """Return the (dx, dy) unit vector for moving one step in this direction."""
        return _DELTAS[self]

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


_DELTAS = {
    Direction.NORTH: (0, 1),
    Direction.EAST: (1, 0),
    Direction.SOUTH: (0, -1),
    Direction.WEST: (-1, 0),
}
