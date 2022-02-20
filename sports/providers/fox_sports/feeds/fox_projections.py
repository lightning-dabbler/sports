import sports.shared.container


class Builder:
    def construct(data):
        return {"details": data["description"], "statistic": data["statistic"], "timestamp": data["timestamp"]}


def extract(self):
    self.data_extracts = self.raw_data.get("foxProjections", {}).get("items", [])


class FoxProjectionsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, event_metadata=None, **kwargs):
        self.event_metadata = event_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Fox Projections!", metadata=self.metadata, event_metadata=self.event_metadata)
        for record in self.data_extracts:
            projection = Builder.construct(record)
            yield {**self.metadata, **self.event_metadata, **projection}
