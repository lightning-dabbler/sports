import sports.shared.container


class Builder:
    __slots__ = ("metadata", "player_metadata", "team_metadata")

    def __init__(self, metadata=None, player_metadata=None, team_metadata=None):
        self.metadata = metadata or {}
        self.player_metadata = player_metadata or {}
        self.team_metadata = team_metadata or {}

    def construct(self, data):
        selection_id = data["id"]
        legend = {detail["key"]: detail["text"].strip() for detail in data.get("legend", {}).get("details", [])}
        headers = data["table"]["headers"][0]["columns"]
        records = data["table"]["rows"]
        n = len(headers)
        for record in records:
            cols = record["columns"]
            for i in range(1, n):
                stats = {
                    "selection_id": selection_id,
                    "year": headers[i]["text"],
                    "stat_abbreviation": cols[0]["text"],
                    "stat_title": legend[cols[0]["text"]],
                    "stat_value": cols[i]["text"],
                }
                yield {**self.metadata, **self.team_metadata, **self.player_metadata, **stats}


def extract(self):
    self.data_extracts = self.raw_data.get("sectionList", [])


class AdvancedPlayerStatsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, player_metadata=None, team_metadata=None, **kwargs):
        self.player_metadata = player_metadata or {}
        self.team_metadata = team_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Advanced Player Stats!", metadata=self.metadata)
        for section in self.data_extracts:
            builder = Builder(
                metadata=self.metadata, player_metadata=self.player_metadata, team_metadata=self.team_metadata
            )
            yield from builder.construct(section)
