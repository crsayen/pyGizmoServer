import yaml
import copy
import logging
import sys
import aiohttp
import json
from typing import Dict, List, Union, Any

logger = logging.getLogger('gizmoLogger')


def setuplog(cfg) -> None:
    """Configures logging for the application.

    once set up, modules can import utility.log and utility.debug to
    log informational and debug messages respectively.

    Arguments:
        cfg {DotDict} -- The application cfg Dict, which has information
            on loglevels for both file and console logging.
    """
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


def makeresolver(schema: Dict) -> callable:
    """Takes a schema dict, and returns a lookup function.

        Recursively walks the passed schema and generates a
        lookup table of <path> -> <properties> for the schema.
        returns a getter for the lookup table.

    Arguments:
        schema {Dict} -- A controller schema

    Returns:
        callable -- A getter function that, given a path, returns
            schema properties at that path.
    """
    def f(dictionary, path, result):
        count = dictionary.get("$count")
        if count:
            dictionary = copy.deepcopy(dictionary)
            del dictionary["$count"]
            for i in range(count):
                f(dictionary, f"{path}/{i}", result)
            return
        if dictionary.get("$type"):
            res = copy.deepcopy(dictionary)
            res["$args"] = res["$args"] if res.get("$args") else []
            res["$args"].extend([int(i) for i in path.split("/") if i.isdigit()])
            result[path] = res
            return
        for k, v in dictionary.items():
            if v.get("$type"):
                res = copy.deepcopy(v)
                if res.get("$args") is not None:
                    res["$args"].extend([int(i) for i in path.split("/") if i.isdigit()])
                if not v.get("$count"):
                    result[path] = res
            f(v, f"{path}/{k}", result)

    propsdict = {}
    f(schema, "", propsdict)
    return lambda x: propsdict.get(x)


class DotDict(dict):
    """A dict that can be accessed with dot-notation.

    Arguments:
        dict {Dict} -- The Dict to convert

    Returns:
        Dict -- A dot-notation-accessible Dict
    """
    def __getattr__(self, item):
        val = self[item]
        if isinstance(val, dict):
            return DotDict(val)
        else:
            return val


def loadconfig(filename: str):
    """Creates a configuration data Dict based on a YAML
        file

    options[0] is always a config file name. otherwise, the
        default configuration is loaded.

    Arguments:
        filename {str} -- The name of a YAML file in pyGizmoServer.config

    Returns:
        DotDict -- A dict which provides a means to lookup configuration
            information.
    """
    try:
        with open(f"./config/{filename}.yml") as f:
            return DotDict(yaml.load(f, Loader=yaml.CLoader))
    except Exception:
        with open(f"./config/{filename}.yml") as f:
            return DotDict(yaml.load(f, Loader=yaml.FullLoader))
    except Exception as e:
        print(f"{e}")
        return None



def ensurelist(item: Union[Any, List[Any]]) -> List[Any]:
    return item if isinstance(item, list) else [item]


def log(msg: str) -> None:
    logger.info(f"{sys._getframe(1).f_code.co_name}: {msg}")


def debug(msg: str) -> None:
    if not logger.isEnabledFor(logging.DEBUG):
        return
    logger.debug(f"{sys._getframe(1).f_code.co_name}: {msg}")


class Error():
    def __init__(self, message=None):
        self.message = message

    def get_response(self):
        return aiohttp.web.json_response([{"error": self.message}])