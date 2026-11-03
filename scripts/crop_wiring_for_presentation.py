#!/usr/bin/env python3
"""Produce slide-friendly PNG crops of native Wiring Studio screenshots.

The cropped contents are never redrawn or fabricated. Crop boxes are recorded
in coordinates of observed, representative preview dimensions, and scaled to
the full-resolution, version-controlled native PNGs.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "diagrams" / "wiring-studio"
OUT = ROOT / "diagrams" / "presentation"

# (output, source, reference_preview_size, preview_crop_box)
# Regions observed in the 2026-11-03 live Studio renders.
CROPS = [
    ("01-power-distribution.png", "W-101-design.png", (2047, 1918), (0, 0, 1830, 1080)),
    ("02-compute-brainchip.png", "W-100-wiring.png", (1821, 2048), (555, 115, 1785, 710)),
    ("03-comms-sensors.png", "W-100-design.png", (1600, 1486), (725, 10, 1565, 580)),
    ("04-propulsion.png", "W-100-wiring.png", (1821, 2048), (580, 845, 1510, 1625)),
    ("05-gripper-control.png", "W-100-wiring.png", (1821, 2048), (715, 1605, 1775, 2048)),
]


def crop_image(source_path, reference_size, coordinates):
    image = Image.open(source_path).convert("RGB")
    w, h = image.size
    ref_w, ref_h = reference_size
    x1, y1, x2, y2 = coordinates
    box = (
        max(0, round(x1 * w / ref_w)),
        max(0, round(y1 * h / ref_h)),
        min(w, round(x2 * w / ref_w)),
        min(h, round(y2 * h / ref_h)),
    )
    region = image.crop(box)
    return ImageOps.expand(region, border=36, fill="white"), box


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for output_name, source_name, reference, box in CROPS:
        source = SRC / source_name
        if not source.exists():
            raise SystemExit(f"Missing source PNG: {source}")
        image, source_box = crop_image(source, reference, box)
        destination = OUT / output_name
        image.save(destination, optimize=True)
        print(f"{destination.relative_to(ROOT)} {image.size} cropped {source_box}")


if __name__ == "__main__":
    main()
