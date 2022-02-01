import pathlib

import pytest

import sports.shared.file
import sports.shared.serde as serde
from sports.shared.operators import Archiver


@pytest.mark.parametrize(
    ("data", "strategy"),
    [
        ([{"col1": "test", "col2": "foo"}, {"col1": "bar", "col3": "baz"}], "json-lines"),
        ([{"col1": "test", "col2": "foo"}, {"col1": "bar", "col2": "baz"}], "json-lines"),
        ([{"look": "far"}, {"look": "here"}], "json-lines"),
    ],
    ids=["col1_col2_col3", "col1_col2", "look"],
)
def test_archiver(tmpdir, data, strategy):
    location = str(tmpdir.join("foo.jsonl.gz"))
    archiver = Archiver(data, location)
    archiver.write()
    with sports.shared.file.open(location, compression=".gz") as f:
        retrieved_strategy = serde.get_strategy(serde.DESERIALIZER_REGISTRY, strategy)
        for idx, record in enumerate(retrieved_strategy(f)):
            record_keys = record.keys()
            data_record = data[idx]
            data_keys = data_record.keys()

            assert set(record_keys) == set(data_keys)
            assert len(record_keys) == len(data_keys)
            for key in record_keys:
                assert data_record[key] == record[key]


def test_archiver_empty_input_stream(tmpdir):
    data = []
    location = str(tmpdir.join("foo.jsonl.gz"))
    archiver = Archiver(data, location)
    archiver.write()
    assert not list(pathlib.Path(location).rglob("*"))
