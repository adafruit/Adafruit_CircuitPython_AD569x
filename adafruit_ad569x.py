# SPDX-FileCopyrightText: Copyright (c) 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Written by Liz Clark (Adafruit Industries) with OpenAI ChatGPT v4 September 27, 2023 build
# https://help.openai.com/en/articles/6825453-chatgpt-release-notes

# https://chat.openai.com/share/9e1559a0-08be-42b4-87b1-3ae1b1b450c4
"""
`adafruit_adafruit_circuitpython_ad569x`
================================================================================

CircuitPython module for the AD5691/2/3 I2C DAC


* Author(s): Liz Clark

Implementation Notes
--------------------

**Hardware:**

* Adafruit `AD5693R Breakout Board - 16-Bit DAC with I2C Interface - STEMMA QT / qwiic
  <https://www.adafruit.com/product/5811>`_ (Product ID: 5811)

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

import time
from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice

try:
    import typing  # pylint: disable=unused-import
    from busio import I2C
except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_AD569x.git"

_NOP = const(0x00)
_WRITE_INPUT = const(0x10)
_UPDATE_DAC = const(0x20)
_WRITE_DAC_AND_INPUT = const(0x30)
_WRITE_CONTROL = const(0x40)

_NORMAL_MODE = const(0x00)
_OUTPUT_1K_IMPEDANCE = const(0x01)
_OUTPUT_100K_IMPEDANCE = const(0x02)
_OUTPUT_TRISTATE = const(0x03)


class Adafruit_AD569x:
    """Class which provides interface to AD569x Dac.

    :param ~I2C i2c: The `busio.I2C` object to use.
    :param int address: (Optional) The I2C address of the device. Default is 0x4C.
    """

    def __init__(self, i2c: I2C, address: int = 0x4C) -> None:
        """
        Initialize the AD569x chip.
        """
        self.i2c_device = I2CDevice(i2c, address)
        self._address = address
        time.sleep(1)
        try:
            self.reset()
            self.set_mode(_NORMAL_MODE, True, False)
        except OSError as exception:
            raise OSError("Failed to set mode for AD569x") from exception

    def set_mode(self, new_mode: int, enable_ref: bool, gain2x: bool) -> bool:
        """
        Set the operating mode, reference, and gain.
        """
        command = _WRITE_CONTROL
        data = 0x0000
        data |= new_mode << 13
        data |= not enable_ref << 12
        data |= gain2x << 11

        high_byte = (data >> 8) & 0xFF
        low_byte = data & 0xFF

        buffer = bytearray([command, high_byte, low_byte])

        with self.i2c_device as i2c:
            print(buffer)
            i2c.write(buffer)
        return True

    def write_update_dac(self, value: int) -> bool:
        """
        Write a 16-bit value to the input register and update the DAC register.
        """
        command = _WRITE_DAC_AND_INPUT
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF

        buffer = bytearray([command, high_byte, low_byte])

        with self.i2c_device as i2c:
            i2c.write(buffer)
        return True

    def write_dac(self, value: int) -> bool:
        """
        Write a 16-bit value to the DAC input register.
        """
        command = _WRITE_INPUT
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF

        buffer = bytearray([command, high_byte, low_byte])

        with self.i2c_device as i2c:
            i2c.write(buffer)
        return True

    def update_dac(self) -> bool:
        """
        Update the DAC register from the input register.
        """
        command = _UPDATE_DAC
        buffer = bytearray([command, 0x00, 0x00])

        with self.i2c_device as i2c:
            i2c.write(buffer)
        return True

    def reset(self) -> None:
        """
        Soft-reset the AD569x chip.
        """
        command = _WRITE_CONTROL
        buffer = bytearray([command, 0x80, 0x00])

        with self.i2c_device as i2c:
            print(buffer)
            i2c.write(buffer, end=False)
