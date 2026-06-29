Introduction
============


.. image:: https://readthedocs.org/projects/circuitpython-hid-power-device/badge/?version=latest
    :target: https://circuitpython-hid-power-device.readthedocs.io/
    :alt: Documentation Status


.. image:: https://github.com/abyrne55/CircuitPython_hid_power_device/workflows/Build%20CI/badge.svg
    :target: https://github.com/abyrne55/CircuitPython_hid_power_device/actions
    :alt: Build Status


.. image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Code Style: Ruff

.. warning::

   **This project is abandoned.** CircuitPython's ``usb_hid`` module has
   platform limitations that prevent it from working with NUT/Synology: the
   ``send_report()`` API does not populate the buffers used by GET_REPORT, so
   the host always reads zeros. There is no Python-level workaround. See
   ``LESSONS_LEARNED.md`` for a full writeup and recommendations for a C/C++
   rewrite using TinyUSB directly.

CircuitPython library for emulating a USB HID Power Device (UPS / battery
system). Makes any CircuitPython board appear as a UPS to the connected host
(macOS only — see warning above).

Inspired by the `HIDPowerDevice <https://github.com/abratchik/HIDPowerDevice>`_
Arduino library by Alexander Bratchik.


Dependencies
=============

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
  (no additional libraries required)


Installation
============

Copy the ``hid_power_device/`` directory to the ``lib/`` folder on your
CircuitPython board.

Or install with `circup <https://github.com/adafruit/circup>`_ (once published
to PyPI):

.. code-block:: shell

    circup install hid_power_device


Usage Example
=============

This library uses CircuitPython's split ``boot.py`` / ``code.py`` pattern.
The HID descriptor must be registered at boot time before the USB stack starts.

**boot.py** (runs once at startup):

.. code-block:: python

    import usb_hid
    from hid_power_device.descriptor import build_power_device
    from hid_power_device.reports import PresentStatus, RemainingCapacity

    usb_hid.enable((build_power_device(PresentStatus, RemainingCapacity),))

**code.py** (main loop — pass the same report classes used in boot.py):

.. code-block:: python

    import time
    from hid_power_device import HIDPowerDevice
    from hid_power_device.reports import PresentStatus, RemainingCapacity

    ups = HIDPowerDevice.find(PresentStatus, RemainingCapacity)
    ups.send()  # send defaults immediately to avoid zero-state bug

    while True:
        time.sleep(10)
        ups.send()

Only include the report classes you need — each one adds to the HID descriptor
size. The minimum viable set for host UPS recognition is ``PresentStatus`` +
``RemainingCapacity``.


Notes
=====

CapacityMode
------------

``CapacityMode`` controls how the host interprets capacity values:

- 0 = mAh (milliamp-hours)
- 1 = mWh (milliwatt-hours)
- 2 = % (percentage, recommended for this library's percentage-based reports)
- 3 = Boolean

Windows may require mode 1 (mWh) instead of 2 (%) when a native laptop battery
is present, as it can conflict with the built-in battery driver.

Time values
-----------

Time reports (``RunTimeToEmpty``, ``AverageTimeToEmpty``, ``AverageTimeToFull``)
use **seconds** as the unit. This follows the HID Power Device spec Table 1
(Unit Code = 0x1001, Exponent = 0). NUT's ``battery.runtime`` also expects
seconds.

The spec prose (section 4.2.5) refers to these values as "in minutes" — that is
the Smart Battery (SMBus) convention, not the HID unit encoding.


Known Limitations
=================

1. **FEATURE-only reports are not readable by the host.** CircuitPython's
   ``usb_hid.Device`` has no ``feature_report_lengths`` parameter. FEATURE-only
   reports (DesignCapacity, ManufactureDate, ConfigVoltage, etc.) appear in the
   HID descriptor for host discovery, but GET_REPORT returns a STALL. Static
   configuration data is unavailable to NUT/Synology. This is a CircuitPython
   platform limitation.

2. **GET_REPORT returns zeros for INPUT reports.** ``send_report()`` sends data
   via the interrupt endpoint but does not populate the ``in_report_buffers``
   used by GET_REPORT (``tud_hid_get_report_cb`` in CircuitPython's
   ``shared-module/usb_hid/Device.c``). Real data
   arrives via interrupt INPUT reports, which NUT/Synology uses for monitoring.


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-hid-power-device.readthedocs.io/>`_.


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/abyrne55/CircuitPython_hid_power_device/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
