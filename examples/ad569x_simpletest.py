# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple demo of writing a sine wave to the AD569x DAC."""

import math
import board
import busio
import adafruit_ad569x

i2c = busio.I2C(board.SCL, board.SDA, frequency=800_000)

# Initialize AD569x
dac = adafruit_ad569x.Adafruit_AD569x(i2c)

# length of the sine wave
LENGTH = 100
# value written to the DAC
value = [0] * LENGTH

while True:
    for i in range(LENGTH):
        value[i] = int(math.sin(math.pi * 2 * i / LENGTH) * ((2**15) - 1) + 2**15)
        # write and update DAC
        dac.value = value[i]
