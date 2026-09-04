import pytest

from robot_simulator.direction import Direction
from robot_simulator.robot import Robot
from robot_simulator.table import Table


@pytest.fixture
def robot():
    return Robot(Table())


def test_not_placed_initially(robot):
    assert robot.is_placed is False
    assert robot.report() is None
    assert robot.report_str() is None


def test_place_valid_position(robot):
    assert robot.place(2, 3, Direction.NORTH) is True
    assert robot.is_placed is True
    assert robot.report() == (2, 3, Direction.NORTH)


@pytest.mark.parametrize(
    "x, y",
    [(-1, 0), (0, -1), (5, 0), (0, 5), (10, 10)],
)
def test_place_rejects_off_table(robot, x, y):
    assert robot.place(x, y, Direction.NORTH) is False
    assert robot.is_placed is False


def test_commands_ignored_before_place(robot):
    assert robot.move() is False
    assert robot.turn_left() is False
    assert robot.turn_right() is False
    assert robot.report() is None


def test_move_changes_position_per_direction():
    r = Robot(Table())
    r.place(1, 1, Direction.NORTH)
    r.move()
    assert r.report() == (1, 2, Direction.NORTH)

    r.place(1, 1, Direction.SOUTH)
    r.move()
    assert r.report() == (1, 0, Direction.SOUTH)

    r.place(1, 1, Direction.EAST)
    r.move()
    assert r.report() == (2, 1, Direction.EAST)

    r.place(1, 1, Direction.WEST)
    r.move()
    assert r.report() == (0, 1, Direction.WEST)


@pytest.mark.parametrize(
    "x, y, facing",
    [
        (0, 0, Direction.SOUTH),
        (0, 0, Direction.WEST),
        (4, 4, Direction.NORTH),
        (4, 4, Direction.EAST),
    ],
)
def test_move_ignored_if_it_would_fall_off(x, y, facing):
    r = Robot(Table())
    r.place(x, y, facing)
    result = r.move()
    assert result is False
    # Position/direction unchanged.
    assert r.report() == (x, y, facing)


def test_left_and_right_rotate_without_moving(robot):
    robot.place(2, 2, Direction.NORTH)
    robot.turn_left()
    assert robot.report() == (2, 2, Direction.WEST)
    robot.turn_right()
    robot.turn_right()
    assert robot.report() == (2, 2, Direction.EAST)


def test_report_str_format(robot):
    robot.place(1, 2, Direction.EAST)
    assert robot.report_str() == "1,2,EAST"


def test_re_place_mid_sequence(robot):
    robot.place(0, 0, Direction.NORTH)
    robot.move()
    robot.place(4, 4, Direction.SOUTH)
    assert robot.report() == (4, 4, Direction.SOUTH)


def test_re_place_off_table_is_rejected_and_keeps_previous_state(robot):
    robot.place(1, 1, Direction.NORTH)
    result = robot.place(10, 10, Direction.NORTH)
    assert result is False
    # Robot remains at its last valid, placed state.
    assert robot.report() == (1, 1, Direction.NORTH)
