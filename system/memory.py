import os
from utility import makeResponse


def getMemory() -> list[str]:
    return os.popen("free --kilo").read().splitlines()


def cleanUp(line: list[list[str]]) -> list[list[str]]:
    return [char for char in line if char != ""]


def formatMemory(lines: list[str]) -> str:
    linesWithoutHeader = lines[1:]
    linesWithWords = [line.strip().split(" ") for line in linesWithoutHeader]
    cleanedLines = [cleanUp(word) for word in linesWithWords]

    totalMemory = int(cleanedLines[0][1])
    totalSwap = int(cleanedLines[1][1])

    usedMemory = int(cleanedLines[0][2])
    usedSwap = int(cleanedLines[1][2])

    memory = round(usedMemory / totalMemory * 100, ndigits=2)
    swap = round(usedSwap / totalSwap * 100, ndigits=2)

    output = ""
    output += "system_stats_memory_used_percent " + str(memory) + "\n"
    output += "system_stats_swap_used_percent " + str(swap) + "\n"

    return output


def getSystemMemoryUsage():
    return makeResponse(formatMemory(getMemory()))
