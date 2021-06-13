from classes.Config import Config
from utils import log

log("STARTED")
from folderScanner import *
from classes.Config import Config
from config import servers

for _datadir, webhook_url in servers.items():
    datadir = Path(_datadir)
    scanner = ResourceScanner(datadir.joinpath("resources/"), webhook_url)
    scanner.resources = scanner.scan()
    for resource in scanner.resources:
        log(resource)

    config = Config(datadir.joinpath("server.cfg"))
    config.resources = config.getResources()
    for resource in config.resources:
        log(resource)
    config.writeResourcesConfig()
    # scanner.log()
# getResourcesFromConfig(datadir)
# pprint(resources)
log("FINISHED")
