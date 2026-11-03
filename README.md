# RTX AVC — Design Control

Engineering design, electrical integration, and revision history for the RTX Autonomous Vehicle Challenge UAV.

## Source of truth
- **Native CAD:** working SolidWorks assembly, with exported/reviewed releases committed when available. Do not infer CAD geometry from wiring diagrams.
- **Electrical:** Wiring Studio project `RTX AVC | R3.5 INTEGRATION SELECTED — engineering test HOLD`, W-100 (integrated wiring) and separate W-101 power-tree project. Wiring Studio is a live working model, *not* automatically synchronized to GitHub.
- **Decisions:** `docs/decisions/` contains date-stamped architecture decisions, alternatives, evidence, changes, and acceptance tests.
- **Validation:** passing a schematic check is not flight qualification. Record hardware/bench evidence before marking a design validated.

## Workflow
1. Inspect the latest physical/documentation baseline before changing interfaces.
2. Record the requirement, alternatives, and decision in a dated design note.
3. Change the smallest necessary parts of the live tool and preserve unrelated interfaces.
4. Compare connected-component counts, wiring nets, and design-rule checks before/after.
5. Commit a change record with the tested/unverified status. Use pull requests for larger revisions.
6. Attach exported drawings or CAD screenshots and update mass, connector, cable-length and packaging evidence as it becomes available.

## Current integration decisions
- [ADR-0001: SiK 915 MHz radio on Jetson USB](docs/decisions/ADR-0001-sik-jetson-usb.md) — replaces Pixhawk TELEM1 radio harness; keeps the R81 safety receiver separate.
- BrainChip AKD1000 B+M 2260 via Delock 64343 in Jetson E-key; SSD remains in the M-key socket (documented in the live W-100 component records).

> Design statuses are deliberately distinct: *proposed*, *schematic-integrated*, *mechanically packaged*, *bench-validated*, and *flight-validated*. Never promote a status without evidence.
