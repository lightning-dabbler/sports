class Transformer:
    def __init__(self, event_meta=None):
        self.event_meta = event_meta or {}

    def parse_odds(self, data):
        details_short = data["title"]
        details_long = data["description"]
        for line in data["odds"]:
            odds = dict(
                designation=line["text"],
                line=line["title"],
                details_short=details_short,
                details_long=details_long,
            )
            yield {**self.event_meta, **odds}
