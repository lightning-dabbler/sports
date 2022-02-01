from ._base import MatchupStatsBaseTransformer


class Transformer(MatchupStatsBaseTransformer):
    def _team(self, data, left_team=True):
        team_details = "leftItemDetails" if left_team else "rightItemDetails"
        team_stats = dict(
            player_id=data[team_details]["entityLink"]["layout"]["tokens"]["id"],
            player=data[team_details]["entityLink"]["title"],
            stat_abbreviation=data["title"],
            stat_value=data[team_details]["subtitle"],
        )
        if left_team:
            return {**self.left_team_meta, **team_stats}
        else:
            return {**self.right_team_meta, **team_stats}
