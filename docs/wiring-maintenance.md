# Wiring diagram publishing and synchronization policy

**Applies to:** W-100 integrated vehicle wiring; W-101 power-tree view; future revisioned sheets and their GitHub diagrams.

## Data ownership

1. The **live Wiring Studio project** remains the editable schematic and harness working source of truth.
2. \`snapshots/wiring-studio/W-100_current.json\` and \`W-101_current.json\` are the latest **committed** representations, including components, pin definitions, wires, cables, both canvas layouts, and DRC status.
3. \`diagrams/wiring-studio/*.png\` are original native Wiring Studio-rendered screenshots; \`diagrams/generated/*.svg\` and \`*.csv\` are generated from the committed JSON snapshots.
4. \`diagrams/architecture.md\` contains human-readable architecture decisions, so it must be reviewed when topology changes.

## Required publication process on **every** wiring change

1. Read the current live sheet and DRC first. Check the desired change against the exact affected pins and branches.
2. Edit the live Wiring Studio model, preserving unaffected connections. Run DRC after edits, note any newly introduced violations.
3. **In the same change:** export/write the revised complete \`W-100_current.json\` and/or \`W-101_current.json\`. Preserve date/revision historical snapshots for significant changes; never overwrite the original dated archive.
4. Render both affected Wiring Studio **design** and **wiring** views as PNGs to \`diagrams/wiring-studio/\`, replacing the previous images on GitHub.
5. Run \`python3 scripts/build_wiring_diagrams.py\` to refresh \`diagrams/generated/\` locally; **or** allow the GitHub Actions [wiring-diagrams.yml](../.github/workflows/wiring-diagrams.yml) workflow to regenerate the derived SVG diagrams and pin-to-pin CSV automatically after the current JSON is committed.
6. Review and update [electrical architecture](../diagrams/architecture.md), affected ADRs, dates, DRC counts, component counts, and the dated change record.
7. Commit these related artifacts together, or link the follow-up generated-artifact commit. Record what changed, why, and validation status. Never mislabel logical schematic completion as physical/flight validation.
8. Confirm the PNGs and derived SVG/CSV in GitHub reflect the expected change. Attach a bench test and photograph to the relevant issue before marking it validated.

## Automation scope and limitation

The GitHub Action listens for updates to the \`*_current.json\` snapshots or the generator script in **GitHub**, and refreshes the derived SVG and pin-netlist CSV. It does **not** authenticate to, subscribe to, or poll Wiring Studio. **A change made directly in Wiring Studio will not appear in GitHub until someone explicitly exports/commits the updated live state.** Native Wiring Studio PNGs likewise require a new capture.

When ChatGPT edits wiring in future project chats, the required procedure is to do the Wiring Studio change and the GitHub snapshot/screenshots/change log **during the same task**, rather than deferring documentation.

## Naming

- Stable latest snapshots: \`W-100_current.json\`, \`W-101_current.json\`.
- Historical checkpoints: \`W-100_Rx.y_YYYY-MM-DD.json\`, likewise W-101.
- Latest native diagrams: \`diagrams/wiring-studio/W-100-wiring.png\`, \`W-100-design.png\`, and W-101 equivalents.
- Regenerable diagrams and netlists: \`diagrams/generated/W-100-wiring.svg\`, \`W-100-design.svg\`, \`W-100-netlist.csv\`, and W-101 equivalents.
- Change notes: \`docs/changes/YYYY-MM-DD-short-description.md\`.

The separate W-101 sheet depicts a power-tree subset of W-100. Do not sum component quantities from both snapshots or BOMs.
