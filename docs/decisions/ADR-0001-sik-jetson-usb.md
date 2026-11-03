# ADR-0001 — SiK 915 MHz radio on Jetson USB

- **Date:** 2026-11-02
- **Requirement source:** Abhi, 2026-10-27, 5:22 PM (team communications/LLM wiring request)
- **Status:** Approved architecture for schematic integration; bench and packaging validation pending
- **Affected baseline:** Wiring Studio `RTX AVC | R3.5 INTEGRATION SELECTED — engineering test HOLD`, sheet W-100; Holybro Pixhawk Jetson baseboard SKU 11072

## Requirement
Exactly one onboard Holybro SiK Telemetry Radio V3, 915 MHz, 100 mW; other radio stays on ground with leader. Radio power and data through **one USB cable directly to the Jetson**, nominal 5 V, 100 mA TX/25 mA RX; no separate power or Pixhawk TELEM UART harness. Radio body 28 x 53 x 10.7 mm without antenna; 23.5 g with antenna. RP-SMA 2 dBi antenna must have clear RF placement and remain adjustable until arena testing. Cable must be accessible for swapping/flashing without disassembling frame. Team observed no loss at 51 ft on prior drone; this is **not** an arena-range qualification.

## Research and discrepancy resolved
- Holybro official V3 product page lists **Micro-USB on 100 mW and 500 mW**, and **USB-C on 1 W**. It includes a Type-C adapter cable with the Micro-USB variant. The request's “USB-C on radio” conflicts with the maker specification. Use **USB-A host → Micro-USB B radio**, with an approved adapter only if the *purchased* unit physically differs; do not procure a bare USB-C-to-C cable based on the note alone.
- Holybro 11072 offers **2 USB 3.2 Type-A host ports (1.5 A each)** and **2 USB 2.0 host ports (5-pin JST-GH, 1.0 A each)**. Manufacturer USB2 GH pin map: 1 VBUS +5 V; 2 D−; 3 D+; 4 GND; 5 shield. Source: https://docs.holybro.com/autopilot/pixhawk-baseboards/pixhawk-jetson-baseboard/ports-pinout
- Radio manufacturer: https://holybro.com/products/sik-telemetry-radio-v3 . Holybro states 5 V power through USB, 100 mA TX/25 mA RX, size/weight, RP-SMA female with supplied antenna and USB/UART bridge on radio.

## Decision / interfaces
1. **Jetson USB3 Type-A #1 → Intel D455**, unchanged.
2. **Jetson USB3 Type-A #2 → one 100 mW SiK radio** using a short, shielded, removable USB-A-to-Micro-B cable. Single cable carries power and data; no Pixhawk TELEM1 connection or separate regulator.
3. **Jetson internal USB2 host #1 JST-GH 5-pin → short captive 5-wire adapter → USB-A female socket → factory USB cable → BasicMicro IMC614 USB isolator → RoboClaw Micro-B**. Implement actual GH VBUS/D−/D+/GND/shield mapping; no new USB hub. Follow USB2 twisted D+/D−, controlled pair geometry and short cable routing. Isolator logic and host side powered by internal host (1 A limit), subject to product data. This retains existing gripper controller, which is *not* a decision that RoboClaw remains the final motion architecture.
4. Preserve **RadioMaster R81 SBUS directly connected to Pixhawk RC-IN**, independently powered through Pixhawk. SiK/Jetson USB link is *not* the emergency stop/RC safety path.
5. Pixhawk TELEM1 is **unused/reserved**, and must not be shown connected to SiK.
6. Mount radio at edge of frame with accessible Micro-USB connector and unblocked removable RP-SMA antenna, with mounting clearance for cable connector, antenna swing/strain relief, vibration protection, RF separation from HV/ESC harnesses, and ability to reposition before arena tests.

## Software interface
The SiK USB-UART bridge should enumerate under Linux (often `/dev/ttyUSB*`; never hardcode USB index). Use `/dev/serial/by-id/` or persistent udev matching. Assign radio to the LLM/comms process, not to Pixhawk TELEM1. Radio is a transparent serial link, **not a high-bandwidth native video link**. Ground unit and onboard radio must use compatible radio settings/firmware. Record baud, NETID, FHSS/channel, serial protocol and application framing in test log. Confirm the intended leader-to-drone data protocol and no conflict with flight control.

## Acceptance tests / evidence needed
- USB port enumeration and proper device assignment with D455 + RoboClaw simultaneously active.
- SiK transmits/receives via Jetson port: record `lsusb`, `udevadm info`, `/dev/serial/by-id`, TX/RX power and connector fit.
- RoboClaw control and USB isolator enumerate through internal USB2 GH port. Check actual USB2 custom adapter continuity, correct polarity, isolation, motor-off backfeed, USB EMI and fault behavior.
- Test hot-plug swap/flash access without frame disassembly; strain relief, cable retention, and antenna RF line of sight.
- Arena-range test to confirm signal at required maximum distances and orientations; 51 ft previous-team result is provisional.
- Verify that R81→Pixhawk kill/failsafe retains control while Jetson or SiK is powered off.
- Capture final component photographs, actual cable lengths, secured routing, CAD weight/CG and mounting envelopes.

## Change boundary
No modifications to flight-controller flight-safety path, main power tree, battery, PM08/PDB, ESCs, motors, BrainChip, SSD, cameras, NFC, or H-Flow. Existing R3.5 incomplete harness design-rule checks remain project issues; update their count after the topology change.

## Open items
Physical purchased SiK connector/USB cable, USB2-A GH adapter construction, exact IMC614 USB compatibility, mechanical radio/antenna location and antenna-range performance. Open items are actionable tests and not claims of demonstrated flight reliability.
