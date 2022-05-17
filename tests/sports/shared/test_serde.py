import pytest

import sports.shared.serde as serde


@pytest.mark.parametrize(
    "serialize,file_type,messages,expected",
    [
        (serde.serialize_json_lines, "json-lines", ["abc"] * 5, [b'"abc"\n'] * 5),
        (serde.serialize_json_lines, "json-lines", [{"k": "abc"}] * 5, [b'{"k": "abc"}\n'] * 5),
        (
            serde.serialize_csv,
            "csv",
            [{"test": 6, "test2": "foo"}] * 2,
            ['"test","test2"\n', '"6","foo"\n', '"6","foo"\n'],
        ),
    ],
    ids=["strings", "dictionaries", "csv"],
)
def test_serialize(tmpdir, serialize, file_type, messages, expected):
    filepath = f"{tmpdir}/test"
    write_mode = serde.WRITE_ACTION.get(file_type, "wb")
    read_mode = serde.READ_ACTION.get(file_type, "rb")
    with open(filepath, write_mode) as f:
        serialize(f, messages)
    with open(filepath, read_mode) as f_in:
        for idx, record in enumerate(f_in):
            assert expected[idx] == record


@pytest.mark.parametrize(
    "deserialize,file_type,messages,expected",
    [
        (serde.deserialize_json_lines, "json-lines", b"\n".join([b'"abc"'] * 5), ["abc"] * 5),
        (serde.deserialize_json_lines, "json-lines", b"\n".join([b'{"k": "abc"}'] * 5), [{"k": "abc"}] * 5),
        (
            serde.deserialize_csv,
            "csv",
            '"test","test2"\n6,"foo"\n4,"baz"\n',
            [{"test": "6", "test2": "foo"}, {"test": "4", "test2": "baz"}],
        ),
    ],
    ids=["strings", "dictionaries", "csv"],
)
def test_deserialize(tmpdir, deserialize, file_type, messages, expected):
    filepath = f"{tmpdir}/test"
    write_mode = serde.WRITE_ACTION.get(file_type, "wb")
    read_mode = serde.READ_ACTION.get(file_type, "rb")
    with open(filepath, write_mode) as f:
        f.write(messages)

    total = 0
    for idx, record in enumerate(deserialize(open(filepath, read_mode))):
        total = idx + 1
        expected_message = expected[idx]
        assert record == expected_message
    assert total == len(expected)
