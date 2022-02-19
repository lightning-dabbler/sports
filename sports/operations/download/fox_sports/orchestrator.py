import concurrent.futures

import sports.providers.fox_sports.feeds as fox_sports_feeds
from sports.operations.download.fox_sports import Dispatcher
from sports.operations.orchestrator import BaseOrchestrator
from sports.shared.utils import MAX_WORKERS


class Orchestrator(BaseOrchestrator):
    def __init__(
        self,
        *args,
        date=None,
        parallel=MAX_WORKERS,
        transport_params=None,
        file_type="json-lines",
        compression=".gz",
        write_strategy=None,
        batch_size=1000,
        feeds_config=None,
        permissions=None,
        tz="UTC",
        output=".",
        **kwargs,
    ):
        super().__init__(
            *args,
            date=date,
            parallel=parallel,
            transport_params=transport_params,
            file_type=file_type,
            compression=compression,
            write_strategy=write_strategy,
            batch_size=batch_size,
            feeds_config=feeds_config,
            permissions=permissions,
            tz=tz,
            output=output,
            **kwargs,
        )

    def _retrieve_matchups(self):
        matchups_url = self.feeds_config["matchups"]["url"].format(date_str=self.date.format("YYYYMMDD"))
        matchups_params = self.feeds_config["matchups"].get("params", {})
        matchups = fox_sports_feeds.MatchupsContainer.from_request(
            matchups_url, set_pull_metadata=True, request_kwargs={"params": matchups_params}
        )
        return matchups

    def _retrieve_matchup_team_stats(self, executor, matchups_home, matchups_away, event_meta):
        matchup_team_stats_url = self.feeds_config["matchup-team-stats"]["url"].format(event_id=event_meta["event_id"])
        matchup_team_stats_params = self.feeds_config["matchup-team-stats"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                fox_sports_feeds.BaseMatchupTeamStatsContainer,
                matchup_team_stats_url,
                set_pull_metadata=True,
                extra_kwargs={"team1_meta": matchups_home, "team2_meta": matchups_away},
                request_kwargs={"params": matchup_team_stats_params},
            )
        )

    def _retrieve_team_stats(self, executor, away_team_meta, home_team_meta):
        away_team_url = self.feeds_config["team-stats"]["url"].format(team_id=away_team_meta["team_id"])
        home_team_url = self.feeds_config["team-stats"]["url"].format(team_id=home_team_meta["team_id"])
        team_params = self.feeds_config["team-stats"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                fox_sports_feeds.BaseTeamStatsContainer,
                away_team_url,
                set_pull_metadata=True,
                request_kwargs={"params": team_params},
                team_metadata=away_team_meta,
            )
        )
        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                fox_sports_feeds.BaseTeamStatsContainer,
                home_team_url,
                set_pull_metadata=True,
                request_kwargs={"params": team_params},
                team_metadata=home_team_meta,
            )
        )

    def _retrieve_team_roster(self, executor, away_team_meta, home_team_meta):
        away_team_roster_url = self.feeds_config["team-roster"]["url"].format(team_id=away_team_meta["team_id"])
        home_team_roster_url = self.feeds_config["team-roster"]["url"].format(team_id=home_team_meta["team_id"])
        team_roster_params = self.feeds_config["team-roster"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                fox_sports_feeds.TeamRosterContainer,
                away_team_roster_url,
                set_pull_metadata=True,
                request_kwargs={"params": team_roster_params},
                team_metadata=away_team_meta,
            )
        )
        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                fox_sports_feeds.TeamRosterContainer,
                home_team_roster_url,
                set_pull_metadata=True,
                request_kwargs={"params": team_roster_params},
                team_metadata=home_team_meta,
            )
        )

    def _store_matchup_team_stats(self, dispatcher, feed):
        if feed == "matchup-team-stats":
            matchups_stats_container = fox_sports_feeds.MatchupTeamStatsContainer
        elif feed == "matchup-team-leaders-stats":
            matchups_stats_container = fox_sports_feeds.MatchupTeamLeaderStatsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        matchups_stats_container_instance = matchups_stats_container(raw_data=dispatcher.container_class.raw_data)
        matchups_stats_container_instance.extraction()
        left_team_metadata = {
            matchups_stats_container_instance.left_team_metadata.get("team_name", False)
            == dispatcher.extra_kwargs["team1_meta"].get("team_name"): dispatcher.extra_kwargs["team1_meta"],
            matchups_stats_container_instance.left_team_metadata.get("team_name", False)
            == dispatcher.extra_kwargs["team2_meta"].get("team_name"): dispatcher.extra_kwargs["team2_meta"],
        }.get(True, {})
        right_team_metadata = {
            matchups_stats_container_instance.right_team_metadata.get("team_name", False)
            == dispatcher.extra_kwargs["team1_meta"].get("team_name"): dispatcher.extra_kwargs["team1_meta"],
            matchups_stats_container_instance.right_team_metadata.get("team_name", False)
            == dispatcher.extra_kwargs["team2_meta"].get("team_name"): dispatcher.extra_kwargs["team2_meta"],
        }.get(True, {})
        matchups_stats_container_instance.left_team_metadata = left_team_metadata
        matchups_stats_container_instance.right_team_metadata = right_team_metadata

        for record in matchups_stats_container_instance.forge():
            self.batch(feed, record)

    def _store_fox_odds(self, dispatcher, feed):
        if feed == "fox-odds":
            foxs_odds_container = fox_sports_feeds.FoxOddsContainer
        elif feed == "fox-projections":
            foxs_odds_container = fox_sports_feeds.FoxProjectionsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        foxs_odds_container_instance = foxs_odds_container(
            raw_data=dispatcher.container_class.raw_data,
            metadata=dispatcher.container_class.metadata,
            event_metadata={"event_id": dispatcher.extra_kwargs["team1_meta"]["event_id"]},
        )
        foxs_odds_container_instance.extraction()
        for record in foxs_odds_container_instance.forge():
            self.batch(feed, record)

    def _store_team_stats(self, dispatcher, feed):
        if feed == "team-player-stats":
            team_stats_container = fox_sports_feeds.TeamPlayerStatsContainer
        elif feed == "team-stats":
            team_stats_container = fox_sports_feeds.TeamStatsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        team_stats_container_instance = team_stats_container(
            raw_data=dispatcher.container_class.raw_data,
            metadata=dispatcher.container_class.metadata,
            team_metadata=dispatcher.container_class.team_metadata,
        )
        team_stats_container_instance.extraction()
        for record in team_stats_container_instance.forge():
            self.batch(feed, record)

    def start(self):
        if not self.get_permission("matchups", "fetch"):
            self.logger.info("Fetch of Matchups Data Denied!", permissions=self.permissions)
            return

        self.logger.info("Pulling matchups data for {date}", date=self.date)
        matchups = self._retrieve_matchups()
        if not matchups.raw_data:
            self.logger.info("No Data available for Matchups!")
            return
        matchups.extraction()
        matchups_gen = matchups.forge()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel) as executor:
            for record in matchups_gen:
                home = record
                away = next(matchups_gen)
                if self.get_permission("matchups", "export"):
                    self.batch("matchups", home)
                    self.batch("matchups", away)

                away_team_meta = matchups.away_team_metadata
                home_team_meta = matchups.home_team_metadata
                event_meta = matchups.event_metadata

                matchups_home = {**event_meta, **home_team_meta}
                matchups_away = {**event_meta, **away_team_meta}

                if any(
                    [
                        self.get_permission("matchup-team-leaders-stats", "fetch"),
                        self.get_permission("matchup-team-stats", "fetch"),
                        self.get_permission("fox-odds", "fetch"),
                        self.get_permission("fox-projections", "fetch"),
                    ]
                ):

                    self._retrieve_matchup_team_stats(executor, matchups_home, matchups_away, event_meta)

                if self.get_permission("team-stats", "fetch") or self.get_permission("team-player-stats", "fetch"):
                    self._retrieve_team_stats(executor, away_team_meta, home_team_meta)

                if self.get_permission("team-roster", "fetch"):
                    self._retrieve_team_roster(executor, away_team_meta, home_team_meta)
            self.export("matchups")

            for future in concurrent.futures.as_completed(self.futures["matchups"]):
                dispatcher = future.result()
                if isinstance(dispatcher.container_class, fox_sports_feeds.BaseMatchupTeamStatsContainer):
                    if self.get_permission("matchup-team-leaders-stats", "export"):
                        self._store_matchup_team_stats(dispatcher, "matchup-team-leaders-stats")

                    if self.get_permission("matchup-team-stats", "export"):
                        self._store_matchup_team_stats(dispatcher, "matchup-team-stats")

                    if self.get_permission("fox-odds", "export"):
                        self._store_fox_odds(dispatcher, "fox-odds")

                    if self.get_permission("fox-projections", "export"):
                        self._store_fox_odds(dispatcher, "fox-projections")

                elif isinstance(dispatcher.container_class, fox_sports_feeds.BaseTeamStatsContainer):

                    if self.get_permission("team-player-stats", "export"):
                        self._store_team_stats(dispatcher, "team-player-stats")
                    if self.get_permission("team-stats", "export"):
                        self._store_team_stats(dispatcher, "team-stats")

                elif isinstance(dispatcher.container_class, fox_sports_feeds.TeamRosterContainer):
                    team_roster_container = fox_sports_feeds.TeamRosterContainer(
                        raw_data=dispatcher.container_class.raw_data,
                        metadata=dispatcher.container_class.metadata,
                        team_metadata=dispatcher.container_class.team_metadata,
                    )
                    team_roster_container.extraction()
                    recent_player_id = None
                    for record in team_roster_container.forge():
                        player_meta = {"player_id": record.get("player_id"), "player": record.get("player")}
                        if self.get_permission("team-roster", "export"):
                            self.batch("team-roster", record)
                        if self.get_permission("player-stats", "fetch") and recent_player_id != player_meta.get(
                            "player_id"
                        ):
                            recent_player_id = player_meta.get("player_id")
                            player_stats_params = self.feeds_config["player-stats"]["params"]
                            player_stats_url = self.feeds_config["player-stats"]["url"].format(
                                player_id=player_meta.get("player_id")
                            )
                            self.futures["player-stats"].append(
                                executor.submit(
                                    Dispatcher.dispatch,
                                    fox_sports_feeds.PlayerStatsContainer,
                                    player_stats_url,
                                    set_pull_metadata=True,
                                    request_kwargs={"params": player_stats_params},
                                    team_metadata=team_roster_container.team_metadata,
                                    player_metadata=player_meta,
                                )
                            )

                else:
                    self.logger.error(
                        "Unknown Container Class!",
                        container_class=dispatcher.container_class,
                        type_=type(dispatcher.container_class),
                    )
                    raise ValueError("Unknown Container Class!")
            del self.futures["matchups"]
            self.export("matchup-team-stats")
            self.export("matchup-team-leaders-stats")
            self.export("fox-odds")
            self.export("fox-projections")
            self.export("team-player-stats")
            self.export("team-stats")
            self.export("team-roster")

            for future in concurrent.futures.as_completed(self.futures["player-stats"]):
                dispatcher = future.result()
                if isinstance(dispatcher.container_class, fox_sports_feeds.PlayerStatsContainer):
                    player_stats_container = dispatcher.container_class
                    player_stats_container.extraction()
                    for record in player_stats_container.forge():
                        if self.get_permission("player-stats", "export"):
                            self.batch("player-stats", record)
                        if (
                            self.get_permission("advanced-player-stats", "fetch")
                            and player_stats_container.uri_to_request
                        ):
                            adv_player_stats_params = self.feeds_config["advanced-player-stats"]["params"]
                            self.futures["advanced-player-stats"].append(
                                executor.submit(
                                    Dispatcher.dispatch,
                                    fox_sports_feeds.AdvancedPlayerStatsContainer,
                                    player_stats_container.uri_to_request,
                                    set_pull_metadata=True,
                                    request_kwargs={"params": adv_player_stats_params},
                                    team_metadata=player_stats_container.team_metadata,
                                    player_metadata=player_stats_container.player_metadata,
                                )
                            )
                else:
                    self.logger.error(
                        "Unknown Container Class!",
                        container_class=dispatcher.container_class,
                        type_=type(dispatcher.container_class),
                    )
                    raise ValueError("Unknown Container Class!")
            del self.futures["player-stats"]
            self.export("player-stats")
            for future in concurrent.futures.as_completed(self.futures["advanced-player-stats"]):
                dispatcher = future.result()
                if isinstance(dispatcher.container_class, fox_sports_feeds.AdvancedPlayerStatsContainer):
                    advanced_player_stats_container = dispatcher.container_class
                    advanced_player_stats_container.extraction()
                    for record in advanced_player_stats_container.forge():
                        self.batch("advanced-player-stats", record)

                else:
                    self.logger.error(
                        "Unknown Container Class!",
                        container_class=dispatcher.container_class,
                        type_=type(dispatcher.container_class),
                    )
                    raise ValueError("Unknown Container Class!")
            del self.futures["advanced-player-stats"]
            self.export("advanced-player-stats")
