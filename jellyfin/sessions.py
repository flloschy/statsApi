import requests
import json
from utility import CONFIG, readCache, makeResponse, writeCache


def getSessions() -> str:
    url = CONFIG["jellyfinUrl"] + "Sessions"
    header = {
        "Authorization": "MediaBrowser Token=" + CONFIG["jellyfinApiKey"]
    }
    return requests.request("GET", url, headers=header).text


def formatSession(text: str) -> str:
    sessionData = json.loads(text)
    cache = readCache("jellyfinSessions")

    output = ""
    activeUsers = []

    for state in sessionData:
        try:
            user = state["UserName"]
            title = state["NowPlayingItem"]["Name"]
            activeUsers.append(user)

            type_ = state["NowPlayingItem"]["MediaType"]
            muted = state["PlayState"]["IsMuted"]
            paused = state["PlayState"]["IsPaused"]

            code = "".join([
                "Paused " if paused else "Playing ",
                "muted " if muted else "",
                type_
            ])

            uid = title + code

            # if user in cache.keys():
            #     if cache[user] == uid:
            #         continue
            cache[user] = None

            output += 'jellyfin_active_session{'
            output += f'user="{user}",title="{title}",state="{code}"'
            output += "} 1\n"
        except KeyError:
            continue

    usersToDelteFromCache = []

    for user in cache.keys():
        if user not in activeUsers:
            output += "jellyfin_active_session{"
            output += f'user="{user}",title="Nothing",state="Stopped"'
            output += "} 1\n"
            usersToDelteFromCache.append(user)

    writeCache("jellyfinSessions", cache)

    return output


def getJellyfinSessions():
    return makeResponse(formatSession(getSessions()))
