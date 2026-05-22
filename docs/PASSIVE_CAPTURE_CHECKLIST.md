# Phase 2: Passive capture baseline

Goal: sniff safely and get comparable logs **before** trying to decode or transmit.

## Listen-only where possible

- In SavvyCAN’s connection settings, enable **listen-only** / passive mode when the hardware/driver exposes it ([SavvyCAN connection window](https://savvycan.com/docs/connectionwindow.html)).
- For GVRET-style serial devices listen-only avoids ACK-ing traffic; QT SerialBus path depends on backend—always prefer vendor-provided passive mode notes.

If listen-only is not available:

- Minimize accidental TX in the UI (don't use fuzz/send until mappings are validated on a bench).

## Physical layer

| Check | Notes |
|------|-------|
| **CAN-H / CAN-L** | Match OBD breakout or vehicle pinout (do not swap). |
| **Ground** | Use a stable ground reference compatible with isolated adapter specs. |
| **Termination** | 120 Ω typically at **two** bus ends—**do not over-terminate** with an extra terminator on short lab harnesses unless bus is unloaded. Adapter may have selectable internal 120 Ω—follow [Pibiger manual / termination docs](https://docs.pibiger-tech.com/home/usb-to-can-fd-series/savvycanfd/quick-start-guide). |
| **Isolation** | Pibiger advertises isolation—still avoid hot-plugging HS CAN with engine critical systems without procedure. |

## Bitrate sanity

Wrong bitrate → garbage or silence.

1. Obtain **CAN nominal** bitrate (often 125k / 250k / 500k automotive).
2. If bus is **CAN FD**, set nominal + **data phase** bitrate from OEM or reverse-engineering assumptions; wrong data rate misses FD payloads.
3. After connection, verify **steady frame timestamps**—no avalanche of BUS-OFF/error frames in tools that show them.

## Baseline captures

Perform before function tests:

| Session | Duration | Condition |
|---------|----------|-----------|
| `baseline_idle` | 5–10 min | IGN on, accessories stable, minimal driver input |
| `baseline_vehicle_off` | 1–2 min | Key off CAN sleep edge (some buses quiessce) |

**File naming suggestion:**  
`YYYYMMDD_vehicle_bus_function_state.savvylog` or export to ASC/CSV from SavvyCAN consistently.

## Readiness checklist

- [ ] Driver + SavvyCAN connect without errors at desk (USB).
- [ ] Correct nominal bitrate + FD data rate selected for target bus (document in session notes).
- [ ] Listen-only on if applicable.
- [ ] Harness + termination validated.
- [ ] Baseline logs saved before ECU-mapping matrix.

Proceed to [ECU_MAPPING_WORKFLOW.md](ECU_MAPPING_WORKFLOW.md).
