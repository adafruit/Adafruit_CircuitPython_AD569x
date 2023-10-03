# SPDX-FileCopyrightText: 2023 Liz Clark for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple demo of writing a sine wave to the AD569x DAC

import time
import board
import math
import adafruit_ad569x


i2c = board.I2C()

# Initialize AD569x
dac = adafruit_ad569x.Adafruit_AD569x(i2c)

# length of the sine wave
length = 100
# value written to the DAC
value = [0] * length

while True:

    for i in range(length):
        value[i] = int(math.sin(math.pi * 2 * i / length) * ((2**15) - 1) + 2**15)
        # write and update DAC
        if not dac.write_update_dac(value[i]):
            print("Failed to update DAC.")
