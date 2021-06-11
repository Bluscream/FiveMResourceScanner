from textwrap import wrap
from typing import List, Optional
from dataclasses import dataclass
from enum import Enum
from os import path, walk, sep
from pprint import pprint
from classes.Resource import Resource
from discord_webhook import DiscordWebhook
from config import webhook_url, data_dir

datadir = data_dir
resources = list()
webhook = DiscordWebhook(
    url=webhook_url,
    content='')
#
"""
def getResourcesFromConfig(serverCfgDir: str):
    with open(path.join(serverCfgDir, "server.cfg"), "r+", encoding='utf-8', errors='ignore') as f:
        d = f.readlines()
        f.seek(0)
        resources.clear()
        for i in d:
            line = i.strip()
            resource = ConfigResourceEntry()
            if line.startswith("#"):
                line = i[1:].strip()
                resource.enabled = False
            if line.startswith("start "):
                resource.startmode = "start"
                resource.name = line.replace("start","").strip()
            elif line.startswith("ensure "):
                resource.startmode = "ensure"
                resource.name = line.replace("ensure","").strip()
            else:
                f.write(i)
            if resource.name != "":
                resources.append(resource)
        f.truncate()
    with open(path.join(serverCfgDir, "resources.cfg"), 'w') as resCfg:
        resCfg.writelines([(str(x)+"\n") for x in resources])
"""


def scanResources(resourcesDir):
    result = list()
    resourcesDir = path.normpath(resourcesDir)
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
                for (_, _, filenames) in walk(path.join(root, "stream")):
                    file: str
                    for file in filenames:
                        file = file.lower()
                        # if not file.split(".")[0].isalpha(): continue
                        if file.endswith(".yft") and not "_" in file:
                            res.spawnnames.add(
                                file.replace(".ytd", "").replace(".yft", "").replace("_hi", "").replace("+hi", ""))

            result.append(res)
        """
        if isCategory:
            tab = "\t" * len(dirPath)
            result.append(tab + sep.join(dirPath))
        else: pass # result.append("\t"+dirPath[-1])
        """
        # for subdir in subdirs:
        # if (subdir)
        # print('\t- subdirectory ' + subdir)

        # for filename in files:
        # file_path = path.join(root, filename)

        # print('\t- file %s (full path: %s)' % (filename, file_path))

        # with open(file_path, 'rb') as f:
    return result


_res = scanResources(path.join(datadir, "resources/"))
# _res.sort(key=lambda x: x.category, reverse=False)
txt = ""
len_template = 11
list_of_categories = dict()
for res in _res:
    if len(res.spawnnames) < 1: continue
    if res.category not in list_of_categories: list_of_categories[res.category] = list()
    list_of_categories[res.category].append(res)
for cat in list_of_categories:
    txt += cat + "\n"
    for res in list_of_categories[cat]:
        txt += f" {res.name}: {', '.join(res.spawnnames)}\n"
for chunk in [txt[i:i + 2000 - 11] for i in range(0, len(txt), 2000 - 11)]:
    webhook.content = "```yaml\n" + chunk + "```"
    webhook.execute()

# getResourcesFromConfig(datadir)
# pprint(resources)
