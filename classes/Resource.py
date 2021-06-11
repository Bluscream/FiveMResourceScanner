from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class ConfigResourceEntry(object):
    name: str = ""
    startmode: str = "start"
    enabled: bool = True
    priority: int = 0
    def __str__(self):
        return f"{'' if self.enabled else '#'}{self.startmode} {self.name}"

@dataclass
class Resource(object):
    name: str = ""
    category: str = ""
    spawnnames: set[str] = field(default_factory=set)
    cfgentry: ConfigResourceEntry = None