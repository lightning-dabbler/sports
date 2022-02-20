import json
import os
import time

import click
from loguru import logger

import sports
import sports.operations.validations
from sports.data_feeds import merge_dicts, read_config
from sports.operations.download.fox_sports import relationships
from sports.operations.download.fox_sports.orchestrator import Orchestrator
from sports.operations.relations import create_relation
from sports.shared.serde import COMPRESSION_OPTIONS, FILE_EXT, FILE_TYPE_OPTIONS
from sports.shared.utils import MAX_WORKERS

validations = sports.operations.validations.Validations(
    datasets=relationships.KNOWN_DATASETS, groups=relationships.KNOWN_GROUPS
)


@click.group()
def cli():
    pass


@click.option("-dt", "--date", default=None, required=False, help="YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss")
@click.option("-s", "--sport", required=True, help="Sport in Fox Sports to pull data for")
@click.option(
    "-o",
    "--output",
    metavar="<output>",
    default=sports.EXPORT,
    type=str,
    help="location to export data file(s) to",
)
@click.option("-ft", "--file-type", default="csv", type=click.Choice(FILE_TYPE_OPTIONS), required=False)
@click.option("-c", "--compression", default=".gz", type=click.Choice(COMPRESSION_OPTIONS), required=False)
@click.option(
    "--config",
    default="{}",
    type=json.loads,
    help="Inline configuration details",
)
@click.option("--tz", default="UTC", type=str, help="Timezone of current data pull")
@click.option("-p", "--parallel", default=MAX_WORKERS, type=int, help="Number of Concurrent Workers")
@click.option(
    "-b",
    "--batch-size",
    default=1000,
    type=int,
    help="Batch size of data to hold in memory per data feed before writing to data file",
)
@click.option(
    "-d",
    "--datasets",
    type=click.Choice(relationships.KNOWN_DATASETS),
    multiple=True,
    default=[],
    required=False,
    callback=validations.options_callback,
    help="Datasets to export",
)
@click.option(
    "-g",
    "--groups",
    type=click.Choice(relationships.KNOWN_GROUPS),
    multiple=True,
    default=[],
    required=False,
    callback=validations.options_callback,
    help="Groups of datasets to export",
)
@click.option("--complete", default=False, is_flag=True, help="Export all Data Files")
@click.option("-f", "--force", default=False, is_flag=True, help="Make nested Directories if necessary")
@cli.command(cls=sports.operations.validations.command_requirement_options("datasets", "groups"))
def matchups(
    sport, datasets, date, file_type, compression, batch_size, groups, output, config, tz, parallel, complete, force
):
    """Retrieves Fox Sports Matchups Data"""
    start = time.time()
    if force:
        os.environ["AUTO_MAKEDIRS"] = "1"
    config = config or {}
    groups = groups or []
    datasets = datasets or []

    config = merge_dicts(
        read_config(f"fox-sports-{sport}.yaml", layer="data_lake"),
        config,
    )
    logger.info("Configuring Fox Sports Matchups for '{sport}'", sport=sport, config=config)
    relations = relationships.Relations()
    datasets_map = relations.datasets_map
    for group in groups:
        for dataset in relations.groups[group]:
            create_relation(datasets_map, dataset, *relations.dependencies.get(dataset, []))
            datasets_map[dataset]["export"] = True
    for dataset in datasets:
        create_relation(datasets_map, dataset, *relations.dependencies.get(dataset, []))
        datasets_map[dataset]["export"] = True
    if complete:
        for dataset in datasets_map:
            datasets_map[dataset]["fetch"] = True
            datasets_map[dataset]["export"] = True

    orchestrate = Orchestrator(
        date=date,
        parallel=parallel,
        feeds_config=config,
        file_type=file_type,
        compression=compression,
        batch_size=batch_size,
        permissions=datasets_map,
        tz=tz,
        output=output,
    )
    orchestrate.start()
    file_ext = FILE_EXT[file_type] + compression
    for uri, record_count in orchestrate.written_files.items():
        full_path = uri if uri.endswith(file_ext) else f"{uri}{file_ext}"
        logger.info("'{file}' written with {records} records", records=record_count, file=full_path)
    logger.info("Process Complete in {total_runtime} seconds!", total_runtime=round(time.time() - start, 4))
