<!--
SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
SPDX-License-Identifier: GPL-3.0-only
-->

# Lessons Learned: USB HID Power Device on CircuitPython

This document captures everything learned during the development and testing of
the CircuitPython HID Power Device library. It is intended to inform a future
C/C++ rewrite targeting RP2040 with TinyUSB directly.

## Goal

Make an RP2040 board (Waveshare RP2040-One) appear as a USB UPS to a Synology
NAS (DSM 7.x), so DSM's built-in UPS monitoring triggers safe shutdown when AC
power is lost. Secondary targets: macOS, Linux/NUT, Windows.

## What works

### Descriptor generation

The HID report descriptor we generate is correct and fully parsed by:
- macOS (System Information > Power > UPS)
- Linux kernel's hid-generic driver (creates hiddev + hidraw)
- NUT's usbhid-ups driver on Synology (found all 32 HID objects)

The descriptor follows the USB HID Power Device Usage Tables spec (Release 1.1,
May 29, 2020). Key structure:

```
USAGE_PAGE(0x84 Power Device) > USAGE(0x04 UPS) > COLLECTION(Application)
  USAGE(0x24 PowerSummary) > COLLECTION(Logical)
    [regular reports: RemainingCapacity, RunTimeToEmpty, etc.]
    USAGE(0x02 PresentStatus) > COLLECTION(Logical)
      [14 boolean bits + 2 padding]
    END_COLLECTION
  END_COLLECTION
END_COLLECTION
```

### HID item encoding

HID short items use sign-extended values. The encoding MUST distinguish between
signed items (LOGICAL_MINIMUM, LOGICAL_MAXIMUM) and unsigned items (everything
else: USAGE_PAGE, USAGE, REPORT_ID, REPORT_SIZE, INPUT, FEATURE, etc.).

- **Unsigned**: 0x84 fits in 1 byte (`05 84`). Using signed encoding produces
  2 bytes (`06 84 00`) because 0x84 > 127. Both are valid HID, but some parsers
  (NUT's old libusb code) only handle the 1-byte form correctly.
- **Signed**: LOGICAL_MAX(255) MUST be 2 bytes (`26 FF 00`) to avoid being
  interpreted as -1. LOGICAL_MAX(65535) MUST be 4 bytes (`27 FF FF 00 00`).

### Minimum viable report set

The minimum for host UPS recognition is PresentStatus + RemainingCapacity.
Adding RunTimeToEmpty gives the host an estimated runtime. The existing
circuitpython-hid-ups project used reports 7, 12, 13 (PresentStatus,
RemainingCapacity, RunTimeToEmpty) and that set works on macOS.

### Report classification (INPUT vs FEATURE)

Per spec Tables 2/3:
- 5 reports have INPUT (sent via interrupt endpoint): PresentStatus(7),
  RemainingCapacity(12), RunTimeToEmpty(13), AverageTimeToEmpty(28), Voltage(11)
- All other reports are FEATURE-only (read via GET_REPORT control transfer)
- AudibleAlarmControl and RemainingTimeLimit are FEATURE-only per spec. The C++
  HIDPowerDevice library makes them INPUT+FEATURE, but NUT accesses both via
  FEATURE, so following the spec has no compatibility impact.

## What doesn't work (CircuitPython limitations)

### GET_REPORT returns zeros

CircuitPython's `usb_hid.Device.send_report()` calls `tud_hid_report()` which
sends data via the interrupt IN endpoint. It does NOT populate
`in_report_buffers` (the buffers used by `tud_hid_get_report_cb` for
GET_REPORT responses).

Source: `circuitpython/shared-module/usb_hid/Device.c:255-276`

This means:
- NUT's initial device probe (which uses GET_REPORT) always gets zeros
- The device appears to have 0% battery, no AC, 0s runtime
- NUT reports status "OB" (On Battery) with no useful data

**This is the primary blocker for NUT/Synology support.**

In a C/C++ rewrite with TinyUSB directly, implement `tud_hid_get_report_cb` to
return actual current values for each report ID. This is straightforward — the
callback receives the report_id and report_type, and you fill the buffer with
the current values.

### Interrupt reports not received by NUT

During 15-second test runs, NUT's `libusb_get_interrupt` always timed out with
0 HID objects received. CircuitPython's `send_report()` appeared to succeed on
the device side, but NUT never received the interrupt data.

This may be related to:
- Timing: code.py sends every 10s, NUT polls with 250ms timeout
- The kernel driver detach/libusb claim transition
- CircuitPython's TinyUSB integration

In the C/C++ rewrite, this should work naturally since TinyUSB handles interrupt
IN transfers directly. Send data frequently (every 1-2 seconds) to ensure the
host catches it within its poll window.

### No feature_report_lengths parameter

CircuitPython's `usb_hid.Device` constructor has no `feature_report_lengths`
parameter. FEATURE-only reports are in the descriptor for host discovery, but
GET_REPORT for them returns STALL (report ID not in `report_ids`).

In the C/C++ rewrite, TinyUSB's `tud_hid_get_report_cb` handles ALL report
types (INPUT, FEATURE) regardless — just return data for any valid report_id.

### send_report() blocks or raises OSError

`send_report()` busy-loops in CircuitPython when the interrupt endpoint is full.
If the host isn't reading (kernel driver not polling, or endpoint not drained),
it blocks indefinitely. Sometimes raises `OSError: USB busy` instead.

The C/C++ rewrite can use non-blocking TinyUSB calls and handle the busy case
explicitly.

## NUT compatibility (critical for Synology)

### Interface 0 requirement (old NUT)

**This is the second major finding.** NUT's `libusb0.c` (used by Synology DSM
7.x with NUT 0.41) hardcodes `wIndex=0` in the GET_DESCRIPTOR control transfer
for the HID descriptor. If the HID interface is not interface 0, NUT gets
"Broken pipe" (USB STALL) and skips the device.

Source: GitHub issue abratchik/HIDPowerDevice#1

The fix was merged into NUT master (PR #1044) and is available in NUT >= 2.8.0.
A second fix for `libusb1.c` (config descriptor index bug) was merged post-2.8.1.

**Synology DSM 7.x ships NUT 0.41 — far too old for either fix.**

Solution: HID MUST be interface 0. On a composite USB device, this means HID
must be the FIRST interface in the USB configuration descriptor.

For the C/C++ rewrite with TinyUSB:
- Configure TinyUSB's interface order so HID comes first
- Or make HID the only interface (no CDC serial, no MSC)
- For development, use a GPIO pin or button to conditionally enable CDC

On CircuitPython, we achieved this by disabling CDC, MIDI, and mass storage:
```python
usb_cdc.disable()
usb_midi.disable()
storage.disable_usb_drive()
```

### VID/PID and nut-scanner

`nut-scanner -U` only finds devices whose VID:PID are in NUT's built-in device
table. Our Waveshare RP2040-One (2e8a:103a) is not in the table, so
`nut-scanner` never finds it. The `usbhid-ups` driver with explicit
`vendorid`/`productid` and `explore` flag DOES work.

For Synology DSM's auto-detection (Control Panel > Hardware & Power > UPS), the
device likely needs to match a known VID:PID. Options:
- Spoof a known UPS VID:PID (e.g., Eaton 0x0463, CyberPower 0x0764)
- Accept manual NUT configuration via `/usr/syno/etc/ups/ups.conf`
- NUT 2.8.3+ has `subdriver=arduino` option for explicit configuration

### NUT subdriver

NUT uses subdrivers for vendor-specific quirks. With `explore` mode, NUT uses
the generic "EXPLORE HID 0.1" subdriver which reads all HID objects. For
production use, the `arduino` subdriver (available in NUT 2.8.0+) maps Arduino
HID Power Device objects to NUT variables.

## USB descriptor details (for the C/C++ rewrite)

### Tested descriptor (194 bytes, 3 reports)

This exact descriptor was successfully parsed by NUT on Synology:

```
05 84 09 04 a1 01 09 24 a1 02 75 08 95 01 15 00
26 ff 00 05 85 25 64 85 0c 09 66 81 a3 09 66 b1
a3 75 10 27 ff ff 00 00 66 01 10 55 00 85 0d 09
68 81 a3 09 68 b1 a3 05 84 09 02 a1 02 85 07 75
01 15 00 25 01 05 85 09 44 81 a3 09 44 b1 a3 09
45 81 a3 09 45 b1 a3 09 d0 81 a3 09 d0 b1 a3 09
d1 81 a3 09 d1 b1 a3 09 42 81 a3 09 42 b1 a3 09
43 81 a2 09 43 b1 a2 09 4b 81 a3 09 4b b1 a3 09
db 81 a3 09 db b1 a3 09 46 81 a3 09 46 b1 a3 09
47 81 a3 09 47 b1 a3 05 84 09 68 81 a2 09 68 b1
a2 09 69 81 a3 09 69 b1 a3 09 73 81 a3 09 73 b1
a3 09 65 81 a3 09 65 b1 a3 95 02 81 01 b1 01 c0
c0 c0
```

### usb_hid.Device parameters that worked

```python
usb_hid.Device(
    report_descriptor=bytes(descriptor),
    usage_page=0x84,
    usage=0x04,
    report_ids=(12, 13, 7),       # RemainingCapacity, RunTimeToEmpty, PresentStatus
    in_report_lengths=(1, 2, 2),  # 1 byte, 2 bytes, 2 bytes
    out_report_lengths=(0, 0, 0),
)
```

### PresentStatus bit layout (report ID 7, 2 bytes)

```
Bit  0: Charging              (page 0x85, usage 0x44, flags 0xA3)
Bit  1: Discharging           (page 0x85, usage 0x45, flags 0xA3)
Bit  2: ACPresent             (page 0x85, usage 0xD0, flags 0xA3)
Bit  3: BatteryPresent        (page 0x85, usage 0xD1, flags 0xA3)
Bit  4: BelowRemainingCapLim  (page 0x85, usage 0x42, flags 0xA3)
Bit  5: RemainingTimeLimExp   (page 0x85, usage 0x43, flags 0xA2)
Bit  6: NeedReplacement       (page 0x85, usage 0x4B, flags 0xA3)
Bit  7: VoltageNotRegulated   (page 0x85, usage 0xDB, flags 0xA3)
Bit  8: FullyCharged          (page 0x85, usage 0x46, flags 0xA3)
Bit  9: FullyDischarged       (page 0x85, usage 0x47, flags 0xA3)
Bit 10: ShutdownRequested     (page 0x84, usage 0x68, flags 0xA2)
Bit 11: ShutdownImminent      (page 0x84, usage 0x69, flags 0xA3)
Bit 12: CommunicationLost     (page 0x84, usage 0x73, flags 0xA3)
Bit 13: Overload              (page 0x84, usage 0x65, flags 0xA3)
Bits 14-15: padding (Constant)
```

AC present, battery OK, fully charged = `0x010C` (bits 2,3,8 set)
On battery, discharging = `0x000A` (bits 1,3 set)

### Full report catalog (25 reports)

See `hid_power_device/reports.py` for the complete catalog with all usage codes,
pages, logical ranges, flags, string indices, and units.

### Time values

Time reports use seconds (HID Unit Code 0x1001, Exponent 0). This matches what
NUT's `battery.runtime` expects. The spec prose says "minutes" but that's the
Smart Battery (SMBus) convention, not the HID unit encoding.

### Voltage values

Voltage uses centivolts (HID Unit 0x00F0D121, Exponent 5). So 12.00V = 1200.

### ManufactureDate encoding

`(year - 1980) * 512 + month * 32 + day` per spec section 4.2.6.

## Hardware tested

- **Board**: Waveshare RP2040-One (RP2040, USB device via native USB)
- **Firmware**: Adafruit CircuitPython 10.2.1
- **Hosts tested**:
  - macOS: works (System Information > Power > UPS shows device)
  - Fedora Linux 43 (kernel 7.0.12): kernel binds hid-generic but NUT can't
    open device due to privilege model; hidraw receives no interrupt data
  - Synology DS220+ (DSM 7.x, kernel 4.4.302+, NUT 0.41): NUT recognizes
    device with `explore` flag but gets all-zero values

## Key references

- USB HID Power Device spec: `~/Downloads/pdcv11.pdf`
- C++ HIDPowerDevice library: `~/src/HIDPowerDevice/`
- NUT usbhid-ups driver source: `~/src/nut/drivers/`
- CircuitPython usb_hid implementation: `~/src/circuitpython/shared-module/usb_hid/`
- TinyUSB HID device: `~/src/tinyusb/src/class/hid/hid_device.c`
- NUT interface-0 bug: https://github.com/abratchik/HIDPowerDevice/issues/1
- NUT fix PR: https://github.com/networkupstools/nut/pull/1044

## Recommendations for C/C++ rewrite

1. **Use TinyUSB directly on RP2040** — not Arduino, not CircuitPython. Full
   control over USB descriptors, GET_REPORT responses, and interface ordering.

2. **Implement `tud_hid_get_report_cb`** — return current values for all report
   IDs (both INPUT and FEATURE). This is the single most important thing that
   CircuitPython can't do.

3. **HID must be interface 0** — either make it the only interface, or ensure it
   comes before CDC/MSC in the TinyUSB configuration. Critical for Synology's
   old NUT.

4. **Send interrupt reports every 1-2 seconds** — don't wait for changes. NUT
   polls with short timeouts and may miss infrequent sends.

5. **Consider spoofing a known UPS VID:PID** — for Synology auto-detection
   without manual NUT configuration. Test with Eaton or CyberPower IDs.

6. **GPIO for development mode** — hold a pin low during boot to enable CDC
   serial for debugging. In production mode (pin floating/high), disable CDC
   so HID is interface 0.

7. **Use the descriptor bytes from this project** — the 194-byte descriptor
   above is proven to work with NUT. Start with that exact byte sequence rather
   than regenerating.

8. **Sane defaults at boot** — set ACPresent=1, BatteryPresent=1,
   RemainingCapacity=100, FullyCharged=1 before the first GET_REPORT can arrive.
   Zero-filled defaults make the host think the UPS has a dead battery.
