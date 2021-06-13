from datetime import datetime
from pprint import pformat

from config import debug


def log(*args):
    if not debug: return
    args = [i if i is not None else '' for i in args]
    args = [pformat(i) if debug > 1 else str(i) for i in args]
    print(f"[{datetime.now()}] {' '.join(args)}")
