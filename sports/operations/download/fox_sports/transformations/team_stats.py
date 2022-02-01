from ._base import TeamStatsBaseTransformer


class Transformer(TeamStatsBaseTransformer):
    def parse_stats(self, data):
        stats = dict(
            stat_title=data["title"],
            stat_abbreviation=data["statAbbreviation"],
            stat_value=data["statValue"],
        )
        self._stats = {**self.team_meta, **stats}
