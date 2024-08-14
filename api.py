import flask
import os
import json
import psutil
import waitress


def getDockerStats() -> list[str]:
    return os.popen("sudo docker stats --no-stream --no-trunc").readlines()


def getMemory():
    return os.popen("free --kilo").readlines()


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
        "GiB": 1024 * 1024 * 1024
    }

    for char in x:
        if char in "0123456789.":
            number += char
        else:
            unit += char

    number = float(number)
    return round(number * unitTransformations[unit])


def parseDockerStatsToCSV(lines: list[str]) -> list[str]:
    csvLines = []
    for line in lines[1:]:
        csvLine = []
        values = line.strip().replace(' / ', ';').split(' ')
        values = [char for char in values if char != ""]
        values = ";".join(values)
        values = values.split(";")

        for i, value in enumerate(values):
            if value.endswith("%"):
                csvLine.append(str(percent(value)))
            elif value.endswith("B") and i != 0:
                csvLine.append(str(anyToKilloBytes(value)))
            else:
                csvLine.append(value)

        csvLines.append(";".join(csvLine))
    return csvLines


def csvToData(lines: list[str]) -> str:
    cache = {}
    try:
        cache = json.load(open("./cache.json", "r"))
    except:
        pass
    headers = ["container_id", "container_name", "cpu_usage_percent", "memory_used_kilobyte", "memory_total_kilobyte", "memory_used_percent",
               "network_download_total_kilobytes", "network_upload_total_kilobytes", "disk_read_total_kilobytes", "disk_write_total_kilobytes", "pid"]
    intHeaders = ["network_download_total_kilobytes", "network_upload_total_kilobytes",
                  "disk_read_total_kilobytes", "disk_write_total_kilobytes"]
    selectedHead = ["cpu_usage_percent", "memory_used_percent", "network_download_total_kilobytes",
                    "network_upload_total_kilobytes", "disk_read_total_kilobytes", "disk_write_total_kilobytes"]

    output = ""
    for line in lines:
        containerName = ""
        for i, value in enumerate(line.split(";")):
            if i == 1:
                containerName = value
            for head in selectedHead:
                if i == headers.index(head):
                    cacheHead = containerName + "_" + head
                    if head in intHeaders:
                        v = int(value)
                        if (cacheHead not in cache.keys()):
                            cache[cacheHead] = v
                        value = max(0, v - cache[cacheHead])
                        cache[cacheHead] = v
                    output += "docker_stats_" + head + \
                        '{container="' + containerName + '"} ' + \
                        str(value) + "\n"

    json.dump(cache, open("./cache.json", "w"))
    return output


def memoryToData(lines: list[str]) -> str:
    values = lines[1:]
    values = [line.split(" ") for line in values]
    values = [[char.strip().replace(":", "")
               for char in line if char != ""] for line in values]

    memoryTotal = int(values[0][1])
    memoryUsed = int(values[0][2])
    memoryPercent = round(memoryUsed / memoryTotal * 100, ndigits=2)

    swapTotal = int(values[1][1])
    swapUsed = int(values[1][2])
    swapPercent = round(swapUsed / swapTotal * 100, ndigits=2)

    return "system_stats_memory_used_percent " + str(memoryPercent) + \
        "\nsystem_stats_swap_used_percent " + str(swapPercent) + "\n"


def getDisk() -> list[str]:
    return os.popen('df --output="target" --output="pcent" -B KB').readlines()


def diskToData(lines: list[str]) -> str:
    values = lines[1:]
    values = [[char for char in line.strip().split(" ") if char != ""]
              for line in values]
    output = ""

    for value in values:
        output += 'system_stats_disk_usage_percent{disk="' + \
            value[0] + '"} ' + value[1].replace("%", "") + "\n"

    return output


def systemStats() -> str:
    cores = psutil.cpu_percent(interval=0.1, percpu=True)
    out = "system_stats_cpu_usage_total " + \
        str(round(sum(cores)/len(cores), ndigits=1)) + "\n"
    for i, core in enumerate(cores):
        out += 'system_stats_cpu_usage{core="' + \
            str(i+1) + '"} ' + str(core) + "\n"
    return out


def dockerMetrics():
    stats = getDockerStats()
    csv = parseDockerStatsToCSV(stats)
    dockerData = csvToData(csv)
    return dockerData


def serverMetrics():
    memory = getMemory()
    memoryData = memoryToData(memory)

    disk = getDisk()
    diskData = diskToData(disk)

    cpu = systemStats()
    return memoryData + diskData + cpu


api = flask.Flask(__name__)


@api.route("/docker", methods=["GET"])
def get_docker():
    return flask.Response(dockerMetrics(), content_type="text/plain")


@api.route("/system", methods=["GET"])
def get_system():
    return flask.Response(serverMetrics(), content_type="text/plain")


if __name__ == '__main__':
    waitress.serve(api, host="127.0.0.1", port=1234)