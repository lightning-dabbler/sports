class Transformer:
    __slots__ = ("_stats", "team_meta", "player_meta", "advanced_stats_uri")

    def __init__(self, team_meta=None, player_meta=None):
        self._stats = {}
        self.team_meta = team_meta or {}
        self.player_meta = player_meta or {}
        self.advanced_stats_uri = None

    @property
    def player_stats(self):
        return self._stats

    def parse_stats(self, data):
        stats = dict(
            selection_id=data["selectionId"],
            stat_title=data["title"],
            stat_abbreviation=data["statAbbreviation"],
            stat_value=data["statValue"],
        )
        if data.get("condensedUri"):
            self.advanced_stats_uri = data["condensedUri"].strip()
        self._stats = {**self.team_meta, **self.player_meta, **stats}
