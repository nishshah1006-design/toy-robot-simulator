"""High-level simulator: feed it lines of text, get REPORT output back."""

from __future__ import annotations

from typing import Iterable, List, Optional, TextIO

from .commands import Command, CommandParseError, parse_line
from .robot import Robot
from .table import Table


class Simulator:
    """Runs a sequence of commands against a :class:`Robot`.

    Malformed or unrecognised lines are skipped (optionally logged via
    `on_error`), matching the spec's tolerant "discard invalid commands"
    behaviour for anything before a valid PLACE, and simply being safe
    no-ops afterwards too.
    """

    def __init__(
        self,
        robot: Optional[Robot] = None,
        table: Optional[Table] = None,
        on_error: Optional[callable] = None,
    ) -> None:
        self.table = table or Table()
        self.robot = robot or Robot(self.table)
        self._on_error = on_error

    def execute(self, command: Command) -> Optional[str]:
        """Execute a single already-parsed command.

        Returns the REPORT string if this command was REPORT and the
        robot is placed, otherwise None.
        """
        if command.name == "PLACE":
            self.robot.place(command.x, command.y, command.facing)
        elif command.name == "MOVE":
            self.robot.move()
        elif command.name == "LEFT":
            self.robot.turn_left()
        elif command.name == "RIGHT":
            self.robot.turn_right()
        elif command.name == "REPORT":
            return self.robot.report_str()
        return None

    def run_line(self, line: str) -> Optional[str]:
        """Parse and execute a single raw line, returning REPORT output (if any)."""
        try:
            command = parse_line(line)
        except CommandParseError as exc:
            if self._on_error:
                self._on_error(str(exc))
            return None
        if command is None:
            return None
        return self.execute(command)

    def run(self, lines: Iterable[str]) -> List[str]:
        """Run many lines, returning the list of REPORT outputs produced."""
        outputs: List[str] = []
        for line in lines:
            result = self.run_line(line)
            if result is not None:
                outputs.append(result)
        return outputs

    def run_stream(self, stream: TextIO) -> List[str]:
        """Run all lines from a file-like object."""
        return self.run(stream)
