from utility import CONFIG

from docker.stats import getDockerStats
from jellyfin.count import getJellyfinItemCount
from jellyfin.sessions import getJellyfinSessions
from system.cpu import getSystemCpuUsage
from system.disk import getSystemDiskUsage
from system.memory import getSystemMemoryUsage
from system.temperature import getSystemTemperature

import flask
import waitress
import os
import setproctitle


endPoints = {
    "/docker": getDockerStats,
    "/jf_items": getJellyfinItemCount,
    "/jf_sessions": getJellyfinSessions,
    "/cpu": getSystemCpuUsage,
    "/disk": getSystemDiskUsage,
    "/memory": getSystemMemoryUsage,
    "/temp": getSystemTemperature
}


api = flask.Flask(__name__)

for endPoint, fn in endPoints.items():
    api.add_url_rule(endPoint, view_func=fn)


if __name__ == '__main__':
    setproctitle.setproctitle("statsApi")
    waitress.serve(api, host="127.0.0.1", port=CONFIG["port"])
    # api.run(host="127.0.0.1", port=CONFIG["port"])
