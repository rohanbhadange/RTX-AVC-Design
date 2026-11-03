# RTX AVC R3.5 — electrical architecture

**Based on:** live Wiring Studio W-100 integrated wiring and W-101 power tree, captured 2026-11-02.  
**Status:** schematic-integrated, engineering test HOLD.

This page is a **functional block-diagram companion** to the pin-level/native schematics in [Wiring diagrams](README.md). It is deliberately simplified: a line may represent a cable assembly, integrated connector, or a bus with multiple wires. **Do not wire the aircraft from this page alone.**

## 1. Main power distribution

```mermaid
flowchart LR
  BAT["6S LiPo"] --> F0["F0 main MRBF fuse<br/>125 A provisional"]
  F0 --> MAIN["AS300 main removable disconnect"]
  MAIN --> PM["PM08-CAN current sense<br/>dual 5.3 V BECs"]
  PM --> BUS["Monitored 6S junction"]
  PM -. "BEC1/BEC2 + CAN" .-> FC["Pixhawk 6X"]

  BUS --> F1["F1 10 A compute fuse"]
  F1 --> CSW["Compute positive switch"]
  CSW --> CD["Compute distribution"]
  CD --> BUCK["Holybro UBEC 15026"]
  BUCK --> JET["Jetson Orin NX carrier"]

  BUS --> MARM["AS300 motion arming disconnect"]
  MARM --> PDB["Holybro 300 A PDB"]
  PDB --> ESC["4 × XRotor 40 A ESC"]
  ESC --> MOT["4 × MN4014 motors"]
  PDB --> F2["F2 10 A gripper fuse"]
  F2 --> GBUCK["Pololu 12 V gripper buck"]
  GBUCK --> ROBO["RoboClaw 2×7A and VClamp"]
```

The Pixhawk and compute subsystems are powered independently of the motion arming plug. Fuse values and terminations are provisional in the live model. W-101 is the power-tree detail, not an additional physical PDB.

## 2. Jetson interfaces and communications

```mermaid
flowchart LR
  J["Holybro Jetson Orin carrier"]
  J -- "USB 3.2 A1" --> D["Intel RealSense D455"]
  J -- "USB 3.2 A2<br/>USB-A to Micro-B, data + 5 V" --> S["Holybro SiK V3<br/>915 MHz 100 mW"]
  S -. "915 MHz link" .-> G["Leader's ground radio"]
  J -- "Internal USB 2.0 GH5<br/>5 V, D-, D+, GND, shield" --> UA["Passive GH5 to USB-A female adapter"]
  UA -- "Factory USB cable" --> ISO["IMC614 USB isolator"]
  ISO -- "Factory USB cable" --> RC["RoboClaw 2×7A"]
  J -- "CSI FFC" --> CAM["IMX219 camera"]
  J -- "I²C + GPIO + 3.3 V/5 V rails" --> NFC["PN7160 NFC and local interface"]
  J -- "M.2 Key M PCIe x4" --> SSD["NVMe SSD"]
  J -- "M.2 Key E to Delock 64343 PCIe x1" --> AK["BrainChip AKD1000 B+M 2260"]
```

**SiK change:** The onboard SiK receives all power/data via one Jetson USB cable, not Pixhawk TELEM1. Holybro identifies **Micro-USB on the V3 100 mW** model; the 1 W model uses USB-C. The team requirement of USB-C is overridden by the actual selected 100 mW product specification unless a different purchased revision is confirmed. Keep antenna accessible, clear of the carbon structure, and adjustable for arena-range testing.

## 3. Flight-control and gripper safety interfaces

```mermaid
flowchart LR
  PM["PM08 BEC power"] --> FC["Pixhawk 6X"]
  R81["R81 RC SBUS receiver"] -->|"Independent RC-IN"| FC
  FLOW["H-Flow DroneCAN"] -->|"CAN2"| FC
  FC -->|"MAIN PWM and grounds"| ESC["4 × ESCs"]
  FC -. "No TELEM1 SiK harness" .- SPARE["TELEM1 spare"]

  J["Jetson USB2 (via isolator)"] --> RC["RoboClaw 2×7A"]
  RC -->|"Motor power + encoder"| M["Gripper Pololu 4845"]
  HOME["Home NC switch"] --> RC
  FAR["Far-travel switch"] --> RC
  RC -->|"S3 clamp control"| VC["BasicMicro VClamp"]
  VC --> BR["2 Ω / 50 W braking resistor"]
```

**Safety:** The R81-to-Pixhawk connection remains the pilot override/kill path independent of the Jetson/SiK communications link. This diagram represents the present RoboClaw controller in W-100, not a completed transition to the proposed Pico 2 / DRV8874 controller.

## Validation and tracing

- See [ADR-0001](../docs/decisions/ADR-0001-sik-jetson-usb.md) and [SiK USB change record](../docs/changes/2026-11-02-sik-usb.md).
- Refer to [W-100 pin-level netlist CSV](generated/W-100-netlist.csv) and [W-101 power netlist CSV](generated/W-101-netlist.csv) for exact modeled endpoints.
- Refer to [the native Wiring Studio PNGs](README.md) for routing and physical locations.
- Do not treat current status as bench/flight validation. Unassigned harness lengths, contact sizes, and physical mounting details remain incomplete.
