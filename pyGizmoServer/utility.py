import yaml
import copy
import logging
import sys
import aiohttp

logger = logging.getLogger('gizmoLogger')


def setuplog(cfg):
    logger = logging.getLogger("gizmoLogger")
    logger.setLevel(getattr(logging, cfg.logging.file.loglevel))
    formatter = logging.Formatter(
        fmt="%(asctime)s.%(msecs)03d %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    filehandler = logging.FileHandler(filename=cfg.logging.file.filename, mode="w")
    filehandler.setLevel(getattr(logging, cfg.logging.file.loglevel))
    filehandler.setFormatter(formatter)
    consolehandler = logging.StreamHandler(sys.stdout)
    consolehandler.setLevel(getattr(logging, cfg.logging.console.loglevel))
    consolehandler.setFormatter(formatter)
    logger.addHandler(filehandler)
    logger.addHandler(consolehandler)
    logger.propagate = False


def makeresolver(schema) -> callable:
    def f(d, p, r):
        count = d.get("$count")
        if count:
            d = copy.deepcopy(d)
            del d["$count"]
            for i in range(count):
                f(d, f"{p}/{i}", r)
            return
        if d.get("$type"):
            res = copy.deepcopy(d)
            if res.get("args") is not None:
                res["args"].extend([int(i) for i in p.split("/") if i.isdigit()])
            r[p] = res
            return
        for k, v in d.items():
            if v.get("$type"):
                res = copy.deepcopy(v)
                if res.get("args") is not None:
                    res["args"].extend([int(i) for i in p.split("/") if i.isdigit()])
                if not v.get("$count"):
                    r[p] = res
            f(v, f"{p}/{k}", r)

    propsdict = {}
    f(schema, "", propsdict)
    return lambda x: propsdict.get(x)


class DotDict(dict):
    def __getattr__(self, item):
        val = self[item]
        if isinstance(val, dict):
            return DotDict(val)
        else:
            return val


def loadconfig(filename):
    try:
        with open(f"./config/{filename}.yml") as f:
            return DotDict(yaml.load(f, Loader=yaml.CLoader))
    except Exception:
        with open(f"./config/{filename}.yml") as f:
            return DotDict(yaml.load(f, Loader=yaml.FullLoader))
    except Exception as e:
        print(f"{e}")
        return None


def ensurelist(item):
    return item if isinstance(item, list) else [item]


def log(msg):
    logger.info(f"{sys._getframe(1).f_code.co_name}: {msg}")


def debug(msg):
    if not logger.isEnabledFor(logging.DEBUG):
        return
    logger.debug(f"{sys._getframe(1).f_code.co_name}: {msg}")


class Error():
    def __init__(self, message=None):
        self.message = message

    def get_response(self):
        return [aiohttp.web.json_response({"error": self.message})]