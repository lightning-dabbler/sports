import sports.shared.container


class Builder:
    def __init__(self, metadata=None, event_metadata=None):
        self.metadata = metadata or {}
        self.event_metadata = event_metadata or {}

    def construct(self, data):
        details_short = data["title"]
        details_long = data["description"]
        for line in data["odds"]:
            odds = {
                "designation": line["text"],
                "line": line["title"],
                "details_short": details_short,
                "details_long": details_long,
            }
            yield {**self.metadata, **self.event_metadata, **odds}


def extract(self):
    self.data_extracts = self.raw_data.get("oddsSixPack", {}).get("items", [])


class FoxOddsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, event_metadata=None, **kwargs):
        self.event_metadata = event_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Fox Odds!", metadata=self.metadata, event_metadata=self.event_metadata)
        for record in self.data_extracts:
            builder = Builder(metadata=self.metadata, event_metadata=self.event_metadata)
            yield from builder.construct(record)
