from PIL import Image, ImageDraw, ImageFont

from sysinfo import Sysinfo
from weather import Weather

SIZE = (320, 240)
mono = ImageFont.truetype("/home/pi/workspace/LCD/fonts/Cascadia.ttf", size=16)
sans_normal = ImageFont.truetype("/home/pi/workspace/LCD/fonts/miao.ttf", size=24)
sans_big = ImageFont.truetype("/home/pi/workspace/LCD/fonts/miao.ttf", size=72)


class MyImage():
    def __init__(self):
        self.weather = Weather()
        self.info = Sysinfo()

    def get(self, rotate: int = 180):
        image = Image.new("RGB", SIZE, "#74a8ce")
        draw = ImageDraw.Draw(image)

        sysinfo = self.info.get()

        draw.rectangle([(10, 140), (309, 229)], fill="#000000")
        draw.text((15, 145), f"> ip: {sysinfo['ip']}", fill="#00FF00", font=mono)
        draw.text((15, 165), f"> mem_total: {sysinfo['memory']['total']} MB",
                  fill="#00FF00", font=mono)
        draw.text((15, 185), f"> mem_avail: {sysinfo['memory']['avail']} MB", fill="#00FF00", font=mono)
        draw.text((15, 205), f"> cpu_temp: {sysinfo['temp']}", fill="#00FF00", font=mono)

        name, weather = self.weather.get()
        if not weather:
            return image.rotate(rotate)

        now = weather["now"]
        forecast = weather["forecast"]

        with Image.open(f"/home/pi/workspace/LCD/icon/{now['icon']}.png") as f:
            f = f.resize((96, 96))
            draw.bitmap((1, 0), f, fill="#FFFFFF")
        draw.text((100, 5), name, fill="#FFFFFF", font=sans_normal)
        draw.text((120, 25), f"{now['temp']}/{now['feelsLike']}°", fill="#FFFFFF", font=sans_big)
        draw.text((160, 5), f"{now['text']} Hum:{now['humidity']}%",
                  font=sans_normal, fill="#FFFFFF")

        for i, info in enumerate(forecast):
            icon, tmin, tmax = info
            with Image.open(f"/home/pi/workspace/LCD/icon/{icon}.png") as f:
                f = f.resize((40, 40))
                draw.bitmap((20 + i * 100, 90), f, fill="#FFFFFF")
                draw.text((60 + i * 100, 110), f"{tmin}~{tmax}", fill="#FFFFFF", font=sans_normal)

        return image.rotate(rotate)

    def update(self):
        self.weather.update()
        self.info.update()
