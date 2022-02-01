"""
matchups
| | |
1 2 3
| | |
+---------> matchup-team-leaders-stats
| | |
+--------> matchup-team-stats
| | |
+----------> fox-odds
| | |
+----------> fox-projections
  | |
  +-----> team-stats
  | |
  +-----> team-player-stats
    |
    +-----> team-roster
                |
                4
                |
                +----> player-stats
                            |
                            5
                            |
                            +-----> advanced-player-stats
"""


class Relations:
    datasets = [
        "matchups",
        "matchup-team-leaders-stats",
        "matchup-team-stats",
        "fox-odds",
        "fox-projections",
        "team-stats",
        "team-player-stats",
        "team-roster",
        "player-stats",
        "advanced-player-stats",
    ]

    def __init__(self):
        self.groups = {
            "matchup-stats": ["matchup-team-leaders-stats", "matchup-team-stats"],
            "fox-lines": ["fox-odds", "fox-projections"],
            "team-stats": ["team-stats", "team-player-stats"],
        }
        self.datasets_map = {dataset: {} for dataset in self.datasets}

        self.dependencies = {
            "matchup-team-leaders-stats": ["matchups"],
            "matchup-team-stats": ["matchups"],
            "fox-odds": ["matchups"],
            "fox-projections": ["matchups"],
            "team-stats": ["matchups"],
            "team-player-stats": ["matchups"],
            "team-roster": ["matchups"],
            "player-stats": ["team-roster", "matchups"],
            "advanced-player-stats": ["player-stats", "team-roster", "matchups"],
        }


relation = Relations()
KNOWN_GROUPS = relation.groups.keys()
KNOWN_DATASETS = relation.datasets
del relation
