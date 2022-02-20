import sports.shared.container


class Builder:
    def construct(data):
        return {
            "selection_id": data["selectionId"],
            "stat_title": data["title"],
            "stat_abbreviation": data["statAbbreviation"],
            "stat_value": data["statValue"],
            "condensed_uri": data["condensedUri"].strip() if data.get("condensedUri") else None,
        }


def extract(self):
    leader_sections = self.raw_data.get("leadersSections")
    if leader_sections:
        self.data_extracts = leader_sections[0].get("leaders", [])


class PlayerStatsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, team_metadata=None, player_metadata=None, **kwargs):
        self.advanced_stats_uris = []
        self.uri_to_request = None
        self.team_metadata = team_metadata
        self.player_metadata = player_metadata
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug(
            "Forging Player Stats!", team_metadata=self.team_metadata, player_metadata=self.player_metadata
        )
        for record in self.data_extracts:
            stats = Builder.construct(record)
            uri = stats.pop("condensed_uri", None)
            if uri and uri not in self.advanced_stats_uris:
                self.uri_to_request = uri
                self.advanced_stats_uris.append(uri)
            else:
                self.uri_to_request = None
            yield {**self.metadata, **self.team_metadata, **self.player_metadata, **stats}
