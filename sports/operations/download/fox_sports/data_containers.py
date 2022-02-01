from loguru import logger

import sports.operations.container

from . import extractors, transformations


class MatchupsContainer(sports.operations.container.BaseContainer):
    def __init__(self, *args, **kwargs):
        self.event_meta = {}
        self.home_team_meta = {}
        self.away_team_meta = {}
        super().__init__(*args, **kwargs)

    def extraction(self):
        super().extraction(extractors.Extractors.extract_matchups)

    def parse_data_extracts(self):
        logger.debug("Parsing Matchups!")
        for record in self.data_extracts:
            transformer = transformations.MatchupsTransformer()
            transformer.parse_event_meta(record)
            transformer.parse_home_team(record)
            transformer.parse_away_team(record)
            self.event_meta = transformer.event_meta
            self.home_team_meta = transformer.home_team_meta
            self.away_team_meta = transformer.away_team_meta
            yield {**self.meta, **transformer.home_team}
            yield {**self.meta, **transformer.away_team}


class BaseTeamStatsContainer(sports.operations.container.BaseContainer):
    def parse_data_extracts(self, transformer_cls, team_meta=None):
        team_meta = team_meta or {}
        logger.debug("Parsing Team Stats", team_meta=team_meta)
        for record in self.data_extracts:
            transformer = transformer_cls(team_meta=team_meta)
            transformer.parse_stats(record)
            yield {**self.meta, **transformer.team_stats}


class TeamPlayerStatsContainer(BaseTeamStatsContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_team_player_stats)

    def parse_data_extracts(self, team_meta=None):
        yield from super().parse_data_extracts(transformations.TeamPlayerStatsTransformer, team_meta=team_meta)


class TeamStatsContainer(BaseTeamStatsContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_team_stats)

    def parse_data_extracts(self, team_meta=None):
        yield from super().parse_data_extracts(transformations.TeamStatsTransformer, team_meta=team_meta)


class BaseMatchupTeamStatsContainer(sports.operations.container.BaseContainer):
    def parse_data_extracts(self, transformer_cls, left_team_meta=None, right_team_meta=None):
        left_team_meta = left_team_meta or {}
        right_team_meta = right_team_meta or {}
        logger.debug("Parsing Matchup Team Stats!", left_team_meta=left_team_meta, right_team_meta=right_team_meta)
        for record in self.data_extracts:
            transformer = transformer_cls(left_team_meta=left_team_meta, right_team_meta=right_team_meta)
            transformer.parse_left_team_stats(record)
            transformer.parse_right_team_stats(record)
            yield {**self.meta, **transformer.left_team_stats}
            yield {**self.meta, **transformer.right_team_stats}


class MatchupTeamStatsContainer(BaseMatchupTeamStatsContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_matchup_team_stats)

    def parse_data_extracts(self, team1_meta=None, team2_meta=None):
        teams = extractors.MetaExtractors.extract_matchup_team_stats_teams(self.raw_data)
        left_team_meta = None
        right_team_meta = None
        if teams.get("left_team"):
            left_team_meta = {
                team1_meta["team_name"] == teams["left_team"]: team1_meta,
                team2_meta["team_name"] == teams["left_team"]: team2_meta,
            }.get(True, {})
        if teams.get("right_team"):
            right_team_meta = {
                team1_meta["team_name"] == teams["right_team"]: team1_meta,
                team2_meta["team_name"] == teams["right_team"]: team2_meta,
            }.get(True, {})

        yield from super().parse_data_extracts(
            transformations.MatchupTeamStatsTransformer,
            left_team_meta=left_team_meta,
            right_team_meta=right_team_meta,
        )


class MatchupTeamLeaderStatsContainer(BaseMatchupTeamStatsContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_matchup_team_leader_stats)

    def parse_data_extracts(self, team1_meta=None, team2_meta=None):
        teams = extractors.MetaExtractors.extract_matchup_team_leader_stats_teams(self.raw_data)
        left_team_meta = None
        right_team_meta = None
        if teams.get("left_team"):
            left_team_meta = {
                team1_meta["team_name"] == teams["left_team"]: team1_meta,
                team2_meta["team_name"] == teams["left_team"]: team2_meta,
            }.get(True, {})
        if teams.get("right_team"):
            right_team_meta = {
                team1_meta["team_name"] == teams["right_team"]: team1_meta,
                team2_meta["team_name"] == teams["right_team"]: team2_meta,
            }.get(True, {})

        yield from super().parse_data_extracts(
            transformations.MatchupTeamLeaderStatsTransformer,
            left_team_meta=left_team_meta,
            right_team_meta=right_team_meta,
        )


class FoxProjectionsContainer(sports.operations.container.BaseContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_fox_projections)

    def parse_data_extracts(self, event_meta=None):
        event_meta = event_meta or {}
        logger.debug("Parsing Fox Projections!", event_meta=event_meta)
        for record in self.data_extracts:
            transformer = transformations.FoxProjectionsTransformer(event_meta=event_meta)
            yield from transformer.parse_projections(record)


class FoxOddsContainer(sports.operations.container.BaseContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_fox_odds)

    def parse_data_extracts(self, event_meta=None):
        event_meta = event_meta or {}
        logger.debug("Parsing Fox Odds!", event_meta=event_meta)
        for record in self.data_extracts:
            transformer = transformations.FoxOddsTransformer(event_meta=event_meta)
            yield from transformer.parse_odds(record)


class TeamRosterContainer(sports.operations.container.BaseContainer):
    def __init__(self, *args, **kwargs):
        self.team_meta = {}
        super().__init__(*args, **kwargs)

    def extraction(self):
        super().extraction(extractors.Extractors.extract_team_roster)

    def parse_data_extracts(self, team_meta=None):
        self.team_meta = team_meta or {}
        headers_columns = extractors.MetaExtractors.extract_team_roster_headers_columns(self.raw_data)
        logger.debug("Parsing Team Roster!", team_meta=self.team_meta)
        for record in self.data_extracts:
            transformer = transformations.TeamRosterTransformer(
                team_meta=self.team_meta, headers_columns=headers_columns, meta=self.meta
            )
            yield from transformer.parse_player_data(record)


class PlayerStats(sports.operations.container.BaseContainer):
    def __init__(self, *args, **kwargs):
        self.advanced_stats_uris = []
        self.current_advanced_stats_uri = None
        self.team_meta = {}
        self.player_meta = {}
        super().__init__(*args, **kwargs)

    def extraction(self):
        super().extraction(extractors.Extractors.extract_player_stats)

    def parse_data_extracts(self, team_meta=None, player_meta=None):
        team_meta = team_meta or {}
        player_meta = player_meta or {}
        self.team_meta = team_meta
        self.player_meta = player_meta
        logger.debug("Parsing Player Stats!", team_meta=team_meta, player_meta=player_meta)
        for record in self.data_extracts:
            transformer = transformations.PlayerStatsTransformer(team_meta=team_meta, player_meta=player_meta)
            transformer.parse_stats(record)
            if transformer.advanced_stats_uri and transformer.advanced_stats_uri not in self.advanced_stats_uris:
                self.current_advanced_stats_uri = transformer.advanced_stats_uri
                self.advanced_stats_uris.append(self.current_advanced_stats_uri)
            else:
                self.current_advanced_stats_uri = None
            yield {**self.meta, **transformer.player_stats}


class AdvancedPlayerStats(sports.operations.container.BaseContainer):
    def extraction(self):
        super().extraction(extractors.Extractors.extract_advanced_player_stats)

    def parse_data_extracts(self, team_meta=None, player_meta=None):
        team_meta = team_meta or {}
        player_meta = player_meta or {}
        logger.debug("Parsing Advanced Player Stats!", team_meta=team_meta, player_meta=player_meta)
        for section in self.data_extracts:
            transformer = transformations.AdvancedPlayerStatsTransformer(
                meta=self.meta, team_meta=team_meta, player_meta=player_meta
            )
            yield from transformer.parse_advanced_stats(section)
