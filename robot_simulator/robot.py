"""The toy robot itself."""

from __future__ import annotations

from typing import Optional, Tuple

from .direction import Direction
from .table import Table


class Robot:
    """A robot that roams a :class:`Table`, refusing any move that would
    make it fall off the edge.

    The robot ignores MOVE/LEFT/RIGHT/REPORT commands until it has been
    successfully placed on the table via :meth:`place`.
    """

    def __init__(self, table: Optional[Table] = None) -> None:
        self._table = table or Table()
        self._x: Optional[int] = None
        self._y: Optional[int] = None
        self._facing: Optional[Direction] = None

    @property
    def is_placed(self) -> bool:
        """Whether the robot currently sits on the table."""
        return self._facing is not None

    def place(self, x: int, y: int, facing: Direction) -> bool:
        """Place the robot at (x, y) facing `facing`.

        The placement is rejected (robot state unchanged) if it would put
        the robot off the table.

        Returns:
            True if the placement succeeded, False if it was rejected.
        """
        if not self._table.is_on_table(x, y):
            return False
        self._x, self._y, self._facing = x, y, facing
        return True

    def move(self) -> bool:
        """Move one unit forward in the current facing direction.

        Ignored (no-op, returns False) if the robot isn't placed yet, or
        if the move would take it off the table.
        """
        if not self.is_placed:
            return False
        dx, dy = self._facing.delta()
        new_x, new_y = self._x + dx, self._y + dy
        if not self._table.is_on_table(new_x, new_y):
            return False
        self._x, self._y = new_x, new_y
        return True

    def turn_left(self) -> bool:
        """Rotate 90 degrees left (anticlockwise) in place. Ignored if not placed."""
        if not self.is_placed:
            return False
        self._facing = self._facing.left()
        return True

    def turn_right(self) -> bool:
        """Rotate 90 degrees right (clockwise) in place. Ignored if not placed."""
        if not self.is_placed:
            return False
        self._facing = self._facing.right()
        return True

    def report(self) -> Optional[Tuple[int, int, Direction]]:
        """Return the current (x, y, facing), or None if not placed."""
        if not self.is_placed:
            return None
        return self._x, self._y, self._facing

    def report_str(self) -> Optional[str]:
        """Return the report formatted as 'X,Y,F', or None if not placed."""
        state = self.report()
        if state is None:
            return None
        x, y, facing = state
        return f"{x},{y},{facing}"
