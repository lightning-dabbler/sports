from ._base import BaseTeamStatsContainer


class Builder:
    def construct(data):
        return {
            "stat_title": data["title"],
            "stat_abbreviation": data["statAbbreviation"],
            "stat_value": data["statValue"],
        }


def extract(self):
    leader_sections = self.raw_data.get("leadersSections")
    if leader_sections:
        self.data_extracts = leader_sections[1].get("leaders", [])


class TeamStatsContainer(BaseTeamStatsContainer):
    def extraction(self):
        super().extraction(extract)

    def forge(self):
        self.logger.debug("Forging Team Stats", team_metadata=self.team_metadata)
        yield from super().forge(Builder)
