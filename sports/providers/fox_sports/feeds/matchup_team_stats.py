from ._base import BaseMatchupTeamStatsContainer


class Builder:
    def construct_right_team_stats(data):
        return {"stat_abbreviation": data["title"], "stat_value": data["rightItemDetails"]["title"]}

    def construct_left_team_stats(data):
        return {"stat_abbreviation": data["title"], "stat_value": data["leftItemDetails"]["title"]}


def extract_matchup_team_stats(self):
    team_stats_comparison = self.raw_data.get("teamStatsComparison")
    if team_stats_comparison:
        self.data_extracts = team_stats_comparison["items"]


def extract_matchup_team_stats_teams(self):
    team_stats_comparison = self.raw_data.get("teamStatsComparison")
    if team_stats_comparison:
        self.left_team_metadata.setdefault("team_name", team_stats_comparison["leftName"])
        self.right_team_metadata.setdefault("team_name", team_stats_comparison["rightName"])


class MatchupTeamStatsContainer(BaseMatchupTeamStatsContainer):
    def extraction(self):
        super().extraction(extract_matchup_team_stats, extract_matchup_team_stats_teams)

    def forge(self):
        self.logger.debug(
            "Forging Matchup Team Stats!",
            left_team_metadata=self.left_team_metadata,
            right_team_metadata=self.right_team_metadata,
        )
        yield from super().forge(Builder)
