# Phase 5: Validation & operational guardrails

## Logging quality

| Check | What to look for |
|-------|-------------------|
| **Timestamps** | Stable monotonic behavior; beware clock jumps vs adapter timestamp source. |
| **Frame floods** | Log size limits; throttle filters in SavvyCAN / `candump` before multi-hour pulls. |
| **Drop indications** | Some stacks report RX drops; correlate with baud mismatch or EMI. |

Keep one **golden baseline** (`baseline_idle`) per vehicle state for regressions against new firmware / harness changes.

## File discipline

Suggested pattern (aligns with [ECU_MAPPING_WORKFLOW.md](ECU_MAPPING_WORKFLOW.md)):

```
captures/<vehicle-or-vin>/<YYYYMMDD>_<bus>_<action>_<attempt>.ext
```

Version **DBC files** beside logs (`dbc/v0_vehicle_date.dbc`).

## Transmit / fuzz / injection policy

Follow the plan directive: **avoid active transmits** until:

1. Passive mapping documents candidate IDs safely, and  
2. You validate on **isolated harness** away from propulsion-critical buses.

Bench testing still requires correct termination and bitrate.

## Authorization

Only analyse buses on systems you **own** or have **explicit written authorization** to test. Passive listening can still violate policy or contracts if misapplied.
