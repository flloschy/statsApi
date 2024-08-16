from utility import CONFIG
import requests
import json
from utility import makeResponse


def getCounts() -> str:
    url = CONFIG["jellyfinUrl"] + "Items/Counts"
    header = {
        "Authorization": "MediaBrowser Token=" + CONFIG["jellyfinApiKey"]
    }
    return requests.request("GET", url, headers=header).text


def formatCount(text: str):
    print(text)
    countData: dict = json.loads(text)

    output = ""

    for (item, count) in countData.items():
        if count == 0:
            continue
        output += "jellyfin_item_count{"
        output += f'item="{item}"'
        output += "} " + str(count) + "\n"

    return output


def getJellyfinItemCount():
    return makeResponse(formatCount(getCounts()))
