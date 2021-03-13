import logging
import socket
import subprocess

import psutil


def get_ip() -> str:
    ip = "x.x.x.x"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception as e:
        logging.warning(e)
    finally:
        s.close()
    return ip


class Sysinfo():
    def __init__(self):
        self.info = {}
        self.update()

    def get(self):
        return self.info

    def update(self):
        memory = psutil.virtual_memory()
        temp = subprocess.check_output(["vcgencmd", "measure_temp"]).decode("utf-8").split("=")[1]
        self.info = {
            "ip": get_ip(),
            "memory": {
                "total": round(memory.total / (1024 * 1024), 2),
                "avail": round(memory.available / (1024 * 1025), 2)
            },
            "temp": temp
        }
