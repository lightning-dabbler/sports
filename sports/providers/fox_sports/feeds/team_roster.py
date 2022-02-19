import sports.shared.container


class Builder:
    __slots__ = ("team_metadata", "header_columns", "metadata")

    def __init__(self, team_metadata=None, header_columns=None, metadata=None):
        self.team_metadata = team_metadata or {}
        self.header_columns = header_columns or []
        self.metadata = metadata or {}

    def construct(self, data):
        columns = data["columns"]
        n = len(columns)
        player_id = data["entityLink"]["layout"]["tokens"]["id"]
        player_meta = {"player_id": player_id, "player": columns[0]["text"]}
        for i in range(1, n):
            player_data = {"attribute": self.header_columns[i]["text"].lower().strip(), "value": columns[i]["text"]}
            yield {**self.metadata, **self.team_metadata, **player_meta, **player_data}


def extract_team_roster(self):
    groups = self.raw_data.get("groups")
    if groups:
        self.data_extracts = groups[0]["rows"]


def extract_team_roster_header_columns(data):
    groups = data.get("groups")
    if groups:
        return groups[0]["headers"][0]["columns"]
    return []


class TeamRosterContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, team_metadata=None, **kwargs):
        self.team_metadata = team_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract_team_roster)

    def forge(self):
        header_columns = extract_team_roster_header_columns(self.raw_data)
        self.logger.debug("Forging Team Roster!", team_metadata=self.team_metadata)
        for record in self.data_extracts:
            builder = Builder(team_metadata=self.team_metadata, header_columns=header_columns, metadata=self.metadata)
            yield from builder.construct(record)
