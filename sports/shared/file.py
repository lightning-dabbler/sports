import os
import pathlib

import smart_open


def open(uri, mode="rb", compression=None, transport_params=None, **kwargs):
    if "AUTO_MAKEDIRS" in os.environ and smart_open.parse_uri(uri).scheme == "file":
        pathlib.Path(uri).parent.mkdir(parents=True, exist_ok=True)
    file_ = smart_open.open(uri, mode=mode, compression=compression, transport_params=transport_params, **kwargs)
    return file_
