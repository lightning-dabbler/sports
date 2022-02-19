import json.decoder

import pendulum
from loguru import logger

import sports.shared.utils
from sports.shared.requests import make_request


class BaseContainer:
    def __init__(self, *args, raw_data=None, metadata=None, **kwargs):
        self.raw_data = raw_data or {}
        self.data_extracts = []
        self.metadata = metadata or {}
        self.logger = logger.bind(__class_name__=self.__class__.__name__, __class__=self.__class__)

    @classmethod
    def from_request(cls, url, *args, set_pull_metadata=True, request_kwargs=None, metadata=None, **kwargs):
        request_kwargs = request_kwargs or {}
        metadata = metadata or {}
        response = make_request(url, **request_kwargs)

        try:
            raw_data = response.json()
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
            logger.error("No JSON Payload at '{url}'", url=url)
            raw_data = {}

        if set_pull_metadata:
            headers = response.headers
            header_date = sports.operations.utils.header_date(headers)
            logger.debug("Headers Date '{header_date}'", header_date=header_date)
            timestamp = pendulum.from_format(header_date, "ddd[,] DD MMM YYYY HH[:]mm[:]ss z")
            logger.trace("Extracted Timestamp '{timestamp}'", timestamp=timestamp)
            pull_timestamp = timestamp.format("YYYY-MM-DD[T]HH:mm:ssZ")
            logger.debug("Formatted Headers Date '{pull_timestamp}'", pull_timestamp=pull_timestamp)
            metadata["pull_timestamp"] = pull_timestamp
        return cls(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self, *extractors):
        for extractor in extractors:
            extractor(self)
