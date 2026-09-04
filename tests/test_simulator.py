from pathlib import Path

import pytest

from robot_simulator.simulator import Simulator

TEST_DATA_DIR = Path(__file__).resolve().parent.parent / "test_data"


def run_file(filename: str):
    sim = Simulator()
    path = TEST_DATA_DIR / filename
    with path.open("r", encoding="utf-8") as fh:
        return sim.run(fh)


# --- Spec examples (a), (b), (c) -------------------------------------------------

def test_example_a():
    assert run_file("example_a.txt") == ["0,1,NORTH"]


def test_example_b():
    assert run_file("example_b.txt") == ["0,0,WEST"]


def test_example_c():
    assert run_file("example_c.txt") == ["3,3,NORTH"]


# --- Behaviour driven straight from the string commands (no files) --------------

def test_ignores_commands_before_first_valid_place():
    sim = Simulator()
    outputs = sim.run(
        [
            "MOVE",
            "LEFT",
            "REPORT",  # robot not placed -> no output
            "PLACE 3,3,SOUTH",
            "REPORT",
        ]
    )
    assert outputs == ["3,3,SOUTH"]


def test_invalid_place_is_ignored_and_leaves_robot_unplaced():
    sim = Simulator()
    outputs = sim.run(["PLACE 10,10,NORTH", "REPORT"])
    assert outputs == []  # nothing reported: robot never got placed


def test_move_off_table_is_prevented_but_further_commands_still_work():
    sim = Simulator()
    outputs = sim.run(
        [
            "PLACE 0,0,SOUTH",
            "MOVE",  # would fall off -> ignored
            "REPORT",
            "RIGHT",  # SOUTH -> WEST
            "MOVE",  # facing WEST at (0,0) -> also blocked
            "REPORT",
            "LEFT",  # WEST -> SOUTH
            "LEFT",  # SOUTH -> EAST
            "MOVE",  # now facing EAST -> valid
            "REPORT",
        ]
    )
    assert outputs == ["0,0,SOUTH", "0,0,WEST", "1,0,EAST"]


def test_place_can_be_reissued_mid_sequence():
    sim = Simulator()
    outputs = sim.run(
        [
            "PLACE 0,0,NORTH",
            "MOVE",
            "REPORT",
            "PLACE 4,4,WEST",
            "REPORT",
        ]
    )
    assert outputs == ["0,1,NORTH", "4,4,WEST"]


def test_malformed_lines_are_skipped_without_crashing():
    sim = Simulator()
    outputs = sim.run(
        [
            "PLACE 1,1,NORTH",
            "JUMP",  # unknown -> skipped
            "PLACE 1,1,NORTHEAST",  # bad direction -> skipped
            "PLACE abc,1,NORTH",  # malformed -> skipped
            "REPORT",
        ]
    )
    assert outputs == ["1,1,NORTH"]


def test_on_error_callback_receives_messages():
    errors = []
    sim = Simulator(on_error=errors.append)
    sim.run(["JUMP", "PLACE 1,2,UP"])
    assert len(errors) == 2
    assert "JUMP" in errors[0]
    assert "UP" in errors[1]


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("prevent_fall.txt", ["0,0,SOUTH", "0,0,WEST", "4,4,NORTH", "4,4,EAST"]),
        ("invalid_place_and_reposition.txt", ["0,2,NORTH", "2,2,SOUTH"]),
        ("malformed_commands.txt", ["1,1,NORTH", "1,1,WEST"]),
    ],
)
def test_additional_data_files(filename, expected):
    assert run_file(filename) == expected
