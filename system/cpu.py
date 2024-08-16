import psutil
from utility import makeResponse


def getCpu() -> list[int]:
    return psutil.cpu_percent(interval=2, percpu=True)


def systemStats(codeUsage: list[int]) -> str:
    cpuAverage = round(sum(codeUsage)/len(codeUsage), ndigits=2)

    output = ""
    output += "system_stats_cpu_usage_total " + str(cpuAverage) + "\n"

    for core, usage in enumerate(codeUsage):
        output += 'system_stats_cpu_usage{core="' + \
            str(core+1) + '"} ' + str(usage) + "\n"

    return output


def getSystemCpuUsage():
    return makeResponse(systemStats(getCpu()))
