from ._base import TeamStatsBaseTransformer


class Transformer(TeamStatsBaseTransformer):
    def parse_stats(self, data):
        stats = dict(
            player_name=data["name"],
            player_name_short=data["shortName"],
            stat_title=data["title"],
            stat_abbreviation=data["statAbbreviation"],
            stat_value=data["statValue"],
        )
        self._stats = {**self.team_meta, **stats}
