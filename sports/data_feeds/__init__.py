import os

import yaml
from loguru import logger

HERE = os.path.dirname(__file__)


def read_yaml_conf(filename):
    """
    Read YAML Configuration file into memory
    :param str filename: YAML File to read
    :return dict: Dictionary derived from YAML file
    """

    with open(filename, "rb") as f:
        data = f.read().decode("utf-8")
        data = yaml.safe_load(data)
        return data


def read_config(name, layer=None, subconfig=None):
    if layer:
        filename = os.path.join(HERE, layer, name)
    else:
        filename = os.path.join(HERE, name)
    config = read_yaml_conf(filename)
    if subconfig:
        config = config[subconfig]
    return config


# https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries
def merge_dicts(a, b, path=None):
    """Merges b into a
    Value at key_path1 of `b` will overwrite Value at key_path1 of `a`
    if keys are identical and values are not of type `dict`
    e.g.
    .. code-block:: python
        x = {"key1":5,"key2":"bar"}
        y = {"key1":"foo"}
        print(merge_dicts(x,y))
        {"key1":"foo","key2":"bar"}
    :param dict a
    :param dict b
    :return: dict `a`
    """

    if path is None:
        path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge_dicts(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                logger.debug("Conflict at %s" % ".".join(path + [str(key)]))
                a[key] = b[key]
        else:
            a[key] = b[key]
    return a
