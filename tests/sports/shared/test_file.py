import json

import pytest

import sports.shared.file


def validate_date(data, location):
    with sports.shared.file.open(location, mode="wb") as f:
        for item in data:
            f.write(json.dumps(item).encode("utf-8") + b"\n")

    with sports.shared.file.open(location, mode="rb") as f:
        for idx, item in enumerate(f):
            assert data[idx] == json.loads(item)


@pytest.mark.parametrize(
    ("file_", "data"),
    [
        ("test.txt", ["foo", "bar", "baz"]),
        ("test.jsonl", [{"x": 1}, {"x": 5}, {"x": 10}]),
        ("test.jsonl.gz", [{"x": 1}, {"x": 5}, {"x": 10}]),
    ],
    ids=["text", "jsonl", "jsonl-gz"],
)
def test_open(tmpdir, file_, data):
    location = str(tmpdir.join(file_))
    validate_date(data, location)
