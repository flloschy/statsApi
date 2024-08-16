from utility import percent, anyToKilloBytes, readCache, writeCache, makeResponse
import os


def getDocker() -> list[str]:
    return os.popen("sudo docker stats --no-stream --no-trunc").read().splitlines()


def formatToCSV(lines: list[str]) -> list[str]:
    linesWithoutHeader = lines[1:]

    output = []

    for line in linesWithoutHeader:
        words = line.strip().replace(" / ", ";").split(' ')
        cleaned = [char for char in words if char != ""]
        csv = ";".join(cleaned)
        values = csv.split(";")

        outputLine = []
        for i, value in enumerate(values):
            if value.endswith("%"):
                outputLine.append(str(percent(value)))
            elif value.endswith("B") and i != 0:  # 0 = container id
                outputLine.append(str(anyToKilloBytes(value)))
            else:
                outputLine.append(value)

        output.append(";".join(outputLine))

    return output


def formatCSV(lines: list[str]):
    cache = readCache("dockerNetwork")
    CSVHeaders = ["container_id", "container_name", "cpu_usage_percent",
                  "memory_used_kilobyte", "memory_total_kilobyte", "memory_used_percent",
                  "network_download_total_kilobytes", "network_upload_total_kilobytes",
                  "disk_read_total_kilobytes", "disk_write_total_kilobytes", "pid"]

    intHeaders = ["network_download_total_kilobytes",
                  "network_upload_total_kilobytes", "disk_read_total_kilobytes",
                  "disk_write_total_kilobytes"]

    selectedHeaders = ["cpu_usage_percent", "memory_used_percent",
                       "network_download_total_kilobytes", "network_upload_total_kilobytes",
                       "disk_read_total_kilobytes", "disk_write_total_kilobytes"]

    output = ""
    for line in lines:
        values = line.split(";")
        activeContainer = values[1]
        for head, value in zip(CSVHeaders, values):
            if head not in selectedHeaders:
                continue
            if head in intHeaders:
                cacheTarget = activeContainer + "_" + head
                v = int(value)
                lastValue = cache[cacheTarget] if cacheTarget in cache.keys(
                ) else v
                value = max(0, v - lastValue)
                cache[cacheTarget] = v
            output += f"docker_stats_{head}"
            output += '{container="' + activeContainer + '"} '
            output += str(value) + "\n"

    writeCache("dockerNetwork", cache)
    return output

def getDockerStats():
    return makeResponse(formatCSV(formatToCSV(getDocker())))
