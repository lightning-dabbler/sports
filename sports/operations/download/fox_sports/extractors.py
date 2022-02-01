class Extractors:
    def extract_matchups(data):
        return data["sectionList"][0]["events"]

    def extract_matchup_team_stats(data):
        team_stats_comparison = data.get("teamStatsComparison")
        if team_stats_comparison:
            return team_stats_comparison["items"]
        return []

    def extract_matchup_team_leader_stats(data):
        team_leaders_comparison = data.get("teamLeadersComparison")
        if team_leaders_comparison:
            return team_leaders_comparison["items"]
        return []

    def extract_team_stats(data):
        leader_sections = data.get("leadersSections")
        if leader_sections:
            return leader_sections[1]["leaders"]
        return []

    def extract_team_player_stats(data):
        leader_sections = data.get("leadersSections")
        if leader_sections:
            return leader_sections[0]["leaders"]
        return []

    def extract_team_roster(data):
        groups = data.get("groups")
        if groups:
            return groups[0]["rows"]
        return []

    def extract_player_stats(data):
        leader_sections = data.get("leadersSections")
        if leader_sections:
            return leader_sections[0].get("leaders", [])
        return []

    def extract_advanced_player_stats(data):
        section_list = data.get("sectionList", [])
        return section_list

    def extract_fox_projections(data):
        return data.get("foxProjections", {}).get("items", [])

    def extract_fox_odds(data):
        return data.get("oddsSixPack", {}).get("items", [])


class MetaExtractors:
    def extract_team_roster_headers_columns(data):
        groups = data.get("groups")
        if groups:
            return groups[0]["headers"][0]["columns"]
        return []

    def extract_matchup_team_leader_stats_teams(data):
        team_leaders_comparison = data.get("teamLeadersComparison")
        if team_leaders_comparison:
            return {
                "left_team": team_leaders_comparison["leftName"],
                "right_team": team_leaders_comparison["rightName"],
            }
        return {}

    def extract_matchup_team_stats_teams(data):
        team_stats_comparison = data.get("teamStatsComparison")
        if team_stats_comparison:
            return {"left_team": team_stats_comparison["leftName"], "right_team": team_stats_comparison["rightName"]}
        return {}
