# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
`hid_power_device`
================================================================================

CircuitPython library for acting like a USB HID Power Device (UPS).

Inspired by the `HIDPowerDevice <https://github.com/abratchik/HIDPowerDevice>`_
Arduino library by Alexander Bratchik.

* Author(s): Anthony Byrne

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

from .device import HIDPowerDevice

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/abyrne55/CircuitPython_hid_power_device.git"

__all__ = ["HIDPowerDevice"]
