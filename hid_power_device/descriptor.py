# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
`hid_power_device.descriptor`
================================================================================

Boot-time HID descriptor builder for USB Power Devices. Call
:func:`build_power_device` from ``boot.py`` to register the device with
:mod:`usb_hid`.

Example ``boot.py``::

    import usb_hid
    from hid_power_device.descriptor import build_power_device
    from hid_power_device.reports import PresentStatus, RemainingCapacity

    usb_hid.enable((build_power_device(PresentStatus, RemainingCapacity),))
"""

import usb_hid


def _encode_item(tag, value):
    """Encode a HID short item (tag + minimal-width signed value)."""
    # HID items are sign-extended, so pick the narrowest width
    # that preserves the sign of the value.
    if -128 <= value <= 127:
        return bytes([tag | 0x01, value & 0xFF])
    if -32768 <= value <= 32767:
        return bytes([tag | 0x02, value & 0xFF, (value >> 8) & 0xFF])
    return bytes(
        [
            tag | 0x03,
            value & 0xFF,
            (value >> 8) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 24) & 0xFF,
        ]
    )


_USAGE_PAGE = 0x04
_USAGE = 0x08
_COLLECTION = 0xA0
_END_COLLECTION = 0xC0
_REPORT_ID = 0x84
_REPORT_SIZE = 0x74
_REPORT_COUNT = 0x94
_LOGICAL_MIN = 0x14
_LOGICAL_MAX = 0x24
_INPUT = 0x80
_FEATURE = 0xB0
_UNIT = 0x64
_UNIT_EXPONENT = 0x54
_STRING_INDEX = 0x78

_COLLECTION_APPLICATION = 0x01
_COLLECTION_LOGICAL = 0x02


def _sort_key(report_cls):
    is_bitfield = getattr(report_cls, "is_bitfield", False)
    return (is_bitfield, report_cls.report_size, report_cls.report_id)


def build_power_device(*report_classes):  # noqa: PLR0912, PLR0915
    """Build a USB HID Power Device from the given report classes.

    :param report_classes: Report classes from :mod:`hid_power_device.reports`.
        Each class defines one HID report via class-level attributes.
    :return: A :class:`usb_hid.Device` ready to pass to :func:`usb_hid.enable`.

    Example::

        from hid_power_device.reports import ALL_REPORTS
        device = build_power_device(*ALL_REPORTS)
    """
    reports = sorted(report_classes, key=_sort_key)

    d = bytearray()

    # Collection preamble
    d.extend(_encode_item(_USAGE_PAGE, 0x84))
    d.extend(_encode_item(_USAGE, 0x04))
    d.extend(_encode_item(_COLLECTION, _COLLECTION_APPLICATION))
    d.extend(_encode_item(_USAGE, 0x24))  # PowerSummary
    d.extend(_encode_item(_COLLECTION, _COLLECTION_LOGICAL))

    # Initial state
    cur_size = 8
    cur_count = 1
    cur_min = 0
    cur_max = 255
    cur_page = 0x84
    cur_unit = None
    cur_unit_exp = None

    d.extend(_encode_item(_REPORT_SIZE, cur_size))
    d.extend(_encode_item(_REPORT_COUNT, cur_count))
    d.extend(_encode_item(_LOGICAL_MIN, cur_min))
    d.extend(_encode_item(_LOGICAL_MAX, cur_max))

    for rpt in reports:
        if getattr(rpt, "is_bitfield", False):
            _emit_present_status(d, rpt)
            continue

        if rpt.usage_page != cur_page:
            d.extend(_encode_item(_USAGE_PAGE, rpt.usage_page))
            cur_page = rpt.usage_page

        if rpt.report_size != cur_size:
            d.extend(_encode_item(_REPORT_SIZE, rpt.report_size))
            cur_size = rpt.report_size

        if rpt.logical_max != cur_max:
            d.extend(_encode_item(_LOGICAL_MAX, rpt.logical_max))
            cur_max = rpt.logical_max

        if rpt.logical_min != cur_min:
            d.extend(_encode_item(_LOGICAL_MIN, rpt.logical_min))
            cur_min = rpt.logical_min

        if rpt.unit != cur_unit:
            if rpt.unit is not None:
                d.extend(_encode_item(_UNIT, rpt.unit))
            else:
                d.extend(_encode_item(_UNIT, 0))
            cur_unit = rpt.unit

        if rpt.unit_exponent != cur_unit_exp:
            if rpt.unit_exponent is not None:
                d.extend(_encode_item(_UNIT_EXPONENT, rpt.unit_exponent))
            else:
                d.extend(_encode_item(_UNIT_EXPONENT, 0))
            cur_unit_exp = rpt.unit_exponent

        d.extend(_encode_item(_REPORT_ID, rpt.report_id))
        d.extend(_encode_item(_USAGE, rpt.usage))

        if rpt.string_index is not None:
            d.extend(_encode_item(_STRING_INDEX, rpt.string_index))

        if rpt.has_input:
            d.extend(_encode_item(_INPUT, rpt.input_flags))
            d.extend(_encode_item(_USAGE, rpt.usage))
        d.extend(_encode_item(_FEATURE, rpt.feature_flags))

    # Close PowerSummary Logical + UPS Application
    d.extend(bytes([_END_COLLECTION]))
    d.extend(bytes([_END_COLLECTION]))

    report_ids = []
    in_lengths = []
    for rpt in reports:
        if rpt.has_input:
            report_ids.append(rpt.report_id)
            in_lengths.append(rpt.input_length)

    return usb_hid.Device(
        report_descriptor=bytes(d),
        usage_page=0x84,
        usage=0x04,
        report_ids=tuple(report_ids),
        in_report_lengths=tuple(in_lengths),
        out_report_lengths=tuple(0 for _ in report_ids),
    )


def _emit_present_status(d, rpt):
    """Emit the PresentStatus nested collection with individual bit fields."""
    d.extend(_encode_item(_USAGE, rpt.usage))
    d.extend(_encode_item(_COLLECTION, _COLLECTION_LOGICAL))
    d.extend(_encode_item(_REPORT_ID, rpt.report_id))

    d.extend(_encode_item(_REPORT_SIZE, 1))
    d.extend(_encode_item(_LOGICAL_MIN, 0))
    d.extend(_encode_item(_LOGICAL_MAX, 1))

    cur_page = None
    for page, usage, in_flags, feat_flags in rpt.status_bits:
        if page != cur_page:
            d.extend(_encode_item(_USAGE_PAGE, page))
            cur_page = page
        d.extend(_encode_item(_USAGE, usage))
        d.extend(_encode_item(_INPUT, in_flags))
        d.extend(_encode_item(_USAGE, usage))
        d.extend(_encode_item(_FEATURE, feat_flags))

    # 2 padding bits
    d.extend(_encode_item(_REPORT_COUNT, 2))
    d.extend(_encode_item(_INPUT, 0x01))
    d.extend(_encode_item(_FEATURE, 0x01))

    d.extend(bytes([_END_COLLECTION]))
