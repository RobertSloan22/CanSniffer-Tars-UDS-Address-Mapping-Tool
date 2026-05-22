# Phase 3: ECU function mapping workflow

Structured reverse-engineering of “advanced ECU functionality” means **changing one stimulus at a time** and correlating CAN/CAN-FD changes.

## 1. Build a capture matrix

Copy [templates/capture_matrix.csv](../templates/capture_matrix.csv) per vehicle project and fill:

- Function (e.g. “Driver door unlock”)
- Precondition (gear, speed, IGN state)
- Action (exact button/order)
- Log filename exported from SavvyCAN

## 2. Capture protocol per row

For each matrix row:

1. **Park** identical preconditions (“IGN on, parked, drivers door closed”).
2. Start SavvyCAN **logging** immediately before stimulus.
3. Wait **quiet period** (~5–10 s).
4. Apply **single** stimulus once (repeat 3× for confidence).
5. Wait **recovery** period (traffic returns to baseline).
6. Stop log → save with planned filename.

Repeating three times separates random traffic from causal IDs.

## 3. SavvyCAN analysis tips

- **Filter by bus** when dual-channel adapter or multiple captures.
- **Filter by arbitration ID / extended ID**.
- Sort by **changing data** columns; FD frames highlight 64-byte changes.
- **Frame info / graphs**: watch bytes that correlate with actuator state.
- Load partial **DBC early**—even wrong scaling helps grouping signals.

Exports for offline Python scripts:

- Use a format scripts here can ingest (SavvyCAN can export to common text formats depending on version; **ASC**/`candump`-like text is easiest for `cantools` + parsers).

See [SavvyCAN](https://savvycan.com/).

## 4. Turning hypotheses into DBC

1. Identify candidate IDs (narrow with diff between baseline and action captures).
2. Add message + raw signals (`SIG …` with placeholder scale/offset).
3. Decode with [`scripts/decode_sample.py`](../scripts/decode_sample.py) pattern → refine bit width and endian until physical values “make sense”.

## 5. Operational guardrails

- No **injection** until passive mapping proves TX addresses and payloads on an isolated bench harness.
- Only authorized vehicles/systems—see root [README](../README.md).
