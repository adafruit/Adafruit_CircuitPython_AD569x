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

"""

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


class Adafruit_AD569x:
    """Class which provides interface to AD569x Dac."""

    NORMAL_MODE = const(0x00)
    OUTPUT_1K_IMPEDANCE = const(0x01)
    OUTPUT_100K_IMPEDANCE = const(0x02)
    OUTPUT_TRISTATE = const(0x03)

    def __init__(  # pylint: disable=too-many-arguments
        self,
        i2c: I2C,
        address: int = 0x4C,
        initial_mode: int = NORMAL_MODE,
        enable_ref: bool = True,
        gain2x: bool = False,
    ) -> None:
        """
        Initialize the AD569x device.

        This function initializes the I2C device, performs a soft reset,
        and sets the initial operating mode,
        reference voltage, and gain settings.

        :param i2c: The I2C bus.
        :param address: The I2C address of the device. Defaults to 0x4C.
        :param initial_mode: The initial operating mode. Defaults to NORMAL_MODE.
        :param enable_ref: Whether to enable the reference. Defaults to True.
        :param gain2x: Whether to set the gain to 2xVref. Defaults to False.
        """
        self.i2c_device = I2CDevice(i2c, address)
        self._address = address

        try:
            self.reset()
            self.mode = (initial_mode, enable_ref, gain2x)
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

    def _send_write_command(self, command: int, data: int) -> None:
        """
        Send a command and data to the I2C device without sending a stop condition.

        This internal function prepares a 3-byte buffer containing the command and data,
        and writes it to the I2C device without sending a stop condition.

        :param command: The command byte to send.
        :param data: The 16-bit data to send.
        """
        try:
            high_byte = (data >> 8) & 0xFF
            low_byte = data & 0xFF
            buffer = bytearray([command, high_byte, low_byte])
            with self.i2c_device as i2c:
                i2c.write(buffer, end=False)
        except Exception as error:
            raise Exception(f"Error sending command: {error}") from error

    @property
    def mode(self) -> typing.Tuple[int, bool, bool]:
        """
        Set the operating mode, reference, and gain for the AD569x chip.

        :param new_values: A tuple containing new operating mode, enable_ref, and gain2x.
        """
        return self.mode

    @mode.setter
    def mode(self, new_values: typing.Tuple[int, bool, bool]) -> None:
        new_mode, enable_ref, gain2x = new_values

        # Prepare the command byte
        command = _WRITE_CONTROL

        # Prepare the high and low data bytes
        data = 0x0000
        data |= new_mode << 13  # Set D14 and D13 for the operating mode
        data |= not enable_ref << 12  # Set D12 for enable_ref
        data |= gain2x << 11  # Set D11 for the gain

        self._send_write_command(command, data)

    def set_value(self, value: int) -> None:
        """
        Write a 16-bit value to the input register and update the DAC register.

        This property writes a 16-bit value to the input register and then updates
        the DAC register of the AD569x chip in a single operation.
        """
        self._send_command(_WRITE_DAC_AND_INPUT, value)

    def write_dac(self, value: int) -> None:
        """
        Write a 16-bit value to the input register.

        This function writes a 16-bit value to the input register of the AD569x chip.
        """
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
        # Use the internal _send_command function with 0x8000 as data
        self._send_write_command(_WRITE_CONTROL, 0x8000)
