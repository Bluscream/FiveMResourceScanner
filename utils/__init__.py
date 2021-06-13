from datetime import datetime, timedelta
import logging
from pathlib import Path
from pprint import pformat
from typing import Sized
from pickle import dumps, loads

logging.basicConfig(format='[%(asctime)s] %(levelname)s > %(message)s', level=logging.DEBUG)

class Logger(object):
    warnings = 0
    errors = 0
    def log(self, *args): self._log(lvl=logging.INFO, args=args)
    def info(self, *args): self._log(lvl=logging.INFO, args=args)
    def warn(self, *args): self.warnings += 1; self._log(lvl=logging.WARNING, args=args)
    def error(self, *args): self.errors += 1; self._log(lvl=logging.ERROR, args=args)
    def _log(self, lvl: int, args):
        # if not debug: return
          # 1 < 2 and 3 > 1: return
        # if debug.value < LogLevel.WARNING.value and lvl.value > LogLevel.ERROR.value: return
        # if debug.value < LogLevel.INFO.value and lvl.value > LogLevel.WARNING.value: return
        args = [i if i is not None else '' for i in args]
        args = [pformat(i) if (type(i) is not str) else str(i) for i in args]
        # args = [i if type(i) is str else str(i) for i in args]
        logging.log(level=lvl, msg=' '.join(args))
        # print(f"[{datetime.now()}] {lvl} {' '.join(args)}")

logger = Logger()

def readable_timedelta(duration: timedelta):
    data = {}
    data['days'], remaining = divmod(duration.total_seconds(), 86_400)
    data['hours'], remaining = divmod(remaining, 3_600)
    data['minutes'], data['seconds'] = divmod(remaining, 60)

    time_parts = ((name, round(value)) for (name, value) in data.items())
    time_parts = [f'{value} {name[:-1] if value == 1 else name}' for name, value in time_parts if value > 0]
    if time_parts:
        return ' '.join(time_parts)
    else:
        return 'below 1 second'


def loadCache(file: Path):
    if not file.is_file():
        logger.log(file, "does not exist!")
        return
    logger.log("Loading cache from", file)
    mtime = datetime.fromtimestamp(file.stat().st_mtime)
    logger.log("Cache was last modified at", str(mtime))
    logger.log("Cache is", readable_timedelta(datetime.now() - mtime), "old")
    with open(file, "rb") as f:
        obj = loads(f.read())
        logger.log("Loaded", len(obj), "objects from", file)
        return obj


def saveCache(file: Path, obj: Sized):
    if file.is_file(): logger.log(file, "already exists!")
    logger.log("Saving", len(obj), "to", file)
    with open(file, "wb") as f:
        f.write(dumps(obj))
    logger.log("Saved cache to", file)
