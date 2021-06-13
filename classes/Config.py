from json import dumps, loads
from pathlib import Path
from typing import List, Optional

from classes.Resource import ConfigResourceEntry
from utils import log


class Config(object):
    file: Path  # path.join(serverCfgDir, "server.cfg")
    cacheFile: Optional[Path]
    resources: Optional[List[ConfigResourceEntry]]

    def __init__(self, filePath: Path):
        self.file = filePath
        self.cacheFile = self.file.parent.joinpath("cache.json")
        log("Config", self.file, self.cacheFile)
        # self.resources = self.getResources()

    def getResources(self, clearServerConfig=False) -> List[ConfigResourceEntry]:
        result = list()
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
                    result.append(resource)
            if clearServerConfig: f.truncate()
        return result

    def writeResourcesConfig(self, filename="resources.cfg"):
        with open(self.file.parent.joinpath(filename), 'w') as resCfg:
            resCfg.writelines([(str(x) + "\n") for x in sorted(self.resources, key=lambda x: x.priority, reverse=True)])

    def loadBackup(self):
        with open(self.cacheFile, "r") as f:
            self.resources = loads(f.read())

    def saveBackup(self):
        with open(self.cacheFile, "w") as f:
            f.write(dumps(self.resources))
