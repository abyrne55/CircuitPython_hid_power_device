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

CircuitPython library for emulating a USB HID Power Device (UPS / battery
system). Makes any CircuitPython board appear as a UPS to the connected host
(macOS, Linux/NUT, Synology DSM, Windows).

Inspired by the `HIDPowerDevice <https://github.com/abratchik/HIDPowerDevice>`_
Arduino library by Alexander Bratchik.


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_
or individual libraries can be installed using
`circup <https://github.com/adafruit/circup>`_.


Installing to a Connected CircuitPython Device with Circup
==========================================================

Make sure that you have ``circup`` installed in your Python environment.
Install it with the following command if necessary:

.. code-block:: shell

    pip3 install circup

With ``circup`` installed and your CircuitPython device connected use the
following command to install:

.. code-block:: shell

    circup install hid_power_device

Or the following command to update an existing version:

.. code-block:: shell

    circup update


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

**code.py** (main loop):

.. code-block:: python

    import time
    from hid_power_device import HIDPowerDevice

    ups = HIDPowerDevice.find()
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
- 2 = % (percentage, the default)
- 3 = Boolean

Windows may require mode 1 (mWh) instead of 2 (%) when a native laptop battery
is present, as it can conflict with the built-in battery driver.

Linux udev rules
----------------

On Linux, UPower may not recognize the device without a udev rule. Create
``/etc/udev/rules.d/99-circuitpython-ups.rules``:

.. code-block:: text

    SUBSYSTEM=="usb", ATTR{idVendor}=="239a", ENV{UPOWER_VENDOR}="CircuitPython"

Replace ``239a`` with your board's USB vendor ID.

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
   used by GET_REPORT (``shared-module/usb_hid/Device.c:255``). Real data
   arrives via interrupt INPUT reports, which NUT/Synology uses for monitoring.


Documentation
=============
API documentation for this library can be found on `Read the Docs <https://circuitpython-hid-power-device.readthedocs.io/>`_.

For information on building library documentation, please check out
`this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.


Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/abyrne55/CircuitPython_hid_power_device/blob/HEAD/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
