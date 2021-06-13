from pickle import dumps, loads
from pathlib import Path
from shutil import copy
from typing import List, Optional, Set

from classes.Resource import ConfigResourceEntry
from utils import *
logger = Logger()

class Config(object):
    file: Path  # path.join(serverCfgDir, "server.cfg")
    cacheFile: Optional[Path]
    resources: Optional[Set[ConfigResourceEntry]]

    def __init__(self, filePath: Path):
        self.file = filePath
        self.cacheFile = self.file.parent.joinpath("cache.json")
        logger.log("new Config", self.file, self.cacheFile)
        # self.resources = self.loadCache()
        # self.resources = self.getResources()

    def getResources(self, clearServerConfig=False) -> set[ConfigResourceEntry]:
        result = set()
        with open(self.file.absolute(), "r+" if clearServerConfig else "r", encoding='utf-8', errors='ignore') as f:
            d = f.readlines()
            if clearServerConfig: f.seek(0)
            _i = len(d)
            for i in d:
                _i-=1
                line = i.strip()
                resource = ConfigResourceEntry()
                if line.startswith("#"):
                    line = i[1:].strip()
                    resource.enabled = False
                if line.startswith("start "):
                    resource.startmode = "start"
                    resource.name = line.replace("start", "").strip()
                elif line.startswith("ensure "):
                    resource.startmode = "ensure"
                    resource.name = line.replace("ensure", "").strip()
                elif clearServerConfig:
                    f.write(i)
                if resource.name != "":
                    resource.priority = _i
                    result.add(resource)
            if clearServerConfig: f.truncate()
        return result

    def writeResourcesConfig(self, filename="resources.cfg"):
        file = self.file.parent.joinpath(filename)
        logger.log("Writing", file)
        with open(file, 'w') as resCfg:
            resCfg.writelines([(str(x) + "\n") for x in sorted(self.resources, key=lambda x: x.priority, reverse=True)])

    def saveBackup(self):
        bakfile = self.file.with_suffix(self.file.suffix + '.bak')
        logger.log("copying", self.file, "to", bakfile)
        copy(self.file, bakfile)

    def loadCache(self):
        return loadCache(self.cacheFile)

    def saveCache(self):
        saveCache(self.cacheFile, self.resources)