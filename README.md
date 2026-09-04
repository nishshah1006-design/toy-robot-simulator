# Toy Robot Simulator

A simulation of a toy robot moving on a 5x5 tabletop, implemented in Python 3
with no third-party runtime dependencies.

## Project layout

```
toy_robot/
├── main.py                     # CLI entry point (stdin or file input)
├── robot_simulator/            # Core library (the actual solution)
│   ├── __init__.py
│   ├── direction.py            # Direction enum (NORTH/EAST/SOUTH/WEST) + rotation
│   ├── table.py                # Table: tabletop bounds checking
│   ├── robot.py                # Robot: position/facing state + movement rules
│   ├── commands.py             # Parses text lines into Command objects
│   └── simulator.py            # Wires parsing + Robot together, runs a sequence
├── tests/                      # pytest unit + integration tests
│   ├── test_direction.py
│   ├── test_table.py
│   ├── test_robot.py
│   ├── test_commands.py
│   └── test_simulator.py       # includes the spec's worked examples (a), (b), (c)
├── test_data/                  # Sample input files exercising the app
│   ├── example_a.txt / example_b.txt / example_c.txt   # spec examples
│   ├── ignore_before_place.txt
│   ├── prevent_fall.txt
│   ├── invalid_place_and_reposition.txt
│   └── malformed_commands.txt
├── pytest.ini
└── requirements-dev.txt
```

## Design

- **`Table`** knows nothing about the robot — just tabletop dimensions and
  whether a coordinate is within bounds. Makes the table size trivially
  configurable/testable in isolation.
- **`Direction`** is a small `Enum` with clockwise integer values, so
  `LEFT`/`RIGHT` are just `-1`/`+1` steps (mod 4), and each direction knows
  its own `(dx, dy)` movement vector — no big if/elif ladders anywhere.
- **`Robot`** owns its own state (`x`, `y`, `facing`) and enforces the two
  core business rules directly:
  1. Ignore all commands until a valid `PLACE` has succeeded.
  2. Reject any `PLACE`/`MOVE` that would put it off the table, leaving its
     prior state untouched.
- **`commands.py`** turns a raw text line into a `Command` dataclass (or
  raises `CommandParseError` for garbage input), completely decoupled from
  robot logic — it doesn't know or care about table bounds.
- **`Simulator`** is the orchestration layer: parses each line and
  dispatches it to the robot, collecting `REPORT` output. It swallows
  parse errors so one bad line can't crash a whole run, matching the
  spec's "discard invalid commands" requirement.

This separation means each class has a single, easily testable
responsibility, and the table size, robot, and parser can all be swapped
or reused independently (e.g. a bigger board, or a different input format).

## Running it

From the `toy_robot/` directory:

```bash
# From a file
python3 main.py test_data/example_a.txt

# From stdin
echo -e "PLACE 0,0,NORTH\nMOVE\nREPORT" | python3 main.py
```

Expected output for `example_a.txt`:
```
0,1,NORTH
```

Any unrecognised/malformed line is silently skipped from stdout and noted
on stderr (`Ignored: ...`), so a typo never crashes a run.

## Running the tests

Set up a virtual environment first so dependencies stay isolated to this
project rather than installed globally:

```bash
python3 -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

pip install -r requirements-dev.txt
python3 -m pytest --cov=robot_simulator --cov-report=term-missing
```

`.venv/` is git-ignored, so it's local to your machine and never committed.

78 tests, ~99% statement coverage, including:
- Unit tests per class (`Direction`, `Table`, `Robot`, command parsing).
- Integration tests running full command sequences through `Simulator`,
  including the three worked examples from the spec and additional edge
  cases (ignoring pre-`PLACE` commands, preventing falls off each edge,
  re-`PLACE`ing mid-sequence, and malformed/unknown commands).
- The same `test_data/*.txt` files are also runnable directly via `main.py`
  for a quick manual/CLI sanity check.

## Notes on requirements coverage

- Table is 5x5, origin `(0,0)` = south-west corner. ✅
- `PLACE X,Y,F` / `MOVE` / `LEFT` / `RIGHT` / `REPORT` all supported. ✅
- First valid command must be `PLACE`; everything before it is discarded. ✅
- Any move (including the initial `PLACE`) that would put the robot off
  the table is ignored/rejected, without crashing the run. ✅
- `PLACE` may be re-issued at any point, per the spec ("any sequence of
  commands may be issued ... including another PLACE command"). ✅
- Input read from a file path (arg) or stdin. ✅
