import concurrent.futures

from sports.operations.download.fox_sports import Dispatcher, data_containers
from sports.operations.orchestrator import BaseOrchestrator
from sports.operations.utils import MAX_WORKERS


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
        matchups = data_containers.MatchupsContainer.from_request(
            matchups_url, set_pull_meta=False, params=matchups_params
        )
        return matchups

    def _retrieve_matchup_team_stats(self, executor, matchups_home, matchups_away, event_meta):
        matchup_team_stats_url = self.feeds_config["matchup-team-stats"]["url"].format(event_id=event_meta["event_id"])
        matchup_team_stats_params = self.feeds_config["matchup-team-stats"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                data_containers.BaseMatchupTeamStatsContainer,
                matchup_team_stats_url,
                set_pull_meta=False,
                extra_kwargs={"team1_meta": matchups_home, "team2_meta": matchups_away},
                params=matchup_team_stats_params,
            )
        )

    def _retrieve_team_stats(self, executor, away_team_meta, home_team_meta):
        away_team_url = self.feeds_config["team-stats"]["url"].format(team_id=away_team_meta["team_id"])
        home_team_url = self.feeds_config["team-stats"]["url"].format(team_id=home_team_meta["team_id"])
        team_params = self.feeds_config["team-stats"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                data_containers.BaseTeamStatsContainer,
                away_team_url,
                set_pull_meta=True,
                extra_kwargs={"team_meta": away_team_meta},
                params=team_params,
            )
        )
        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                data_containers.BaseTeamStatsContainer,
                home_team_url,
                set_pull_meta=True,
                extra_kwargs={"team_meta": home_team_meta},
                params=team_params,
            )
        )

    def _retrieve_team_roster(self, executor, away_team_meta, home_team_meta):
        away_team_roster_url = self.feeds_config["team-roster"]["url"].format(team_id=away_team_meta["team_id"])
        home_team_roster_url = self.feeds_config["team-roster"]["url"].format(team_id=home_team_meta["team_id"])
        team_roster_params = self.feeds_config["team-roster"]["params"]

        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                data_containers.TeamRosterContainer,
                away_team_roster_url,
                set_pull_meta=True,
                extra_kwargs={"team_meta": away_team_meta},
                params=team_roster_params,
            )
        )
        self.futures["matchups"].append(
            executor.submit(
                Dispatcher.dispatch,
                data_containers.TeamRosterContainer,
                home_team_roster_url,
                set_pull_meta=True,
                extra_kwargs={"team_meta": home_team_meta},
                params=team_roster_params,
            )
        )

    def _store_matchup_team_stats(self, dispatcher, feed):
        if feed == "matchup-team-stats":
            matchups_stats_container = data_containers.MatchupTeamStatsContainer
        elif feed == "matchup-team-leaders-stats":
            matchups_stats_container = data_containers.MatchupTeamLeaderStatsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        matchups_stats_container_instance = matchups_stats_container(raw_data=dispatcher.container_class.raw_data)
        matchups_stats_container_instance.extraction()
        matchup_stats_gen = matchups_stats_container_instance.parse_data_extracts(
            team1_meta=dispatcher.kwargs["team1_meta"],
            team2_meta=dispatcher.kwargs["team2_meta"],
        )
        for record in matchup_stats_gen:
            self.batch(feed, record)
            self.batch(feed, next(matchup_stats_gen))

    def _store_fox_odds(self, dispatcher, feed):
        if feed == "fox-odds":
            foxs_odds_container = data_containers.FoxOddsContainer
        elif feed == "fox-projections":
            foxs_odds_container = data_containers.FoxProjectionsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        foxs_odds_container_instance = foxs_odds_container(raw_data=dispatcher.container_class.raw_data)
        foxs_odds_container_instance.extraction()
        fox_odds_gen = foxs_odds_container_instance.parse_data_extracts(
            event_meta={"event_id": dispatcher.kwargs["team1_meta"]["event_id"]}
        )
        for record in fox_odds_gen:
            self.batch(feed, record)

    def _store_team_stats(self, dispatcher, feed):
        if feed == "team-player-stats":
            team_stats_container = data_containers.TeamPlayerStatsContainer
        elif feed == "team-stats":
            team_stats_container = data_containers.TeamStatsContainer
        else:
            raise ValueError(f"Invalid Feed {feed}!")

        team_stats_container_instance = team_stats_container(
            raw_data=dispatcher.container_class.raw_data, **dispatcher.container_class.meta
        )
        team_stats_container_instance.extraction()
        team_stats_gen = team_stats_container_instance.parse_data_extracts(team_meta=dispatcher.kwargs["team_meta"])
        for record in team_stats_gen:
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
        matchups_gen = matchups.parse_data_extracts()
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.parallel) as executor:
            for record in matchups_gen:
                home = record
                away = next(matchups_gen)
                if self.get_permission("matchups", "export"):
                    self.batch("matchups", home)
                    self.batch("matchups", away)

                away_team_meta = matchups.away_team_meta
                home_team_meta = matchups.home_team_meta
                event_meta = matchups.event_meta

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
                if isinstance(dispatcher.container_class, data_containers.BaseMatchupTeamStatsContainer):
                    if self.get_permission("matchup-team-leaders-stats", "export"):
                        self._store_matchup_team_stats(dispatcher, "matchup-team-leaders-stats")

                    if self.get_permission("matchup-team-stats", "export"):
                        self._store_matchup_team_stats(dispatcher, "matchup-team-stats")

                    if self.get_permission("fox-odds", "export"):
                        self._store_fox_odds(dispatcher, "fox-odds")

                    if self.get_permission("fox-projections", "export"):
                        self._store_fox_odds(dispatcher, "fox-projections")

                elif isinstance(dispatcher.container_class, data_containers.BaseTeamStatsContainer):

                    if self.get_permission("team-player-stats", "export"):
                        self._store_team_stats(dispatcher, "team-player-stats")
                    if self.get_permission("team-stats", "export"):
                        self._store_team_stats(dispatcher, "team-stats")

                elif isinstance(dispatcher.container_class, data_containers.TeamRosterContainer):
                    team_roster_container = data_containers.TeamRosterContainer(
                        raw_data=dispatcher.container_class.raw_data, **dispatcher.container_class.meta
                    )
                    team_roster_container.extraction()
                    team_roster_gen = team_roster_container.parse_data_extracts(
                        team_meta=dispatcher.kwargs["team_meta"]
                    )
                    recent_player_id = None
                    for record in team_roster_gen:
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
                                    data_containers.PlayerStats,
                                    player_stats_url,
                                    set_pull_meta=True,
                                    extra_kwargs={
                                        "team_meta": team_roster_container.team_meta,
                                        "player_meta": player_meta,
                                    },
                                    params=player_stats_params,
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
                if isinstance(dispatcher.container_class, data_containers.PlayerStats):
                    player_stats_container = data_containers.PlayerStats(
                        raw_data=dispatcher.container_class.raw_data, **dispatcher.container_class.meta
                    )
                    player_stats_container.extraction()
                    player_stats_gen = player_stats_container.parse_data_extracts(
                        team_meta=dispatcher.kwargs["team_meta"],
                        player_meta=dispatcher.kwargs["player_meta"],
                    )
                    for record in player_stats_gen:
                        if self.get_permission("player-stats", "export"):
                            self.batch("player-stats", record)
                        if (
                            self.get_permission("advanced-player-stats", "fetch")
                            and player_stats_container.current_advanced_stats_uri
                        ):
                            adv_player_stats_params = self.feeds_config["advanced-player-stats"]["params"]
                            self.futures["advanced-player-stats"].append(
                                executor.submit(
                                    Dispatcher.dispatch,
                                    data_containers.AdvancedPlayerStats,
                                    player_stats_container.current_advanced_stats_uri,
                                    set_pull_meta=True,
                                    extra_kwargs={
                                        "team_meta": player_stats_container.team_meta,
                                        "player_meta": player_stats_container.player_meta,
                                    },
                                    params=adv_player_stats_params,
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
                if isinstance(dispatcher.container_class, data_containers.AdvancedPlayerStats):
                    advanced_player_stats_container = data_containers.AdvancedPlayerStats(
                        raw_data=dispatcher.container_class.raw_data, **dispatcher.container_class.meta
                    )
                    advanced_player_stats_container.extraction()
                    advanced_player_stats_gen = advanced_player_stats_container.parse_data_extracts(
                        team_meta=dispatcher.kwargs["team_meta"],
                        player_meta=dispatcher.kwargs["player_meta"],
                    )
                    for record in advanced_player_stats_gen:
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
