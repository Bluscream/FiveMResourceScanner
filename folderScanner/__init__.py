from pathlib import Path
from typing import List
from os import walk
from classes.Resource import Resource


class ResourceScanner(object):
    resourcesDir: Path
    resources: List[Resource]
    """ Next time lol
    def walk(self, path):
        for p in Path(path).iterdir():
            if p.is_dir():
                yield from walk(p)
                continue
            yield p.resolve()
    """
    def __init__(self, resourceDir):
        self.resourcesDir = Path(resourceDir)
        self.resources = self.scan()

    def scan(self):
        result = list()
        root = str(self.resourcesDir.absolute())
        for curDir, subdirs, files in walk(root):
            dirPath = Path(curDir.replace(root, "")).parent
            if len(dirPath) < 1: continue
            # isCategory = dirPath[-1].startswith("[")
            isResourceInRoot = len(dirPath) < 2 and not dirPath[0].startswith("[")
            isCategoryInRoot = len(dirPath) < 2 and dirPath[0].startswith("[")
            isResource = not isCategoryInRoot and (isResourceInRoot or dirPath[-2].startswith("["))
            if isResource:
                res = Resource(dirPath[-1], sep.join(dirPath[:-1]))
                if "stream" in subdirs:
                    res.spawnnames = set()
                    for (_, _, filenames) in walk(path.join(curDir, "stream")):
                        file: str
                        for file in filenames:
                            file = file.lower()
                            # if not file.split(".")[0].isalpha(): continue
                            if file.endswith(".yft") and not "_" in file:
                                res.spawnnames.add(
                                    file.replace(".ytd", "").replace(".yft", "").replace("_hi", "").replace("+hi", ""))
                pprint(res)
                result.append(res)
        return result


    def log(self):
        for datadir, webhook_url in servers.items():
            now = datetime.datetime.now()
            webhook = DiscordWebhook(
                url=webhook_url,
                content='')
            _res = self.scan(path.join(datadir, "resources/"))
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
            webhook.content = f"**START OF {name_count} SPAWNNAMES FOR \"{datadir}\" [{now}]**"
            webhook.execute()
            for chunk in [txt[i:i + 2000 - 11] for i in range(0, len(txt), 2000 - 11)]:
                webhook.content = "```yaml\n" + chunk + "```"
                webhook.execute()
            webhook.content = f"**END OF {name_count} SPAWNNAMES FOR \"{datadir}\" [{datetime.datetime.now()}]**"
            webhook.execute()