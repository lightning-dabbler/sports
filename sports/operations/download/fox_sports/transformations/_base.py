class MatchupStatsBaseTransformer:
    def __init__(self, left_team_meta=None, right_team_meta=None):
        self._left_team_stats = {}
        self._right_team_stats = {}
        self.left_team_meta = left_team_meta or {}
        self.right_team_meta = right_team_meta or {}

    @property
    def left_team_stats(self):
        return self._left_team_stats

    @property
    def right_team_stats(self):
        return self._right_team_stats

    def parse_left_team_stats(self, data):
        self._left_team_stats = self._team(data, left_team=True)

    def parse_right_team_stats(self, data):
        self._right_team_stats = self._team(data, left_team=False)

    def _team(self, data, left_team=True):
        if left_team:
            return {**self.left_team_meta}
        else:
            return {**self.right_team_meta}


class TeamStatsBaseTransformer:
    def __init__(self, team_meta=None):
        self._stats = {}
        self.team_meta = team_meta

    @property
    def team_stats(self):
        return self._stats
