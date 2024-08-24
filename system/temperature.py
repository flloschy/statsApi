import os
from utility import makeResponse


def getTemp() -> str:
    return os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()

def format(temp: str) -> float:
    return "system_stats_temperature " + str(round(int(temp) / 1000, ndigits=3)) + "\n"

def getSystemTemperature():
    return makeResponse(formatMemory(getMemory()))
