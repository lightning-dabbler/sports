from ._base import BaseTeamStatsContainer


class Builder:
    def construct(data):
        return {
            "player_name": data["name"],
            "player_name_short": data["shortName"],
            "stat_title": data["title"],
            "stat_abbreviation": data["statAbbreviation"],
            "stat_value": data["statValue"],
        }


def extract(self):
    leader_sections = self.raw_data.get("leadersSections")
    if leader_sections:
        self.data_extracts = leader_sections[0].get("leaders", [])


class TeamPlayerStatsContainer(BaseTeamStatsContainer):
    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Team Player Stats", team_metadata=self.team_metadata)
        yield from super().forge(Builder)
