import sports.shared.container


class Builder:
    TEAM_META_HEADERS = ["team_id", "team_name", "team_name_long", "team_name_full"]

    def __init__(self):
        self._event_metadata = {}
        self.home_team_metadata = {}
        self.away_team_metadata = {}
        self._home_team = {}
        self._away_team = {}

    @property
    def event_metadata(self):
        return self._event_metadata

    @property
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

    def assign_event_metadata(self, data):
        metadata = {
            "event_id": data["entityLink"]["layout"]["tokens"]["id"],
            "event_time": data["eventTime"],
            "event_status": data["eventStatus"],
            "status_line": data.get("status_line"),
        }
        self._event_metadata = metadata

    def assign_home_team(self, data):
        team = self._assign_team(data, home_team=True)
        self.home_team_metadata = {key: val for key, val in team.items() if key in self.TEAM_META_HEADERS}
        self._home_team = {**self._event_metadata, **team}

    def assign_away_team(self, data):
        team = self._assign_team(data, home_team=False)
        self.away_team_metadata = {key: val for key, val in team.items() if key in self.TEAM_META_HEADERS}
        self._away_team = {**self._event_metadata, **team}

    def _assign_team(self, data, home_team=True):
        uri = "homeUri" if home_team else "awayUri"
        team_place = "lowerTeam" if home_team else "upperTeam"
        team_uri = data["entityLink"]["layout"]["tokens"].get(uri)
        team_data = {
            "team_id": team_uri.split("/")[-1] if team_uri else "",
            "team_name": data[team_place]["name"],
            "team_name_long": data[team_place]["longName"],
            "team_name_full": data[team_place]["imageAltText"],
            "record": data[team_place].get("record"),
            "score": data[team_place].get("score"),
            "rank": data[team_place].get("rank"),
            "home_team": home_team,
            "is_loser": data[team_place]["isLoser"],
        }
        return team_data


def extract(self):
    self.data_extracts = self.raw_data["sectionList"][0]["events"]


class MatchupsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, **kwargs):
        self.event_metadata = {}
        self.home_team_metadata = {}
        self.away_team_metadata = {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Matchups!")
        for record in self.data_extracts:
            builder = Builder()
            builder.assign_event_metadata(record)
            builder.assign_home_team(record)
            builder.assign_away_team(record)
            self.event_metadata = builder.event_metadata
            self.home_team_metadata = builder.home_team_metadata
            self.away_team_metadata = builder.away_team_metadata
            yield {**self.metadata, **builder.home_team}
            yield {**self.metadata, **builder.away_team}
