import json
import os
import flask
CONFIG = json.load(open("./config.json", "r"))


def percent(x: str) -> float:
    try:
        return round(float(x.replace("%", "")), ndigits=2)
    except:
        return 0.0


def anyToKilloBytes(x: str) -> int:
    number = ""
    unit = ""

    unitTransformations = {
        "B": 0.001,
        "kB": 1,
        "KiB": 1024,
        "MB": 1000,
        "MiB": 1024 * 1024,
        "GB": 1000 * 1000,
        "GiB": 1024 * 1024 * 1024,
        "TB": 1000 * 1000 * 1000,
        "TiB": 1024 * 1024 * 1024 * 1024,
    }

    for char in x:
        if char in "0123456789.":
            number += char
        else:
            unit += char

    number = float(number)
    return round(number * unitTransformations[unit])


cache = {}


def readCache(file: str) -> dict:
    if file in cache.keys():
        return cache[file]

    location = CONFIG["cacheFolder"] + file + ".json"
    fileContent = json.load(
        open(location, "r")) if os.path.exists(location) else {}
    cache[file] = fileContent
    return fileContent


def writeCache(file: str, content: dict) -> None:
    cache[file] = content
    location = CONFIG["cacheFolder"] + file + ".json"
    json.dump(content, open(location, "w" if os.path.exists(location) else "x"))


def makeResponse(text):
    return flask.Response(text, content_type="text/plain")
