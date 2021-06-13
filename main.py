from utils import log
log("STARTED")
from folderScanner import *
from config import servers
for datadir, webhook_url in servers.items():
    scanner = ResourceScanner(datadir, webhook_url)
    scanner.resources = scanner.scan()
    # scanner.log()
# getResourcesFromConfig(datadir)
# pprint(resources)
log("FINISHED")