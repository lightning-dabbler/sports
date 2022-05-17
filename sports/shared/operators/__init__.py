import more_itertools
from loguru import logger
from smart_open.compression import get_supported_extensions

import sports.shared.file
import sports.shared.serde as serde


class Archiver:
    def __init__(
        self,
        data,
        base_uri,
        *,
        write_strategy=None,
        transport_params=None,
        file_type="json-lines",
        append=False,
        **kwargs,
    ):
        self.data = data

        default_strategy = {"compression": ".gz"}
        write_strategy = write_strategy or {}
        self.write_strategy = {**default_strategy, **write_strategy, "transport_params": transport_params}
        if self.write_strategy.get("compression") in get_supported_extensions():
            file_ext = serde.FILE_EXT[file_type] + self.write_strategy["compression"]
        else:
            file_ext = serde.FILE_EXT[file_type]
        self.base_uri = base_uri if base_uri.endswith(file_ext) else f"{base_uri}{file_ext}"
        self.serialization_strategy = serde.get_strategy(serde.SERIALIZER_REGISTRY, file_type)
        self.serialization_strategy_kwargs = {"append": append}
        action = serde.APPEND_ACTION.get(file_type, "ab") if append is True else serde.WRITE_ACTION.get(file_type, "wb")
        self.action = {"mode": action}
        self.written_file = None
        self.records_written = 0
        self.logger = logger.bind(__class_name__=self.__class__.__name__, __class__=self.__class__)

    def write(
        self,
    ):
        if self.data:
            (first), iterable = more_itertools.spy(self.data, 1)
            if not first:
                self.logger.critical("Source stream is empty!", stream=iterable)
                return
        else:
            self.logger.critical("Source stream is empty!", stream=self.data)
            return
        with sports.shared.file.open(self.base_uri, **self.action, **self.write_strategy) as f:
            self.records_written = self.serialization_strategy(f, iterable, **self.serialization_strategy_kwargs)
            self.written_file = self.base_uri
