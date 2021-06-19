from os import walk, sep, path, linesep
from pathlib import Path
from shutil import copyfile
from typing import List, Set, Optional

from discord_webhook import DiscordWebhook

from classes.Resource import Resource
from utils import *
logger = Logger()


class ResourceScanner(object):
    resourcesDir: Path
    webhook: DiscordWebhook
    resources: Optional[List[Resource]]
    class counts():
        spawnables = 0
        resources = 0
        categories = 0
        directories = 0
        missing_config_entry = 0
        missing_directory = 0
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
                self.counts.resources +=1
                catPath = dirPath[:-1]
                res = Resource(dirPath[-1], sep.join(catPath))
                # catPath[-1].replace("[","").replace("]","")
                res.path = Path(root)
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
                    if len(res.spawnnames) > 0: self.counts.spawnables += 1
                result.append(res)
            elif isCategory: self.counts.categories += 1
            else: self.counts.directories += 1

        logger.log("Found",self.counts.spawnables,"spawnables in",self.counts.resources,"resources in",self.counts.categories,"categories in",self.counts.directories,"folders")
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

    def generateDefaultELSFiles(self, targetPath: Path):
        lines: set
        with open("cache/els_vehicles.txt") as f:
            lines = set(filter(None, (line.strip() for line in f)))
        logger.info(lines)
        for line in lines:
            target = targetPath.joinpath(line+".xml")
            if target.is_file(): continue
            else: target.parent.mkdir(parents=True, exist_ok=True)
            copyfile("cache/non-els.xml", target)

    def generateVehicleShopSQL(self, targetPath: Path, dbName: str, namePattern: str = "{category}", tableName: str = "vehicles", defaultPrice: int = 1000000):
        with open(targetPath, 'w') as f:
            f.write(f"-- GENERATED AT {datetime.now()} BY https://github.com/Bluscream/FiveMResourceScanner{linesep}")
            f.write(f"-- GENERATED FROM {self.counts.spawnables} Spawnables | {self.counts.resources} Resources | {self.counts.categories} Categories | {self.counts.directories} Folders{linesep}")
            f.write(f"USE `{dbName}`{linesep}{linesep}")
            for resource in self.resources:
                for spawnname in resource.spawnnames:
                    "Insert IGNORE into `vehicles` (`name`, `model`, `price`, `category`) VALUES('gtrnismo17', 'gtrnismo17', 1000000, '[cars]/[nissan]');"
                    txt = f"Insert into `{tableName}` (`name`, `model`, `price`, `category`) VALUES('{namePattern.format(model=spawnname, resource=resource.name, category=resource.category.split('/')[-1].replace('[','').replace(']',''))}', '{spawnname}', {defaultPrice}, '{resource.category}'){linesep}"
                    """BEGIN
   IF NOT EXISTS (SELECT * FROM `{tableName}` WHERE `model` = "{spawnname}")
   BEGIN
       INSERT INTO `{tableName}` (`name`, `model`, `price`, `category`) VALUES ("{namePattern.format(model=spawnname, resource=resource.name, category=resource.category)}", "{spawnname}", {defaultPrice}, "{resource.category}")
   END
END

"""
                    f.write(txt)

    def generateELSFiles(self):
        for res in [x for x in self.resources if x.spawnnames]:
            pass # TODO IMPLEMENT

    def loadCache(self):
        return loadCache(self.cacheFile)
    def saveCache(self):
        saveCache(self.cacheFile, self.resources)