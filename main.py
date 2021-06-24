from os import linesep
from config import *
from utils import Logger
logger = Logger()
logger.info("STARTED")
from folderScanner import *
from classes.Config import Config, ConfigResourceEntry
def main(*args):
    """
    datadir_slrp = Path(servers.items()[0][0])
    config_slrp = Config(datadir_slrp.joinpath("resources.cfg"))
    config_slrp.saveBackup()
    config_slrp.resources = config_slrp.getResources(False)
    datadir_test = Path(servers.items()[0][0])
    config_test = Config(datadir_slrp.joinpath("resources.cfg"))
    config_test.saveBackup()
    config_test.resources = config_test.getResources(False)
    exit()
    """
    for _datadir, webhook_url in servers.items():
        datadir = Path(_datadir)
        resdir = datadir.joinpath("resources/")
        scanner = ResourceScanner(resdir, webhook_url)
        scanner.resources = scanner.scan()
        # scanner.generateDefaultELSFiles(resdir.joinpath("[local]", "[ELS]", "elsvcfs"))
        scanner.generateVehicleShopSQL(targetPath=datadir.joinpath("vehicle_shop.sql"), namePattern="{model}", dbName=datadir.name)
        scanner.saveCache()
        resourcesCfgFile = datadir.joinpath("resources.cfg")
        config: Config
        if not resourcesCfgFile.is_file():
            serverCfgFile = datadir.joinpath("server.cfg")
            config = Config(serverCfgFile)
            config.saveBackup()
            config.resources = config.getResources(False) # TODO
            with open(config.file, 'a') as f:
                f.write(linesep+f"exec "+resourcesCfgFile.name)
        else:
            config = Config(resourcesCfgFile)
            config.resources = config.getResources()
        for resource in scanner.resources:
            existing_entries = [i for i in config.resources if i.name == resource.name]
            len_existing_entries = len(existing_entries)
            if (len_existing_entries > 0):
                if (len_existing_entries > 1): logger.warn(len(existing_entries), "CONFIG ENTRIES FOR", resource.name, ", ", [i.priority for i in existing_entries])
                resource.cfgentry = existing_entries[0]
            else:
                resource.cfgentry = ConfigResourceEntry(resource.name)
        # scanner.resources.sort(key=lambda x: x.cfgentry.priority, reverse=True)
        for resource in scanner.resources:
            logger.log(resource)
        for resource in config.resources:
            existing_entries = [i for i in scanner.resources if i.name == resource.name]
            if (len(existing_entries) > 1): logger.warn(len(existing_entries), "CONFIG ENTRIES FOR MISSING RESOURCE", resource.name)
        # config.resources = config.getResources()
        config.saveCache()
        config.writeResourcesConfig(scanner=scanner)

        # scanner.log()


if __name__ == "__main__":
    main()
# getResourcesFromConfig(datadir)
# pprint(resources)
logger._log(logging.WARNING if logger.warnings else logging.INFO, ["FINISHED with", logger.warnings, "warns and", logger.errors, "errors"])
