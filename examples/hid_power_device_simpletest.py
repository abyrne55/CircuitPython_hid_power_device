# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
Minimal USB HID Power Device (UPS) example.

Registers PresentStatus and RemainingCapacity, then reports AC power
at 100% capacity. The host sees a fully-charged UPS on AC.

**boot.py** — runs once at startup to register the HID descriptor::

    import usb_hid
    from hid_power_device.descriptor import build_power_device
    from hid_power_device.reports import PresentStatus, RemainingCapacity

    usb_hid.enable((build_power_device(PresentStatus, RemainingCapacity),))

**code.py** — the main loop (this file):
"""

import time

from hid_power_device import HIDPowerDevice
from hid_power_device.reports import PresentStatus, RemainingCapacity

ups = HIDPowerDevice.find(PresentStatus, RemainingCapacity)

# Defaults are already sensible (AC present, battery present, 100%,
# fully charged), so just send immediately to avoid the zero-state bug.
ups.send()

while True:
    time.sleep(10)
    ups.send()
