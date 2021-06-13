from os import walk, sep, path
from pathlib import Path
from typing import List, Set, Optional

from discord_webhook import DiscordWebhook

from classes.Resource import Resource
from utils import *
logger = Logger()


class ResourceScanner(object):
    resourcesDir: Path
    webhook: DiscordWebhook
    resources: Optional[List[Resource]]
    """ Next time lol
    def walk(self, path):
        for p in Path(path).iterdir():
            if p.is_dir():
                yield from walk(p)
                continue
            yield p.resolve()
    """

    def __init__(self, resourcesDir: Path, webhook_url: str):
        self.resourcesDir = resourcesDir
        self.webhook = DiscordWebhook(url=webhook_url, content='')
        self.cacheFile = self.resourcesDir.parent.joinpath("resources.json")
        logger.log("new ResourceScanner", self.resourcesDir, webhook_url, self.cacheFile)
        self.resources = self.loadCache()
        # self.resources = self.scan()

    def scan(self):
        result = list()
        resourcesDir = str(self.resourcesDir.absolute())
        resCount = 0; catCount = 0; spawnCount = 0;dirCount = 0
        for root, subdirs, files in walk(resourcesDir):
            # logger.log(root)
            dirPath = root.replace(resourcesDir, "").split(sep)[1:]
            dirPathLen = len(dirPath)
            if dirPathLen < 1: continue
            elif dirPathLen < 2: pass
            isCategory = dirPath[-1].startswith("[")
            inRoot = dirPathLen < 2
            isCategoryInRoot = inRoot and isCategory
            isResourceInRoot = inRoot and not isCategory
            isResource = not isCategory and not isCategoryInRoot and (isResourceInRoot or dirPath[-2].startswith("["))
            # if isCategory or isResource: logger.log("dirPathLen:", dirPathLen, "| isCategory:", isCategory, "| isResource:", isResource, "| inRoot:", inRoot, "| isCategoryInRoot:", isCategoryInRoot, "| isResourceInRoot:", isResourceInRoot)
            if isResource:
                resCount +=1
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
                    if len(res.spawnnames) > 0: spawnCount += 1
                result.append(res)
            elif isCategory: catCount += 1
            else: dirCount += 1

        logger.log("Found",spawnCount,"spawnables in",resCount,"resources in",catCount,"categories in",dirCount,"folders")
        return result

    def log(self):
        now = datetime.now()
        _res = self.resources if self.resources is not None else self.scan()
        _res.sort(key=lambda x: x.category, reverse=False)
        txt = ""
        list_of_categories = categorizeResources(self.resources)
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

    def loadCache(self):
        return loadCache(self.cacheFile)

    def saveCache(self):
        saveCache(self.cacheFile, self.resources)