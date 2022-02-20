import pathlib
import sys

import pytest
from loguru import logger

from sports.data_feeds import merge_dicts, read_config
from sports.operations.download.fox_sports import relationships
from sports.operations.download.fox_sports.orchestrator import Orchestrator
from sports.shared.utils import MAX_WORKERS

logger.remove()
logger.add(sys.stderr, level=20, serialize=False, backtrace=True, diagnose=True)


@pytest.mark.parametrize(
    "config,date,sport",
    [
        (
            {
                "matchups": {"filename": "fox-sports-nba-matchups-{timestamp}"},
                "matchup-team-stats": {"filename": "fox-sports-nba-matchup-team-stats-{timestamp}"},
                "matchup-team-leaders-stats": {"filename": "fox-sports-nba-matchup-team-leaders-stats-{timestamp}"},
                "fox-odds": {"filename": "fox-sports-nba-fox-odds-{timestamp}"},
                "fox-projections": {"filename": "fox-sports-nba-fox-projections-{timestamp}"},
                "team-player-stats": {"filename": "fox-sports-nba-team-player-stats-{timestamp}-current"},
                "team-stats": {"filename": "fox-sports-nba-team-stats-{timestamp}-current"},
                "team-roster": {"filename": "fox-sports-nba-team-roster-{timestamp}-current"},
                "player-stats": {"filename": "fox-sports-nba-player-stats-{timestamp}-current"},
                "advanced-player-stats": {"filename": "fox-sports-nba-advanced-player-stats-{timestamp}-current"},
            },
            "2022-02-16",
            "nba",
        )
    ],
)
def test_orchestrator(tmp_path, config, date, sport):
    config = merge_dicts(
        read_config(f"fox-sports-{sport}.yaml", layer="data_lake"),
        config,
    )
    relations = relationships.Relations()
    datasets_map = relations.datasets_map
    for dataset in datasets_map:
        datasets_map[dataset]["fetch"] = True
        datasets_map[dataset]["export"] = True
    orchestrate = Orchestrator(
        date=date,
        parallel=MAX_WORKERS,
        feeds_config=config,
        file_type="csv",
        compression=".gz",
        batch_size=2000,
        permissions=datasets_map,
        tz="UTC",
        output=str(tmp_path),
    )
    orchestrate.start()

    files = [path for path in pathlib.Path(tmp_path).rglob("*")]
    assert len(files) == len(config)
