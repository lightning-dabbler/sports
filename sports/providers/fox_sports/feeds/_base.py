import sports.shared.container

# Base Data Containers


class BaseTeamStatsContainer(sports.shared.container.BaseContainer):
    def __init__(self, *args, raw_data=None, metadata=None, team_metadata=None, **kwargs):
        self.team_metadata = team_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def forge(self, builder_obj):
        for record in self.data_extracts:
            stats = builder_obj.construct(record)
            yield {**self.metadata, **self.team_metadata, **stats}


class BaseMatchupTeamStatsContainer(sports.shared.container.BaseContainer):
    def __init__(
        self, *args, raw_data=None, metadata=None, left_team_metadata=None, right_team_metadata=None, **kwargs
    ):
        self.left_team_metadata = left_team_metadata or {}
        self.right_team_metadata = right_team_metadata or {}
        super().__init__(*args, raw_data=raw_data, metadata=metadata, **kwargs)

    def forge(self, builder_obj):
        for record in self.data_extracts:
            left_team_stats = builder_obj.construct_left_team_stats(record)
            right_team_stats = builder_obj.construct_right_team_stats(record)
            yield {**self.metadata, **self.left_team_metadata, **left_team_stats}
            yield {**self.metadata, **self.right_team_metadata, **right_team_stats}
