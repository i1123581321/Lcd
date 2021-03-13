import json
import logging

import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81 "
}

key = "81d70d330760407b9102184d47874d2d"

forecast_url = "https://devapi.qweather.com/v7/weather/3d"
now_url = "https://devapi.qweather.com/v7/weather/now"


def get(url, location):
    try:
        response = requests.get(
            url=url,
            params={
                "key": key,
                "location": location
            },
            headers=headers,
            timeout=2.0
        )
        if response.status_code != 200:
            logging.error(f"ERROR: {response.status_code}")
            return None
    except Exception as e:
        logging.error(e)
        return None
    return response.json()


class Weather():
    def __init__(self, update_interval=60):
        self.city_location = {
            "荔湾": "101280106",
            "栖霞": "101190112"
        }
        self.update_interval = update_interval
        self.cnt = 0
        self.updated = False
        self.weather = {x: {} for x in self.city_location.keys()}
        self.weather_iter = iter(self.weather)
        self.update()

    def get(self):
        try:
            name = next(self.weather_iter)
            return name, self.weather[name]
        except StopIteration:
            self.weather_iter = iter(self.weather)
            return self.get()

    def update(self):
        if not self.updated:
            for name, location in self.city_location.items():
                now = get(now_url, location)
                forecast = get(forecast_url, location)
                if now is not None and forecast is not None:
                    self.weather[name]["now"] = now["now"]
                    self.weather[name]["forecast"] = [(x["iconDay"], x["tempMin"], x["tempMax"]) for x in
                                                      forecast["daily"]]
                else:
                    self.updated = False
                    self.cnt = 0
                    return
            self.updated = True
        else:
            self.cnt += 1
            if self.cnt == self.update_interval:
                self.cnt = 0
                self.updated = False
                self.update()
