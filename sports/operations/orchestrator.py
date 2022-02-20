import collections
import itertools

import pendulum
from loguru import logger

from sports.shared.operators import Archiver
from sports.shared.utils import MAX_WORKERS


class BaseOrchestrator:
    """
    Inherit usecase is to orchestrate concurrent web GET requests
    that pull data relevant to any particular data feed(s)
    and construct structured data files relavant to their data feeds

    -- Meant to be inherited by other orchestrators
    """

    def __init__(
        self,
        *args,
        date=None,
        parallel=MAX_WORKERS,
        transport_params=None,
        file_type="json-lines",
        compression=".gz",
        write_strategy=None,
        batch_size=1000,
        feeds_config=None,
        permissions=None,
        tz="UTC",
        output=".",
        **kwargs,
    ):
        self.exports = {}
        self.batch_size = batch_size
        self.batches = collections.defaultdict(list)
        self.output = output

        self.run_time = pendulum.now(tz=tz)
        self.date = pendulum.parse(date, tz=tz) if date else self.run_time
        self.feeds_config = feeds_config or collections.defaultdict(dict)
        self.permissions = permissions or collections.defaultdict(dict)
        self.parallel = parallel if parallel >= 1 and parallel <= MAX_WORKERS else MAX_WORKERS
        self.futures = collections.defaultdict(list)

        self.written_files = {}

        # Archiver Keyword Arguments
        self.transport_params = transport_params
        self.file_type = file_type
        self.write_strategy = write_strategy or {}
        self.write_strategy.update({"compression": compression})

        # Logging
        self.logger = logger.bind(__class_name__=self.__class__.__name__, __class__=self.__class__)

    def batch(self, feed, record):
        if len(self.batches[feed]) >= self.batch_size:
            self.exports[feed] = itertools.chain(self.exports.get(feed, []), self.batches[feed])
            del self.batches[feed]
            self.export(feed)
        if isinstance(record, dict):
            self.batches[feed].append(record)
        else:
            raise TypeError(f"Expected 'dict' type and instead received type: '{type(record)}' for feed: {feed}")

    def export(self, feed):
        if self.batches[feed]:
            self.exports[feed] = itertools.chain(self.exports.get(feed, []), self.batches[feed])
            del self.batches[feed]

        if self.exports.get(feed):
            uri = self.uri(feed)
            self.written_files.setdefault(uri, 0)
            write = True
            if self.written_files[uri] > 0:
                write = False

            archiver = Archiver(
                self.exports[feed],
                uri,
                write_strategy=self.write_strategy,
                transport_params=self.transport_params,
                file_type=self.file_type,
                write=write,
            )
            archiver.write()
            self.logger.info(
                "{records} records written to '{filename}'",
                filename=archiver.written_file,
                records=archiver.records_written,
                feed=feed,
            )
            self.written_files[uri] += archiver.records_written
            del self.exports[feed]

    def uri(self, feed):
        filename = self.feeds_config[feed]["filename"]
        if filename.endswith("-current"):
            filename = filename.format(timestamp=self.run_time.format("YYYYMMDDHHmmssZ"))
        else:
            filename = filename.format(timestamp=self.date.format("YYYYMMDDHHmmssZ"))
        return f"{self.output.rstrip('/')}/{filename.lstrip('/')}"

    def get_permission(self, feed, permission):
        return self.permissions.get(feed, {}).get(permission, False)
