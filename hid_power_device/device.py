# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
`hid_power_device.device`
================================================================================

Runtime API for USB HID Power Devices. Use :class:`HIDPowerDevice` from
``code.py`` to set report values and send INPUT reports.
"""

import usb_hid

from .reports import (
    AverageTimeToEmpty,
    PresentStatus,
    RemainingCapacity,
    RunTimeToEmpty,
    Voltage,
)


class HIDPowerDevice:  # noqa: PLR0904
    """Runtime interface for a USB HID Power Device.

    Sets report values and sends INPUT reports over the interrupt endpoint.
    Only reports registered in :func:`~hid_power_device.descriptor.build_power_device`
    are sent.

    :param device: A :class:`usb_hid.Device` with ``usage_page=0x84``.
    """

    _STATUS_BIT_NAMES = (
        "charging",
        "discharging",
        "ac_present",
        "battery_present",
        "below_remaining_capacity_limit",
        "remaining_time_limit_expired",
        "need_replacement",
        "voltage_not_regulated",
        "fully_charged",
        "fully_discharged",
        "shutdown_requested",
        "shutdown_imminent",
        "communication_lost",
        "overload",
    )

    def __init__(self, device):
        self._device = device
        self._active_ids = set(device.report_ids)

        self._buf1 = bytearray(1)
        self._buf2 = bytearray(2)

        self._present_status = 0
        self._remaining_capacity = 100
        self._runtime_to_empty = 0
        self._average_time_to_empty = 0
        self._voltage = 0

        # Sane defaults to avoid zero-state bug
        self.battery_present = True
        self.ac_present = True
        self.fully_charged = True

    @staticmethod
    def find():
        """Find the Power Device from :data:`usb_hid.devices`.

        :return: A :class:`HIDPowerDevice` wrapping the first device with
            ``usage_page=0x84`` and ``usage=0x04``.
        :raises StopIteration: If no Power Device is registered.
        """
        dev = next(d for d in usb_hid.devices if d.usage_page == 0x84 and d.usage == 0x04)
        return HIDPowerDevice(dev)

    # -- PresentStatus boolean properties --

    @property
    def charging(self):
        return bool(self._present_status & (1 << 0))

    @charging.setter
    def charging(self, value):
        if value:
            self._present_status |= 1 << 0
        else:
            self._present_status &= ~(1 << 0)

    @property
    def discharging(self):
        return bool(self._present_status & (1 << 1))

    @discharging.setter
    def discharging(self, value):
        if value:
            self._present_status |= 1 << 1
        else:
            self._present_status &= ~(1 << 1)

    @property
    def ac_present(self):
        return bool(self._present_status & (1 << 2))

    @ac_present.setter
    def ac_present(self, value):
        if value:
            self._present_status |= 1 << 2
        else:
            self._present_status &= ~(1 << 2)

    @property
    def battery_present(self):
        return bool(self._present_status & (1 << 3))

    @battery_present.setter
    def battery_present(self, value):
        if value:
            self._present_status |= 1 << 3
        else:
            self._present_status &= ~(1 << 3)

    @property
    def below_remaining_capacity_limit(self):
        return bool(self._present_status & (1 << 4))

    @below_remaining_capacity_limit.setter
    def below_remaining_capacity_limit(self, value):
        if value:
            self._present_status |= 1 << 4
        else:
            self._present_status &= ~(1 << 4)

    @property
    def remaining_time_limit_expired(self):
        return bool(self._present_status & (1 << 5))

    @remaining_time_limit_expired.setter
    def remaining_time_limit_expired(self, value):
        if value:
            self._present_status |= 1 << 5
        else:
            self._present_status &= ~(1 << 5)

    @property
    def need_replacement(self):
        return bool(self._present_status & (1 << 6))

    @need_replacement.setter
    def need_replacement(self, value):
        if value:
            self._present_status |= 1 << 6
        else:
            self._present_status &= ~(1 << 6)

    @property
    def voltage_not_regulated(self):
        return bool(self._present_status & (1 << 7))

    @voltage_not_regulated.setter
    def voltage_not_regulated(self, value):
        if value:
            self._present_status |= 1 << 7
        else:
            self._present_status &= ~(1 << 7)

    @property
    def fully_charged(self):
        return bool(self._present_status & (1 << 8))

    @fully_charged.setter
    def fully_charged(self, value):
        if value:
            self._present_status |= 1 << 8
        else:
            self._present_status &= ~(1 << 8)

    @property
    def fully_discharged(self):
        return bool(self._present_status & (1 << 9))

    @fully_discharged.setter
    def fully_discharged(self, value):
        if value:
            self._present_status |= 1 << 9
        else:
            self._present_status &= ~(1 << 9)

    @property
    def shutdown_requested(self):
        return bool(self._present_status & (1 << 10))

    @shutdown_requested.setter
    def shutdown_requested(self, value):
        if value:
            self._present_status |= 1 << 10
        else:
            self._present_status &= ~(1 << 10)

    @property
    def shutdown_imminent(self):
        return bool(self._present_status & (1 << 11))

    @shutdown_imminent.setter
    def shutdown_imminent(self, value):
        if value:
            self._present_status |= 1 << 11
        else:
            self._present_status &= ~(1 << 11)

    @property
    def communication_lost(self):
        return bool(self._present_status & (1 << 12))

    @communication_lost.setter
    def communication_lost(self, value):
        if value:
            self._present_status |= 1 << 12
        else:
            self._present_status &= ~(1 << 12)

    @property
    def overload(self):
        return bool(self._present_status & (1 << 13))

    @overload.setter
    def overload(self, value):
        if value:
            self._present_status |= 1 << 13
        else:
            self._present_status &= ~(1 << 13)

    # -- Value properties --

    @property
    def remaining_capacity(self):
        """Battery remaining capacity (0–100 percent)."""
        return self._remaining_capacity

    @remaining_capacity.setter
    def remaining_capacity(self, value):
        self._remaining_capacity = value

    @property
    def runtime_to_empty(self):
        """Estimated runtime remaining in seconds."""
        return self._runtime_to_empty

    @runtime_to_empty.setter
    def runtime_to_empty(self, value):
        self._runtime_to_empty = value

    @property
    def average_time_to_empty(self):
        """Average time to empty in seconds."""
        return self._average_time_to_empty

    @average_time_to_empty.setter
    def average_time_to_empty(self, value):
        self._average_time_to_empty = value

    @property
    def voltage(self):
        """Battery voltage in centivolts (e.g. 1200 = 12.00V)."""
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value

    # -- Send --

    def send(self):
        """Send all active INPUT reports via the interrupt endpoint.

        Only reports whose IDs were registered with
        :func:`~hid_power_device.descriptor.build_power_device` are sent.
        """
        for rid in self._device.report_ids:
            if rid == PresentStatus.report_id:
                self._buf2[0] = self._present_status & 0xFF
                self._buf2[1] = (self._present_status >> 8) & 0xFF
                self._device.send_report(self._buf2, rid)
            elif rid == RemainingCapacity.report_id:
                self._buf1[0] = self._remaining_capacity & 0xFF
                self._device.send_report(self._buf1, rid)
            elif rid == RunTimeToEmpty.report_id:
                self._buf2[0] = self._runtime_to_empty & 0xFF
                self._buf2[1] = (self._runtime_to_empty >> 8) & 0xFF
                self._device.send_report(self._buf2, rid)
            elif rid == AverageTimeToEmpty.report_id:
                self._buf2[0] = self._average_time_to_empty & 0xFF
                self._buf2[1] = (self._average_time_to_empty >> 8) & 0xFF
                self._device.send_report(self._buf2, rid)
            elif rid == Voltage.report_id:
                self._buf2[0] = self._voltage & 0xFF
                self._buf2[1] = (self._voltage >> 8) & 0xFF
                self._device.send_report(self._buf2, rid)

    # -- Utility --

    @staticmethod
    def encode_manufacture_date(year, month, day):
        """Encode a date for the ManufactureDate report.

        Per the HID Power Device spec section 4.2.6, the date is packed as:
        ``(year - 1980) * 512 + month * 32 + day``.

        :param int year: Four-digit year (>= 1980).
        :param int month: Month (1–12).
        :param int day: Day (1–31).
        :return: Encoded 16-bit date value.
        :rtype: int
        """
        return (year - 1980) * 512 + month * 32 + day
