from datetime import datetime
from json import loads, dumps
from pathlib import Path
from typing import List
from os import walk, sep, path

from discord_webhook import DiscordWebhook

from classes.Resource import Resource
from utils import log


class ResourceScanner(object):
    resourcesDir: Path
    webhook: DiscordWebhook
    resources: List[Resource]
    """ Next time lol
    def walk(self, path):
        for p in Path(path).iterdir():
            if p.is_dir():
                yield from walk(p)
                continue
            yield p.resolve()
    """
    def __init__(self, resourceDir, webhook_url):
        self.resourcesDir = Path(resourceDir)
        self.webhook = DiscordWebhook(url=webhook_url, content='')
        self.cacheFile = self.resourcesDir.parent.joinpath("resources.json")
        log("ResourceScanner", self.resourcesDir, webhook_url, self.cacheFile)
        # self.resources = self.scan()

    def scan(self):
        result = list()
        resourcesDir = str(self.resourcesDir.joinpath("resources/").absolute())
        for root, subdirs, files in walk(resourcesDir):
            dirPath = root.replace(resourcesDir, "").split(sep)[1:]
            if len(dirPath) < 1: continue
            # isCategory = dirPath[-1].startswith("[")
            isResourceInRoot = len(dirPath) < 2 and not dirPath[0].startswith("[")
            isCategoryInRoot = len(dirPath) < 2 and dirPath[0].startswith("[")
            isResource = not isCategoryInRoot and (isResourceInRoot or dirPath[-2].startswith("["))
            if isResource:
                res = Resource(dirPath[-1], sep.join(dirPath[:-1]))
                if "stream" in subdirs:
                    res.spawnnames = set()
                    for (_, _, filenames) in walk(path.join(root, "stream")):
                        file: str
                        for file in filenames:
                            file = file.lower()
                            # if not file.split(".")[0].isalpha(): continue
                            if file.endswith(".yft") and not "_" in file:
                                res.spawnnames.add(
                                    file.replace(".ytd", "").replace(".yft", "").replace("_hi", "").replace("+hi", ""))
                log(res)
                result.append(res)
        return result


    def log(self):
        now = datetime.now()
        _res = self.scan()
        _res.sort(key=lambda x: x.category, reverse=False)
        txt = ""
        list_of_categories = dict()
        for res in _res:
            if len(res.spawnnames) < 1: continue
            if res.category not in list_of_categories: list_of_categories[res.category] = list()
            list_of_categories[res.category].append(res)
        name_count = 0
        for cat in list_of_categories:
            txt += cat + "\n"
            for res in list_of_categories[cat]:
                txt += f" {res.name}: {', '.join(res.spawnnames)}\n"
                name_count += len(res.spawnnames)
        self.webhook.content = f"**START OF {name_count} SPAWNNAMES FOR \"{self.resourcesDir.parent}\" [{now}]**"
        self.webhook.execute()
        for chunk in [txt[i:i + 2000 - 11] for i in range(0, len(txt), 2000 - 11)]:
            self.webhook.content = "```yaml\n" + chunk + "```"
            self.webhook.execute()
        self.webhook.content = f"**END OF {name_count} SPAWNNAMES FOR \"{self.resourcesDir.parent}\" [{datetime.now()}]**"
        self.webhook.execute()

    def loadBackup(self):
        with open(self.cacheFile, "r") as f:
            self.resources = loads(f.read())

    def saveBackup(self):
        with open(self.cacheFile, "w") as f:
            f.write(dumps(self.resources))