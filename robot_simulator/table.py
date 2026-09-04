"""The tabletop the robot moves around on."""

from __future__ import annotations


class Table:
    """A rectangular tabletop with the origin (0,0) at the south-west corner."""

    def __init__(self, width: int = 5, height: int = 5) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Table dimensions must be positive integers.")
        self.width = width
        self.height = height

    def is_on_table(self, x: int, y: int) -> bool:
        """Return True if (x, y) is a valid position on this table."""
        return 0 <= x < self.width and 0 <= y < self.height

    def __repr__(self) -> str:  # pragma: no cover - trivial
        return f"Table(width={self.width}, height={self.height})"
