import pytest

from robot_simulator.commands import Command, CommandParseError, parse_line
from robot_simulator.direction import Direction


def test_parse_place_basic():
    cmd = parse_line("PLACE 1,2,NORTH")
    assert cmd == Command(name="PLACE", x=1, y=2, facing=Direction.NORTH)


def test_parse_place_case_insensitive_and_spacing():
    cmd = parse_line("place 1 , 2 , north")
    assert cmd == Command(name="PLACE", x=1, y=2, facing=Direction.NORTH)


@pytest.mark.parametrize("name", ["MOVE", "move", "Left", "RIGHT", "report"])
def test_parse_simple_commands(name):
    cmd = parse_line(name)
    assert cmd.name == name.upper()
    assert cmd.x is None and cmd.y is None and cmd.facing is None


@pytest.mark.parametrize("line", ["", "   ", "# a comment"])
def test_blank_and_comment_lines_return_none(line):
    assert parse_line(line) is None


def test_parse_unknown_command_raises():
    with pytest.raises(CommandParseError):
        parse_line("JUMP")


def test_parse_place_bad_direction_raises():
    with pytest.raises(CommandParseError):
        parse_line("PLACE 1,2,UP")


@pytest.mark.parametrize(
    "line",
    [
        "PLACE 1,2",
        "PLACE 1,NORTH",
        "PLACE a,b,NORTH",
        "PLACE 1,2,",
        "PLACE",
    ],
)
def test_parse_place_malformed_raises(line):
    with pytest.raises(CommandParseError):
        parse_line(line)


def test_parse_place_negative_numbers_parsed_but_may_be_off_table():
    # Parsing itself should succeed; bounds checking is Robot/Table's job.
    cmd = parse_line("PLACE -1,-2,SOUTH")
    assert cmd == Command(name="PLACE", x=-1, y=-2, facing=Direction.SOUTH)
