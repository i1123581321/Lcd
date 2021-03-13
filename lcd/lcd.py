import time

import numpy as np
import RPi.GPIO as gpio
import spidev

from . import config


class Lcd():
    def __init__(self):
        gpio.setmode(gpio.BCM)
        gpio.setwarnings(False)

        gpio.setup([
            config.RST_PIN,
            config.DC_PIN,
            config.BL_PIN
        ], gpio.OUT)

        gpio.output(config.BL_PIN, gpio.HIGH)

        self.spi = spidev.SpiDev(0, 0)
        self.spi.max_speed_hz = config.SPI_FREQ
        self.spi.mode = 0b00

        self.pmw = gpio.PWM(config.BL_PIN, config.BL_FREQ)

    def command(self, cmd):
        gpio.output(config.DC_PIN, gpio.LOW)
        self.spi.writebytes([cmd])

    def data(self, value):
        gpio.output(config.DC_PIN, gpio.HIGH)
        self.spi.writebytes([value])

    def reset(self):
        gpio.output(config.RST_PIN, gpio.HIGH)
        self.delay(10)
        gpio.output(config.RST_PIN, gpio.LOW)
        self.delay(10)
        gpio.output(config.RST_PIN, gpio.HIGH)
        self.delay(10)

    def delay(self, ms):
        time.sleep(ms / 1000.0)

    def change_duty_cycle(self, dc):
        self.pmw.ChangeDutyCycle(dc)

    def change_frequency(self, freq):
        self.pmw.ChangeFrequency(freq)

    def setup(self):
        self.pmw.start(100)
        self.reset()

        self.command(0x36)
        self.data(0x00)

        self.command(0x3A)
        self.data(0x05)

        self.command(0x21)

        self.command(0x2A)
        self.data(0x00)
        self.data(0x00)
        self.data(0x01)
        self.data(0x3F)

        self.command(0x2B)
        self.data(0x00)
        self.data(0x00)
        self.data(0x00)
        self.data(0xEF)

        self.command(0xB2)
        self.data(0x0C)
        self.data(0x0C)
        self.data(0x00)
        self.data(0x33)
        self.data(0x33)

        self.command(0xB7)
        self.data(0x35)

        self.command(0xBB)
        self.data(0x1F)

        self.command(0xC0)
        self.data(0x2C)

        self.command(0xC2)
        self.data(0x01)

        self.command(0xC3)
        self.data(0x12)

        self.command(0xC4)
        self.data(0x20)

        self.command(0xC6)
        self.data(0x0F)

        self.command(0xD0)
        self.data(0xA4)
        self.data(0xA1)

        self.command(0xE0)
        self.data(0xD0)
        self.data(0x08)
        self.data(0x11)
        self.data(0x08)
        self.data(0x0C)
        self.data(0x15)
        self.data(0x39)
        self.data(0x33)
        self.data(0x50)
        self.data(0x36)
        self.data(0x13)
        self.data(0x14)
        self.data(0x29)
        self.data(0x2D)

        self.command(0xE1)
        self.data(0xD0)
        self.data(0x08)
        self.data(0x10)
        self.data(0x08)
        self.data(0x06)
        self.data(0x06)
        self.data(0x39)
        self.data(0x44)
        self.data(0x51)
        self.data(0x0B)
        self.data(0x16)
        self.data(0x14)
        self.data(0x2F)
        self.data(0x31)
        self.command(0x21)

        self.command(0x11)

        self.command(0x29)

    def set_windows(self, x0, y0, x1, y1):
        self.command(0x2A)
        self.data(x0 >> 8)
        self.data(x0 & 0xff)
        self.data(x1 >> 8)
        self.data((x1 - 1) & 0xff)

        self.command(0x2B)
        self.data(y0 >> 8)
        self.data(y0 & 0xff)
        self.data(y1 >> 8)
        self.data((y1 - 1) & 0xff)

        self.command(0x2C)

    def show(self, image, x0=0, y0=0):
        image = np.asarray(image)
        pixel = np.zeros((config.HEIGHT, config.WIDTH, 2), dtype=np.uint8)

        pixel[..., [0]] = np.add(np.bitwise_and(image[..., [0]], 0xF8), np.right_shift(image[..., [1]], 5))
        pixel[..., [1]] = np.add(np.bitwise_and(np.left_shift(image[..., [1]], 3), 0xE0), np.right_shift(image[..., [2]], 3))

        pixel = pixel.flatten().tolist()

        self.command(0x36)
        self.data(0x70)
        self.set_windows(0, 0, config.WIDTH, config.HEIGHT)

        gpio.output(config.DC_PIN, gpio.HIGH)
        for i in range(0, len(pixel), 4096):
            self.spi.writebytes(pixel[i:i + 4096])

    def clear(self):
        buffer = [0xff] * (config.WIDTH * config.HEIGHT * 2)
        self.set_windows(0, 0, config.WIDTH, config.HEIGHT)
        gpio.output(config.DC_PIN, gpio.HIGH)
        for i in range(0, len(buffer), 4096):
            self.spi.writebytes(buffer[i: i + 4096])

    def teardown(self):
        self.spi.close()
        gpio.output(config.RST_PIN, gpio.HIGH)
        gpio.output(config.DC_PIN, gpio.LOW)
        self.pmw.stop()
        self.delay(1)
        gpio.output(config.BL_PIN, gpio.HIGH)
        gpio.cleanup()

