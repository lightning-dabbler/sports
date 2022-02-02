<h1 align="center">Sports</h1>
<p align="center"><a href="https://circleci.com/gh/lightning-dabbler/sports" target="_blank"><img src="https://circleci.com/gh/lightning-dabbler/sports.svg?style=svg" alt="CircleCI Build Status"/>
</a></p>

<p align="center">An opinionated collection of processes that extracts and constructs sports related data artifacts from public applications</p>

### Installation
Python 3.7.5+ Required

```bash
# latest
pip install git+https://github.com/lightning-dabbler/sports.git

# Tag
pip install git+https://github.com/lightning-dabbler/sports.git@TAG
```

### Usage
```bash
$ sports --help
Usage: sports [OPTIONS] COMMAND [ARGS]...

  This is the main sports entrypoint

Options:
  -v, --verbose
  -s, --serialize
  --help           Show this message and exit.

Commands:
  fox-sports  Executes Fox Sports related CLI commands
```

```bash
$ sports fox-sports matchups --help
Usage: sports fox-sports matchups [OPTIONS]

  Retrieves Fox Sports Matchups Data

Options:
  -f, --force                     Make nested Directories if necessary
  --complete                      Export all Data Files
  -g, --groups [matchup-stats|fox-lines|team-stats]
                                  Groups of datasets to export
  -d, --datasets [matchups|matchup-team-leaders-stats|matchup-team-stats|fox-odds|fox-projections|team-stats|team-player-stats|team-roster|player-stats|advanced-player-stats]
                                  Datasets to export
  -b, --batch-size INTEGER        Batch size of data to hold in memory per
                                  data feed before writing to data file
  -p, --parallel INTEGER          Number of Concurrent Workers
  --tz TEXT                       Timezone of current data pull
  --config LOADS                  Inline configuration details
  -c, --compression [.bz2|.gz]
  -ft, --file-type [json-lines|csv]
  -o, --output <output>           location to export data file(s) to
  -s, --sport TEXT                Sport in Fox Sports to pull data for
                                  [required]
  -dt, --date TEXT                YYYY-MM-DD or YYYY-MM-DDTHH:mm:ss
  --help                          Show this message and exit.
```

### Development Setup
Enter main sports docker container:
```bash
make enter
```
Development:
```
make up
```
In the case of development that doesn't utilize containers the following are required:
- [poetry]==1.1.12
- Python 3.7.5+

```bash
make install-deps # It's imperative to use an isolated environment before running this command or one will risk Python dependencies in their environment being removed and pip being upgraded
make init
```

### Repository Dependencies
- [pre-commit]==2.17.0
- [docker 20.10.5+]
- [docker-compose 1.29.0+]



### Help?

```bash
make
```

### License
[MIT](./LICENSE)

### Author
Osarodion Irabor

[pre-commit]:https://pre-commit.com/
[docker 20.10.5+]:https://docs.docker.com/engine/release-notes/#20105
[docker-compose 1.29.0+]:https://docs.docker.com/compose/release-notes/#1290
[poetry]:https://python-poetry.org/docs/
