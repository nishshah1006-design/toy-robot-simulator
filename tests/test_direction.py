import pytest

from robot_simulator.direction import Direction


def test_from_string_valid_case_insensitive():
    assert Direction.from_string("north") == Direction.NORTH
    assert Direction.from_string("EAST") == Direction.EAST
    assert Direction.from_string(" South ") == Direction.SOUTH


def test_from_string_invalid_raises():
    with pytest.raises(ValueError):
        Direction.from_string("UP")


@pytest.mark.parametrize(
    "start, expected_left, expected_right",
    [
        (Direction.NORTH, Direction.WEST, Direction.EAST),
        (Direction.EAST, Direction.NORTH, Direction.SOUTH),
        (Direction.SOUTH, Direction.EAST, Direction.WEST),
        (Direction.WEST, Direction.SOUTH, Direction.NORTH),
    ],
)
def test_left_and_right_rotation(start, expected_left, expected_right):
    assert start.left() == expected_left
    assert start.right() == expected_right


def test_four_lefts_return_to_start():
    d = Direction.NORTH
    for _ in range(4):
        d = d.left()
    assert d == Direction.NORTH


def test_four_rights_return_to_start():
    d = Direction.EAST
    for _ in range(4):
        d = d.right()
    assert d == Direction.EAST


@pytest.mark.parametrize(
    "direction, expected_delta",
    [
        (Direction.NORTH, (0, 1)),
        (Direction.SOUTH, (0, -1)),
        (Direction.EAST, (1, 0)),
        (Direction.WEST, (-1, 0)),
    ],
)
def test_delta(direction, expected_delta):
    assert direction.delta() == expected_delta


def test_str_returns_name():
    assert str(Direction.NORTH) == "NORTH"
