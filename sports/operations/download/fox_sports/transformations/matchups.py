class Transformer:
    TEAM_META_HEADERS = ["team_id", "team_name", "team_name_long", "team_name_full"]

    def __init__(self):
        self._event_meta = {}
        self.home_team_meta = {}
        self.away_team_meta = {}
        self._home_team = {}
        self._away_team = {}

    @property
    def event_meta(self):
        return self._event_meta

    @property
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

    def parse_event_meta(self, data):
        metadata = dict(
            event_id=data["entityLink"]["layout"]["tokens"]["id"],
            event_time=data["eventTime"],
            event_status=data["eventStatus"],
            status_line=data.get("status_line"),
        )
        self._event_meta = metadata

    def parse_home_team(self, data):
        team = self._team(data, home_team=True)
        self.home_team_meta = {key: val for key, val in team.items() if key in self.TEAM_META_HEADERS}
        self._home_team = {**self._event_meta, **team}

    def parse_away_team(self, data):
        team = self._team(data, home_team=False)
        self.away_team_meta = {key: val for key, val in team.items() if key in self.TEAM_META_HEADERS}
        self._away_team = {**self._event_meta, **team}

    def _team(self, data, home_team=True):
        uri = "homeUri" if home_team else "awayUri"
        team_place = "lowerTeam" if home_team else "upperTeam"
        team_uri = data["entityLink"]["layout"]["tokens"].get(uri)
        team_data = dict(
            team_id=team_uri.split("/")[-1] if team_uri else "",
            team_name=data[team_place]["name"],
            team_name_long=data[team_place]["longName"],
            team_name_full=data[team_place]["imageAltText"],
            record=data[team_place].get("record"),
            score=data[team_place].get("score"),
            rank=data[team_place].get("rank"),
            home_team=home_team,
            is_loser=data[team_place]["isLoser"],
        )
        return team_data
