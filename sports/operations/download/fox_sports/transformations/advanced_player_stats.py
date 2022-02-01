class Transformer:
    __slots__ = ("team_meta", "player_meta", "meta")

    def __init__(self, team_meta=None, player_meta=None, meta=None):
        self.team_meta = team_meta or {}
        self.player_meta = player_meta or {}
        self.meta = meta or {}

    def parse_advanced_stats(self, data):
        selection_id = data["id"]
        legend = {detail["key"]: detail["text"].strip() for detail in data.get("legend", {}).get("details", [])}
        headers = data["table"]["headers"][0]["columns"]
        records = data["table"]["rows"]
        n = len(headers)
        for record in records:
            cols = record["columns"]
            for i in range(1, n):
                stats = dict(
                    selection_id=selection_id,
                    year=headers[i]["text"],
                    stat_abbreviation=cols[0]["text"],
                    stat_title=legend[cols[0]["text"]],
                    stat_value=cols[i]["text"],
                )
                yield {**self.meta, **self.team_meta, **self.player_meta, **stats}
