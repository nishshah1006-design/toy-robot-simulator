# Command Circuit

How one line of input becomes either a `REPORT` line, an ignored-error
message, or a silent no-op — traced through every class in
`robot_simulator/`, down to the single gate that enforces the spec's core
rule: never fall off the table.

![Diagram: main.py sends each line to Simulator, which parses it; malformed lines short-circuit to stderr, valid commands go to Robot; a detail view shows that only PLACE and MOVE pass through Robot's is_on_table gate, which either updates state or silently keeps the previous state.](docs/command-circuit.svg)

Every valid line travels `main.py → Simulator → Robot` and back; a
malformed line short-circuits straight to stderr without ever reaching
`Robot`. Only `PLACE`/`MOVE` pass through the `is_on_table` gate shown in
the inset — the one check that enforces "must be prevented from falling
to destruction."

Maps to `main.py` and `robot_simulator/{simulator,commands,robot,table,direction}.py`.
