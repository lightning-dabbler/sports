import json.decoder

import pendulum
from loguru import logger

import sports.operations.utils
from sports.operations.requests import make_request


class BaseContainer:
    pull_meta_keys = ["pull_timestamp"]

    def __init__(self, raw_data=None, **meta):
        self.raw_data = raw_data
        self.data_extracts = []
        self.meta = {}
        for key in self.pull_meta_keys:
            if meta.get(key):
                self.meta[key] = meta[key]

    @classmethod
    def from_request(cls, url, set_pull_meta=True, **kwargs):
        response = make_request(url, **kwargs)

        try:
            raw_data = response.json()
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
            logger.error("No JSON Payload at '{url}'", url=url)
            raw_data = {}

        meta = {}
        if set_pull_meta:
            headers = response.headers
            header_date = sports.operations.utils.header_date(headers)
            logger.debug("Headers Date '{header_date}'", header_date=header_date)
            timestamp = pendulum.from_format(header_date, "ddd[,] DD MMM YYYY HH[:]mm[:]ss z")
            logger.trace("Extracted Timestamp '{timestamp}'", timestamp=timestamp)
            pull_timestamp = timestamp.format("YYYY-MM-DD[T]HH:mm:ssZ")
            logger.debug("Formatted Headers Date '{pull_timestamp}'", pull_timestamp=pull_timestamp)
            meta["pull_timestamp"] = pull_timestamp
        return cls(raw_data=raw_data, **meta)

    def extraction(self, extractor):
        self.data_extracts = extractor(self.raw_data)
