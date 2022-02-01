from ._base import MatchupStatsBaseTransformer


class Transformer(MatchupStatsBaseTransformer):
    def _team(self, data, left_team=True):
        team_details = "leftItemDetails" if left_team else "rightItemDetails"
        team_stats = dict(stat_abbreviation=data["title"], stat_value=data[team_details]["title"])
        if left_team:
            return {**self.left_team_meta, **team_stats}
        else:
            return {**self.right_team_meta, **team_stats}
