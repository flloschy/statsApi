import os
from utility import makeResponse


def getDisk() -> list[str]:
    return os.popen('df --output="target" --output="pcent" -B KB').read().splitlines()


def cleanUp(line: list[list[str]]) -> list[list[str]]:
    return [char for char in line if char != ""]


def formatDisk(lines: list[str]) -> str:
    linesWithoutHeader = lines[1:]
    linesWithWords = [line.strip().split(" ") for line in linesWithoutHeader]

    cleanedLines = [cleanUp(word) for word in linesWithWords]

    output = ""
    for line in cleanedLines:
        disk = line[0]
        usage = line[1].replace("%", "")
        output += 'system_stats_disk_usage_percent{disk="' + \
            disk + '"} ' + usage + "\n"

    return output


def getSystemDiskUsage():
    return makeResponse(formatDisk(getDisk()))
