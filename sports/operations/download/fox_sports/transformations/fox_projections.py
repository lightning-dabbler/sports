class Transformer:
    def __init__(self, event_meta=None):
        self.event_meta = event_meta or {}

    def parse_projections(self, data):
        projections = dict(details=data["description"], statistic=data["statistic"], timestamp=data["timestamp"])
        yield {**self.event_meta, **projections}
