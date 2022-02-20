from ._base import BaseMatchupTeamStatsContainer


class Builder:
    def construct_right_team_stats(data):
        return {
            "player_id": data["rightItemDetails"]["entityLink"]["layout"]["tokens"]["id"],
            "player": data["rightItemDetails"]["entityLink"]["title"],
            "stat_abbreviation": data["title"],
            "stat_value": data["rightItemDetails"]["subtitle"],
        }

    def construct_left_team_stats(data):
        return {
            "player_id": data["leftItemDetails"]["entityLink"]["layout"]["tokens"]["id"],
            "player": data["leftItemDetails"]["entityLink"]["title"],
            "stat_abbreviation": data["title"],
            "stat_value": data["leftItemDetails"]["subtitle"],
        }


def extract_matchup_team_leader_stats(self):
    team_leaders_comparison = self.raw_data.get("teamLeadersComparison")
    if team_leaders_comparison:
        self.data_extracts = team_leaders_comparison["items"]


def extract_matchup_team_leader_stats_teams(self):
    team_leaders_comparison = self.raw_data.get("teamLeadersComparison")
    if team_leaders_comparison:
        self.left_team_metadata.setdefault("team_name", team_leaders_comparison["leftName"])
        self.right_team_metadata.setdefault("team_name", team_leaders_comparison["rightName"])


class MatchupTeamLeaderStatsContainer(BaseMatchupTeamStatsContainer):
    def extraction(self):
        super().extraction(extract_matchup_team_leader_stats, extract_matchup_team_leader_stats_teams)

    def forge(self):
        self.logger.debug(
            "Forging Matchup Team Leader Stats!",
            left_team_metadata=self.left_team_metadata,
            right_team_metadata=self.right_team_metadata,
        )
        yield from super().forge(Builder)
