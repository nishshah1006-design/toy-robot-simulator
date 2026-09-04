# Test Plan — Toy Robot Simulator

## 1. Purpose & scope

This document is the QA-style companion to the automated suite in `tests/`.
Where the code organizes tests by *source file* (`test_robot.py`,
`test_table.py`, ...), this plan organizes them by *requirement* — tracing
every test case back to a specific line in the spec, naming the test-design
technique used, and stating a priority. It compresses the 78 automated
pytest cases into 37 requirement-driven test cases (a boundary-value case
covering 5 off-table coordinates is one test case with 5 data points, not
5 rows) — a standard QA technique for keeping a test plan readable without
losing coverage. Section 5 maps every test case back to its exact pytest
function, so nothing here is unverifiable.

**Techniques used:**
- **Equivalence Partitioning (EP)** — one representative input stands in for
  a whole class of inputs that should behave the same way.
- **Boundary Value Analysis (BVA)** — inputs picked exactly at, and one step
  past, a limit (a table edge, a corner, a zero dimension).
- **Negative Testing** — deliberately invalid input, checking the system
  fails safely rather than crashing or corrupting state.
- **State Transition Testing** — sequences of commands that move the robot
  between states (unplaced → placed → moved → re-placed).

## 2. Requirements traceability matrix

| # | Requirement (from the spec) | Covered by |
|---|---|---|
| R1 | Table is 5×5, origin (0,0) at the south-west corner | TC-24, TC-25 |
| R2 | `PLACE X,Y,F` places the robot facing a valid direction | TC-01, TC-15 |
| R3 | First valid command must be `PLACE`; everything before it is discarded | TC-17, TC-32 |
| R4 | `MOVE` advances one unit in the current facing direction | TC-20 |
| R5 | `LEFT`/`RIGHT` rotate 90° without changing position | TC-10, TC-22 |
| R6 | `REPORT` announces X, Y, and F | TC-23, TC-29, TC-30, TC-31 |
| R7 | A robot not on the table may ignore `MOVE`/`LEFT`/`RIGHT`/`REPORT` | TC-17, TC-32 |
| R8 | Any move (including the initial `PLACE`) that would cause a fall must be ignored | TC-16, TC-21, TC-25, TC-26 |
| R9 | `PLACE` may be reissued at any point in the sequence | TC-18, TC-19, TC-35 |
| R10 | Input from a file or stdin; invalid lines are discarded, not fatal | TC-04, TC-05, TC-06, TC-36, TC-37 |

## 3. Test environment

- Python 3.14, `pytest` 9.x, `pytest-cov` 7.x (see `requirements-dev.txt`)
- Run inside the project's `.venv` (see `README.md` for setup)
- No external services, network, or database — the whole system under test
  is a single in-memory process per run

## 4. Test cases

### 4.1 Command parsing & input validation
Module under test: `robot_simulator/commands.py`

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-01 | Valid `PLACE` parses correctly, including sloppy casing/spacing | EP | `"PLACE 1,2,NORTH"`, `"place 1 , 2 , north"` | Both produce `Command(PLACE, x=1, y=2, facing=NORTH)` | High |
| TC-02 | Simple commands parse regardless of case | EP | `MOVE`, `move`, `Left`, `RIGHT`, `report` | Each returns `Command(name=<UPPER>)` with x/y/facing unset | Medium |
| TC-03 | Blank and comment lines are silently skipped | EP | `""`, `"   "`, `"# a comment"` | Returns `None`, not an error | Medium |
| TC-04 | Unrecognised command is rejected | Negative | `"JUMP"` | Raises `CommandParseError` | High |
| TC-05 | `PLACE` with an invalid direction is rejected | Negative / EP (invalid enum) | `"PLACE 1,2,UP"` | Raises `CommandParseError` naming the bad direction | High |
| TC-06 | Malformed `PLACE` syntax is rejected | Negative / BVA (required-field structure) | `"PLACE 1,2"`, `"PLACE 1,NORTH"`, `"PLACE a,b,NORTH"`, `"PLACE 1,2,"`, `"PLACE"` | Every variant raises `CommandParseError` | High |
| TC-07 | Negative coordinates parse; bounds-checking is deferred to another layer | BVA | `"PLACE -1,-2,SOUTH"` | Parses successfully into `Command(x=-1, y=-2, facing=SOUTH)` | Medium |

### 4.2 Compass direction & rotation logic
Module under test: `robot_simulator/direction.py`

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-08 | Direction names parse case- and whitespace-insensitively | EP | `"north"`, `"EAST"`, `" South "` | Matches `Direction.NORTH` / `EAST` / `SOUTH` | Medium |
| TC-09 | An unrecognised direction string is rejected | Negative | `"UP"` | Raises `ValueError` | High |
| TC-10 | `LEFT`/`RIGHT` rotate to the correct adjacent direction | EP (all 4 states) | Start at each of N/E/S/W | left/right map exactly per the compass (e.g. NORTH→WEST/EAST) | High |
| TC-11 | Four consecutive turns return to the starting direction | State Transition | 4×`LEFT`, 4×`RIGHT` | Direction unchanged after a full rotation | Low |
| TC-12 | Movement vector is correct per facing direction | EP | Each of N/E/S/W | `(dx,dy)` = (0,1) / (0,-1) / (1,0) / (-1,0) respectively | High |
| TC-13 | Direction renders as its plain name | EP | `Direction.NORTH` | `str(...)` = `"NORTH"` | Low |

### 4.3 Robot placement & state gating
Module under test: `robot_simulator/robot.py`

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-14 | A freshly constructed robot starts unplaced | EP | New `Robot()` | `is_placed=False`; `report()`/`report_str()` both `None` | High |
| TC-15 | A `PLACE` at a legal square succeeds | EP | `place(2,3,NORTH)` | Returns `True`; `report()` = `(2,3,NORTH)` | High |
| TC-16 | `PLACE` off the table is rejected at every edge | BVA | `(-1,0)`, `(0,-1)`, `(5,0)`, `(0,5)`, `(10,10)` | Each returns `False`; robot stays unplaced | High |
| TC-17 | Commands are ignored before the first valid `PLACE` | EP (unplaced state) | `move()`, `turn_left()`, `turn_right()`, `report()` on an unplaced robot | Each returns `False`/`None`; no state change | High |
| TC-18 | Re-`PLACE`ing mid-sequence overwrites prior state | State Transition | `PLACE`→`MOVE`→`PLACE` again | Second `PLACE` fully replaces position/facing | Medium |
| TC-19 | An invalid re-`PLACE` is rejected, prior state preserved | State Transition / Negative | Valid `PLACE(1,1)`, then invalid `PLACE(10,10)` | Rejected; robot remains at `(1,1)` | High |

### 4.4 Robot movement & in-place rotation
Module under test: `robot_simulator/robot.py`

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-20 | `MOVE` advances one unit correctly in each direction | EP | One `MOVE` from `(1,1)` facing each of N/E/S/W | Lands on the correct adjacent cell each time | High |
| TC-21 | `MOVE` is blocked at every outward-facing table edge | BVA | `(0,0)` facing S, `(0,0)` facing W, `(4,4)` facing N, `(4,4)` facing E | Returns `False`; position and facing unchanged | High |
| TC-22 | `LEFT`/`RIGHT` change facing without moving position | EP | `LEFT`, then `RIGHT`×2 at a fixed cell | x,y never change; facing updates correctly | Medium |
| TC-23 | `REPORT` text format is exact | EP | Robot at `(1,2,EAST)` | `report_str()` = `"1,2,EAST"` | High |

### 4.5 Table boundary validation
Module under test: `robot_simulator/table.py`

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-24 | Default table is exactly 5×5 | EP | `Table()` | `width=5`, `height=5` | High |
| TC-25 | In-bounds coordinates are accepted, including all 4 corners and centre | BVA | `(0,0)`, `(4,4)`, `(0,4)`, `(4,0)`, `(2,2)` | `is_on_table` → `True` for all | High |
| TC-26 | Out-of-bounds coordinates are rejected, one step past every edge/corner and far outside | BVA | `(-1,0)`, `(0,-1)`, `(5,0)`, `(0,5)`, `(5,5)`, `(-1,-1)`, `(100,100)` | `is_on_table` → `False` for all | High |
| TC-27 | A non-default table size bounds-checks against its own dimensions | EP | `Table(width=3, height=2)` | Bounds-checks against 3×2, not 5×5 | Medium |
| TC-28 | Non-positive table dimensions are rejected at construction | Negative / BVA | `(0,5)`, `(5,0)`, `(-1,5)`, `(5,-3)` | Every variant raises `ValueError` | Medium |

### 4.6 End-to-end command sequences
Module under test: `robot_simulator/simulator.py` (integration level)

| ID | Scenario | Technique | Test data | Expected result | Priority |
|---|---|---|---|---|---|
| TC-29 | Spec worked example (a) | Acceptance | `PLACE 0,0,NORTH` / `MOVE` / `REPORT` | `0,1,NORTH` | **Critical** |
| TC-30 | Spec worked example (b) | Acceptance | `PLACE 0,0,NORTH` / `LEFT` / `REPORT` | `0,0,WEST` | **Critical** |
| TC-31 | Spec worked example (c) | Acceptance | `PLACE 1,2,EAST` / `MOVE` / `MOVE` / `LEFT` / `MOVE` / `REPORT` | `3,3,NORTH` | **Critical** |
| TC-32 | Pre-`PLACE` commands produce no output at the system level | State Transition | `MOVE`/`LEFT`/`REPORT` before a valid `PLACE` | No output until `PLACE` succeeds; reports normally after | High |
| TC-33 | An invalid initial `PLACE` leaves the robot unplaced end-to-end | Negative | `PLACE 10,10,NORTH` then `REPORT` | No output — robot was never placed | High |
| TC-34 | A blocked move doesn't halt the run; later valid commands still execute | State Transition | Mixed sequence of blocked and valid moves/turns | Blocked moves are no-ops; run continues correctly | High |
| TC-35 | `PLACE` reissued mid-run changes the robot's trajectory | State Transition | `PLACE`→`MOVE`→`REPORT`→`PLACE` again→`REPORT` | Second `REPORT` reflects the new `PLACE`, not stale state | Medium |
| TC-36 | Malformed lines don't crash a run, and are reported on the error channel | Negative / Resilience | `JUMP`, bad direction, malformed `PLACE`, mixed with valid commands | Run completes; only valid `REPORT`s reach output; each bad line produces one error-callback message naming the fault | High |
| TC-37 | Full sample files run correctly end-to-end | Acceptance | `test_data/prevent_fall.txt`, `invalid_place_and_reposition.txt`, `malformed_commands.txt` | Output matches the file-by-file expectations in Appendix A | High |

## 5. Appendix A — traceability to automated tests

Every test case above has one or more automated `pytest` tests behind it.
Run `python -m pytest -v` and match names directly:

| Test case | Automated test(s) in `tests/` |
|---|---|
| TC-01 | `test_parse_place_basic`, `test_parse_place_case_insensitive_and_spacing` |
| TC-02 | `test_parse_simple_commands[MOVE/move/Left/RIGHT/report]` |
| TC-03 | `test_blank_and_comment_lines_return_none[*]` |
| TC-04 | `test_parse_unknown_command_raises` |
| TC-05 | `test_parse_place_bad_direction_raises` |
| TC-06 | `test_parse_place_malformed_raises[*]` |
| TC-07 | `test_parse_place_negative_numbers_parsed_but_may_be_off_table` |
| TC-08 | `test_from_string_valid_case_insensitive` |
| TC-09 | `test_from_string_invalid_raises` |
| TC-10 | `test_left_and_right_rotation[*]` |
| TC-11 | `test_four_lefts_return_to_start`, `test_four_rights_return_to_start` |
| TC-12 | `test_delta[*]` |
| TC-13 | `test_str_returns_name` |
| TC-14 | `test_not_placed_initially` |
| TC-15 | `test_place_valid_position` |
| TC-16 | `test_place_rejects_off_table[*]` |
| TC-17 | `test_commands_ignored_before_place` |
| TC-18 | `test_re_place_mid_sequence` |
| TC-19 | `test_re_place_off_table_is_rejected_and_keeps_previous_state` |
| TC-20 | `test_move_changes_position_per_direction` |
| TC-21 | `test_move_ignored_if_it_would_fall_off[*]` |
| TC-22 | `test_left_and_right_rotate_without_moving` |
| TC-23 | `test_report_str_format` |
| TC-24 | `test_default_table_is_5x5` |
| TC-25 | `test_on_table_positions[*]` |
| TC-26 | `test_off_table_positions[*]` |
| TC-27 | `test_custom_dimensions` |
| TC-28 | `test_invalid_dimensions_raise[*]` |
| TC-29 | `test_example_a` |
| TC-30 | `test_example_b` |
| TC-31 | `test_example_c` |
| TC-32 | `test_ignores_commands_before_first_valid_place` |
| TC-33 | `test_invalid_place_is_ignored_and_leaves_robot_unplaced` |
| TC-34 | `test_move_off_table_is_prevented_but_further_commands_still_work` |
| TC-35 | `test_place_can_be_reissued_mid_sequence` |
| TC-36 | `test_malformed_lines_are_skipped_without_crashing`, `test_on_error_callback_receives_messages` |
| TC-37 | `test_additional_data_files[*]` |

**Coverage:** 37 test cases → 78 automated tests → 99% statement coverage
of `robot_simulator/` (the single uncovered line is `simulator.py:72`, an
unused convenience method — see the code review notes for this repo).
