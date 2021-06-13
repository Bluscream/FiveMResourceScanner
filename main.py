import datetime
from os import path, walk, sep
from pprint import pprint
from classes.Resource import Resource, ConfigResourceEntry
from discord_webhook import DiscordWebhook
from config import servers
from typing import List, Optional
from dataclasses import dataclass, field
from enum import Enum
from folderScanner import *
from configScanner import *

scanner =
logResources()
# getResourcesFromConfig(datadir)
# pprint(resources)
