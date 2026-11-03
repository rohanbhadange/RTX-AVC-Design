#!/usr/bin/env python3
"""Generate searchable wiring diagrams and pin-level netlists from Wiring Studio snapshots.

No third-party dependencies. Outputs are deterministic and are not a substitute
for the native Wiring Studio rendered PNG screenshots or hardware validation.
"""
import argparse
import csv
import io
import json
import textwrap
from collections import defaultdict
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUTS = {
    "W-100": ROOT / "snapshots/wiring-studio/W-100_current.json",
    "W-101": ROOT / "snapshots/wiring-studio/W-101_current.json",
}
OUT = ROOT / "diagrams/generated"


def pin_label(component, cavity):
    if cavity is None:
        return ""
    for pin in component.get("pins", []):
        if pin.get("cavity") == cavity:
            return str(pin.get("label") or cavity)
    return str(cavity)


def make_csv(data):
    components = {p["name"]: p for p in data["sheet"]["components"]}
    buffer = io.StringIO()
    out = csv.writer(buffer, lineterminator="\n")
    out.writerow(["network", "source_component", "source_cavity", "source_pin",
                  "target_component", "target_cavity", "target_pin",
                  "wire_part", "twisted_pair_id", "wire_id"])
    edges = sorted(data["wires"], key=lambda w: (
        str(w.get("from", {}).get("component", "")),
        int(w.get("from", {}).get("cavity") or 0),
        str(w.get("to", {}).get("component", "")),
        int(w.get("to", {}).get("cavity") or 0),
        w.get("id", "")))
    for w in edges:
        src = w["from"]
        dst = w["to"]
        source = src["component"]
        target = dst["component"]
        out.writerow([
            w.get("networkName") or "",
            source, src.get("cavity") or "",
            pin_label(components.get(source, {}), src.get("cavity")),
            target, dst.get("cavity") or "",
            pin_label(components.get(target, {}), dst.get("cavity")),
            w.get("wirePartNumber") or "",
            (w.get("group") or {}).get("id", ""),
            w.get("id") or "",
        ])
    return buffer.getvalue()


def theme(name):
    n = name.upper()
    if any(t in n for t in ("BAT", "F0-", "F1-", "F2-", "PDB", "PM08", "HV-", "AS300", "BUCK", "UBEC")):
        return "#fff0eb", "#c46e54"
    if any(t in n for t in ("JETSON", "ORIN", "BRAINCHIP", "NVME", "M2-", "PIXHAWK", "COMPUTE")):
        return "#ebf2ff", "#547bb4"
    if any(t in n for t in ("ESC", "MOTOR", "PROPULSION", "PWM")):
        return "#fff4df", "#b58b3f"
    if any(t in n for t in ("ROBO", "GRIP", "CLAMP", "BRAKE")):
        return "#f5eefd", "#9070af"
    return "#e9f6f3", "#5d9c91"


def make_svg(data, view):
    layout = data["designLayout"] if view == "design" else data["wiringLayout"]
    nodes = layout["nodes"]
    raw_edges = layout["edges"]
    index = {n["name"]: n for n in nodes}
    coords_x = [n["x"] for n in nodes]
    coords_y = [n["y"] for n in nodes]
    for edge in raw_edges:
        for pt in edge.get("waypoints") or []:
            coords_x.append(pt["x"])
            coords_y.append(pt["y"])
    left, top = min(coords_x), min(coords_y)
    right, bottom = max(coords_x), max(coords_y)
    width = int(right - left + 450)
    height = int(bottom - top + 400)
    offset_x, offset_y = 210 - left, 240 - top

    def point(x, y):
        return f"{x + offset_x:.0f},{y + offset_y:.0f}"

    grouped = defaultdict(list)
    for edge in raw_edges:
        # Group multi-conductor links: retain exact individual pin mapping in CSV.
        key = (edge.get("from"), edge.get("to"))
        grouped[key].append(edge)

    title = f"{data['sheet']['name']} — {view.capitalize()} view"
    sub = (f"Generated from {data['snapshotDate']} checked-in Wiring Studio "
           "snapshot. Logical connectivity only; not a fabrication drawing.")

    s = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
        '<style>text{font-family:Arial,Helvetica,sans-serif} .edge{fill:none;stroke:#77869c;stroke-width:2.3;opacity:.55} .node{stroke-width:1.6} .title{font-weight:700;fill:#1c2d41;font-size:30px} .sub{fill:#5d6f83;font-size:16px} .name{fill:#172b3f;font-size:15px;font-weight:600} .meta{fill:#52657c;font-size:12px} .count{font-size:13px;fill:#34495e}</style>',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
        f'<text class="title" x="44" y="60">{escape(title)}</text>',
        f'<text class="sub" x="44" y="91">{escape(sub)}</text>',
    ]
    # Draw routes under the labeled component boxes. Labels/coordinates are
    # copied from the source layout; connections are not electrically inferred.
    for (a, b), edges in sorted(grouped.items(), key=lambda p: str(p[0])):
        if a not in index or b not in index:
            continue
        first = edges[0]
        paths = [point(index[a]["x"], index[a]["y"])]
        if view == "design":
            paths.extend(point(p["x"], p["y"]) for p in (first.get("waypoints") or []))
        paths.append(point(index[b]["x"], index[b]["y"]))
        info = f"{a} → {b}: {len(edges)} " + ("cable(s)" if view == "design" else "wire(s)")
        s.append(f'<polyline class="edge" points="{" ".join(paths)}"><title>{escape(info)}</title></polyline>')
        if len(edges) > 1:
            mx = (index[a]["x"] + index[b]["x"]) / 2 + offset_x
            my = (index[a]["y"] + index[b]["y"]) / 2 + offset_y
            s.append(f'<text class="count" x="{mx:.0f}" y="{my - 7:.0f}">×{len(edges)}</text>')

    components = {p["name"]: p for p in data["sheet"]["components"]}
    box_w, box_h = (166, 68) if view == "design" else (172, 78)
    for n in nodes:
        x, y = n["x"] + offset_x - box_w / 2, n["y"] + offset_y - box_h / 2
        fill, stroke = theme(n["name"])
        p = components.get(n["name"], {})
        part = p.get("partNumber", "")
        s.append(f'<g><title>{escape(n["name"])} | {escape(part)}</title>')
        s.append(f'<rect class="node" x="{x:.0f}" y="{y:.0f}" width="{box_w}" height="{box_h}" rx="7" fill="{fill}" stroke="{stroke}"/>')
        lines = textwrap.wrap(n["name"], width=21, break_long_words=True, break_on_hyphens=True)[:2]
        for i, line in enumerate(lines):
            s.append(f'<text class="name" x="{x + 8:.0f}" y="{y + 23 + i * 17:.0f}">{escape(line)}</text>')
        if part:
            s.append(f'<text class="meta" x="{x + 8:.0f}" y="{y + box_h - 8:.0f}">{escape(part[:23])}</text>')
        s.append('</g>')
    s.append(f'<text class="sub" x="44" y="{height - 37}">Source: Wiring Studio | {len(nodes)} components | {len(raw_edges)} drawn connections | full pin-level nets in accompanying CSV</text>')
    s.append('</svg>\n')
    return "\n".join(s)


def outputs():
    for name, source in INPUTS.items():
        data = json.loads(source.read_text(encoding="utf-8"))
        yield OUT / f"{name}-netlist.csv", make_csv(data)
        for view in ("design", "wiring"):
            yield OUT / f"{name}-{view}.svg", make_svg(data, view)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Fail if committed generated outputs differ from snapshots")
    opts = parser.parse_args()
    if not opts.check:
        OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for path, content in outputs():
        if opts.check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(str(path.relative_to(ROOT)))
        else:
            path.write_text(content, encoding="utf-8")
            print(f"Wrote {path.relative_to(ROOT)}")
    if stale:
        parser.error("Stale wiring outputs: " + ", ".join(stale)
                     + ". Run python3 scripts/build_wiring_diagrams.py")
    if opts.check:
        print("Generated wiring diagrams and netlists match committed snapshots.")


if __name__ == "__main__":
    main()
