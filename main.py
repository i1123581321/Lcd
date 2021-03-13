#!/usr/bin/python3
import logging
import signal
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from lcd import config, lcd
from my_image import MyImage

lcd = lcd.Lcd()
logging.basicConfig(filename=f"/home/pi/workspace/LCD/log/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

def handler(signum, frame):
    print(f"Signal handler called with {signum}")
    lcd.clear()
    lcd.teardown()
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    lcd.setup()
    lcd.clear()

    image = MyImage()

    while True:
        lcd.show(image.get())
        lcd.delay(10*1000)
        image.update()
