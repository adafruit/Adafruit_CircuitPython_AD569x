# SPDX-FileCopyrightText: Copyright (c) 2023 Liz Clark for Adafruit Industries
#
# SPDX-License-Identifier: MIT

# Written by Liz Clark (Adafruit Industries) with OpenAI ChatGPT v4 September 25, 2023 build
# https://help.openai.com/en/articles/6825453-chatgpt-release-notes

# https://chat.openai.com/share/36910a8a-dfce-4c68-95fe-978721c697c9
"""
`adafruit_ad569x`
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
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register

"""

from micropython import const
from adafruit_bus_device.i2c_device import I2CDevice
from adafruit_register.i2c_bits import RWBits

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


class Adafruit_AD569x:
    """Class which provides interface to AD569x Dac."""

    NORMAL_MODE = const(0x00)
    OUTPUT_1K_IMPEDANCE = const(0x01)
    OUTPUT_100K_IMPEDANCE = const(0x02)
    OUTPUT_TRISTATE = const(0x03)
    GAIN_1X = const(0)
    GAIN_2X = const(1)

    def __init__(self, i2c: I2C, address: int = 0x4C) -> None:
        """
        Initialize the AD569x device.

        This function initializes the I2C device, performs a soft reset,
        and sets the initial operating mode,
        reference voltage, and gain settings.

        :param i2c: The I2C bus.
        :param address: The I2C address of the device. Defaults to 0x4C.
        """
        self.i2c_device = I2CDevice(i2c, address)
        self._address = address

        self._reset_command = RWBits(1, _WRITE_CONTROL, 15, 2)
        self._mode_command = RWBits(2, _WRITE_CONTROL, 13, 2)
        self._ref_command = RWBits(1, _WRITE_CONTROL, 12, 2)
        self._gain_command = RWBits(1, _WRITE_CONTROL, 11, 2)

        try:
            self.reset()
            self.mode = self.NORMAL_MODE
            self.enable_ref = True
            self.gain = self.GAIN_1X
        except OSError as error:
            raise OSError(f"Failed to initialize AD569x, {error}") from error

    def _send_command(self, command: int, data: int) -> None:
        """
        Send a command and data to the I2C device.

        This internal function prepares a 3-byte buffer containing the command and data,
        and writes it to the I2C device.

        :param command: The command byte to send.
        :param data: The 16-bit data to send.
        """
        try:
            high_byte = (data >> 8) & 0xFF
            low_byte = data & 0xFF
            buffer = bytearray([command, high_byte, low_byte])
            with self.i2c_device as i2c:
                i2c.write(buffer)
        except Exception as error:
            raise Exception(f"Error sending command: {error}") from error

    @property
    def mode(self) -> int:
        """
        Set the operating mode for the AD569x chip.

        :param value: An int containing new operating mode.
        """
        return self._mode_command

    @mode.setter
    def mode(self, value: int) -> None:
        self._mode_command = value

    @property
    def ref_enabled(self) -> bool:
        """
        Enable the reference voltage for the AD569x chip.

        :param value: A bool to enable the reference voltage.
        """
        return not bool(self._ref_command)

    @ref_enabled.setter
    def ref_enabled(self, value: bool) -> None:
        self._ref_command = value

    @property
    def gain(self) -> bool:
        """
        Set the gain for the AD569x chip.

        :param value: A bool to choose 1X or 2X gain.
        """
        return bool(self._gain_command)

    @gain.setter
    def gain(self, value: bool) -> None:
        self._gain_command = value

    @property
    def value(self) -> int:
        """
        Write a 16-bit value to the input register and update the DAC register.

        This property writes a 16-bit value to the input register and then updates
        the DAC register of the AD569x chip in a single operation.
        """
        return self.value

    @value.setter
    def value(self, value: int) -> None:
        self._send_command(_WRITE_DAC_AND_INPUT, value)

    @property
    def dac(self) -> int:
        """
        Write a 16-bit value to the input register.

        This function writes a 16-bit value to the input register of the AD569x chip.
        """
        return self.dac

    @dac.setter
    def dac(self, value: int) -> None:
        # Use the internal _send_command function
        self._send_command(_WRITE_INPUT, value)

    def update_dac(self) -> None:
        """
        Update the DAC register from the input register.

        This function sends the UPDATE_DAC command to the AD569x chip to update
        the DAC register based on the value stored in the input register.
        """
        # Use the internal _send_command function with 0x0000 as data
        self._send_command(_UPDATE_DAC, 0x0000)

    def reset(self) -> None:
        """
        Soft-reset the AD569x chip.

        This function writes 0x8000 to the control register of the AD569x chip
        to perform a reset operation. Resets the DAC to zero-scale and
        resets the input, DAC, and control registers to their default values.
        """
        self._reset_command = 0x8000
