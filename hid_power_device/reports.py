# SPDX-FileCopyrightText: Copyright (c) 2026 Anthony Byrne
#
# SPDX-License-Identifier: GPL-3.0-only

"""
`hid_power_device.reports`
================================================================================

HID Power Device report definitions. Each class defines a single HID report
with class-level attributes — no instances are created. Pass report classes
directly to :func:`hid_power_device.descriptor.build_power_device`.

Usage pages and usages follow the USB HID Power Device Usage Tables spec
(Release 1.1, May 29, 2020). INPUT/FEATURE classification follows spec
Tables 2/3.
"""

_PAGE_POWER = 0x84
_PAGE_BATTERY = 0x85


class IProduct:
    report_id = 1
    usage_page = _PAGE_POWER
    usage = 0xFE
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = 2
    unit = None
    unit_exponent = None
    signed = False


class ISerialNumber:
    report_id = 2
    usage_page = _PAGE_POWER
    usage = 0xFF
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = 3
    unit = None
    unit_exponent = None
    signed = False


class IManufacturer:
    report_id = 3
    usage_page = _PAGE_POWER
    usage = 0xFD
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = 1
    unit = None
    unit_exponent = None
    signed = False


class Rechargeable:
    report_id = 6
    usage_page = _PAGE_BATTERY
    usage = 0x8B
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class PresentStatus:
    report_id = 7
    usage_page = _PAGE_POWER
    usage = 0x02
    report_size = 16
    logical_min = 0
    logical_max = 1
    has_input = True
    input_length = 2
    feature_flags = 0
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False
    is_bitfield = True
    # (usage_page, usage, input_flags, feature_flags) per bit
    status_bits = (
        (_PAGE_BATTERY, 0x44, 0xA3, 0xA3),  # Charging
        (_PAGE_BATTERY, 0x45, 0xA3, 0xA3),  # Discharging
        (_PAGE_BATTERY, 0xD0, 0xA3, 0xA3),  # ACPresent
        (_PAGE_BATTERY, 0xD1, 0xA3, 0xA3),  # BatteryPresent
        (_PAGE_BATTERY, 0x42, 0xA3, 0xA3),  # BelowRemainingCapacityLimit
        (_PAGE_BATTERY, 0x43, 0xA2, 0xA2),  # RemainingTimeLimitExpired
        (_PAGE_BATTERY, 0x4B, 0xA3, 0xA3),  # NeedReplacement
        (_PAGE_BATTERY, 0xDB, 0xA3, 0xA3),  # VoltageNotRegulated
        (_PAGE_BATTERY, 0x46, 0xA3, 0xA3),  # FullyCharged
        (_PAGE_BATTERY, 0x47, 0xA3, 0xA3),  # FullyDischarged
        (_PAGE_POWER, 0x68, 0xA2, 0xA2),  # ShutdownRequested
        (_PAGE_POWER, 0x69, 0xA3, 0xA3),  # ShutdownImminent
        (_PAGE_POWER, 0x73, 0xA3, 0xA3),  # CommunicationLost
        (_PAGE_POWER, 0x65, 0xA3, 0xA3),  # Overload
    )


class RemainingTimeLimit:
    report_id = 8
    usage_page = _PAGE_BATTERY
    usage = 0x2A
    report_size = 16
    logical_min = 120
    logical_max = 1380
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = 0x1001
    unit_exponent = 0
    signed = False


class ManufactureDate:
    report_id = 9
    usage_page = _PAGE_BATTERY
    usage = 0x85
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = False
    input_length = 0
    feature_flags = 0xA3
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class ConfigVoltage:
    report_id = 10
    usage_page = _PAGE_POWER
    usage = 0x40
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = None
    unit = 0x00F0D121
    unit_exponent = 5
    signed = False


class Voltage:
    report_id = 11
    usage_page = _PAGE_POWER
    usage = 0x30
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = True
    input_length = 2
    feature_flags = 0xA3
    input_flags = 0xA3
    string_index = None
    unit = 0x00F0D121
    unit_exponent = 5
    signed = False


class RemainingCapacity:
    report_id = 12
    usage_page = _PAGE_BATTERY
    usage = 0x66
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = True
    input_length = 1
    feature_flags = 0xA3
    input_flags = 0xA3
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class RunTimeToEmpty:
    report_id = 13
    usage_page = _PAGE_BATTERY
    usage = 0x68
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = True
    input_length = 2
    feature_flags = 0xA3
    input_flags = 0xA3
    string_index = None
    unit = 0x1001
    unit_exponent = 0
    signed = False


class FullChargeCapacity:
    report_id = 14
    usage_page = _PAGE_BATTERY
    usage = 0x67
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0x83
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class WarningCapacityLimit:
    report_id = 15
    usage_page = _PAGE_BATTERY
    usage = 0x8C
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class CapacityGranularity1:
    report_id = 16
    usage_page = _PAGE_BATTERY
    usage = 0x8D
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0x22
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class RemainingCapacityLimit:
    report_id = 17
    usage_page = _PAGE_BATTERY
    usage = 0x29
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class DelayBeforeShutdown:
    report_id = 18
    usage_page = _PAGE_POWER
    usage = 0x57
    report_size = 16
    logical_min = -32768
    logical_max = 32767
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = True


class DelayBeforeReboot:
    report_id = 19
    usage_page = _PAGE_POWER
    usage = 0x55
    report_size = 16
    logical_min = -32768
    logical_max = 32767
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = True


class AudibleAlarmControl:
    report_id = 20
    usage_page = _PAGE_POWER
    usage = 0x5A
    report_size = 8
    logical_min = 1
    logical_max = 3
    has_input = False
    input_length = 0
    feature_flags = 0xA2
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class CapacityMode:
    report_id = 22
    usage_page = _PAGE_BATTERY
    usage = 0x2C
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class DesignCapacity:
    report_id = 23
    usage_page = _PAGE_BATTERY
    usage = 0x83
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0x83
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class CapacityGranularity2:
    report_id = 24
    usage_page = _PAGE_BATTERY
    usage = 0x8E
    report_size = 8
    logical_min = 0
    logical_max = 100
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = None
    unit = None
    unit_exponent = None
    signed = False


class AverageTimeToFull:
    report_id = 26
    usage_page = _PAGE_BATTERY
    usage = 0x6A
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = False
    input_length = 0
    feature_flags = 0xA3
    input_flags = 0
    string_index = None
    unit = 0x1001
    unit_exponent = 0
    signed = False


class AverageTimeToEmpty:
    report_id = 28
    usage_page = _PAGE_BATTERY
    usage = 0x69
    report_size = 16
    logical_min = 0
    logical_max = 65535
    has_input = True
    input_length = 2
    feature_flags = 0xA3
    input_flags = 0xA3
    string_index = None
    unit = 0x1001
    unit_exponent = 0
    signed = False


class IDeviceChemistry:
    report_id = 31
    usage_page = _PAGE_BATTERY
    usage = 0x89
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = 4
    unit = None
    unit_exponent = None
    signed = False


class IOEMInformation:
    report_id = 32
    usage_page = _PAGE_BATTERY
    usage = 0x8F
    report_size = 8
    logical_min = 0
    logical_max = 255
    has_input = False
    input_length = 0
    feature_flags = 0x23
    input_flags = 0
    string_index = 5
    unit = None
    unit_exponent = None
    signed = False


ALL_REPORTS = (
    IProduct,
    ISerialNumber,
    IManufacturer,
    Rechargeable,
    PresentStatus,
    RemainingTimeLimit,
    ManufactureDate,
    ConfigVoltage,
    Voltage,
    RemainingCapacity,
    RunTimeToEmpty,
    FullChargeCapacity,
    WarningCapacityLimit,
    CapacityGranularity1,
    RemainingCapacityLimit,
    DelayBeforeShutdown,
    DelayBeforeReboot,
    AudibleAlarmControl,
    CapacityMode,
    DesignCapacity,
    CapacityGranularity2,
    AverageTimeToFull,
    AverageTimeToEmpty,
    IDeviceChemistry,
    IOEMInformation,
)
