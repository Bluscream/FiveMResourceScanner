from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConfigResourceEntry(object):
    name: str = ""
    startmode: str = "start"
    enabled: bool = True
    priority: int = 0

    def __str__(self):
        return f"{'' if self.enabled else '#'}{self.startmode} {self.name}"

    def __hash__(self):
        return hash(self.name) ^ hash(self.startmode) ^ hash(self.enabled) ^ hash(self.priority)


@dataclass
class Resource(object):
    name: str = ""
    category: str = ""
    spawnnames = set()  # : set[str] = field(default_factory=set)
    cfgentry: ConfigResourceEntry = None
    path: Path = Path()

    def getCategoryName(self):
        return self.category.split('/')[-1].replace('[','').replace(']','')

    def __hash__(self):
        return hash(self.name) ^ hash(self.category) ^ hash(self.cfgentry)
