# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
GPIO-based UPS example for RP2040.

Two GPIO pins detect AC power (both HIGH = AC present). When AC is lost,
the device reports "on battery" with a reduced capacity and runtime.
Change detection avoids unnecessary USB traffic.

**boot.py** — runs once at startup to register the HID descriptor::

    import usb_hid
    from hid_power_device.descriptor import build_power_device
    from hid_power_device.reports import PresentStatus, RemainingCapacity, RunTimeToEmpty

    usb_hid.enable(
        (build_power_device(PresentStatus, RemainingCapacity, RunTimeToEmpty),)
    )

**code.py** — the main loop (this file):
"""

import time

import board
import digitalio

from hid_power_device import HIDPowerDevice

# -- Configuration --
GPIO_AC_PIN_1 = board.GP0
GPIO_AC_PIN_2 = board.GP1
POLL_INTERVAL_S = 2
FORCE_SEND_INTERVAL_S = 50

ups = HIDPowerDevice.find()


def make_input(pin):
    p = digitalio.DigitalInOut(pin)
    p.direction = digitalio.Direction.INPUT
    p.pull = digitalio.Pull.DOWN  # floating = LOW = on battery (fail-safe)
    return p


pin1 = make_input(GPIO_AC_PIN_1)
pin2 = make_input(GPIO_AC_PIN_2)


def update_state(ac):
    if ac:
        ups.charging = False
        ups.discharging = False
        ups.ac_present = True
        ups.fully_charged = True
        ups.remaining_capacity = 100
        ups.runtime_to_empty = 3600
    else:
        ups.charging = False
        ups.discharging = True
        ups.ac_present = False
        ups.fully_charged = False
        ups.remaining_capacity = 50
        ups.runtime_to_empty = 300


ac = pin1.value and pin2.value
update_state(ac)
ups.send()

prev_ac = ac
cycles = 0
force_every = FORCE_SEND_INTERVAL_S // POLL_INTERVAL_S

while True:
    time.sleep(POLL_INTERVAL_S)
    cycles += 1
    ac = pin1.value and pin2.value
    if ac != prev_ac or cycles >= force_every:
        update_state(ac)
        ups.send()
        prev_ac = ac
        cycles = 0
