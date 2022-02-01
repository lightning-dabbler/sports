import pytest

import sports.shared.serde as serde


@pytest.mark.parametrize(
    "serialize,messages,expected",
    [
        (serde.serialize_json_lines, ["abc"] * 5, [b'"abc"\n'] * 5),
        (serde.serialize_json_lines, [{"k": "abc"}] * 5, [b'{"k": "abc"}\n'] * 5),
    ],
    ids=["strings", "dictionaries"],
)
def test_serialize(tmpdir, serialize, messages, expected):
    filepath = f"{tmpdir}/test"
    with open(filepath, "wb") as f:
        serialize(f, messages)
    with open(filepath, "rb") as f_in:
        for idx, record in enumerate(f_in):
            assert expected[idx] == record


@pytest.mark.parametrize(
    "deserialize,messages,expected",
    [
        (serde.deserialize_json_lines, "\n".join(['"abc"'] * 5), ["abc"] * 5),
        (serde.deserialize_json_lines, "\n".join(['{"k": "abc"}'] * 5), [{"k": "abc"}] * 5),
    ],
    ids=["strings", "dictionaries"],
)
def test_deserialize(tmpdir, deserialize, messages, expected):
    filepath = f"{tmpdir}/test"
    with open(filepath, "wb") as f:
        f.write(messages.encode("utf-8"))

    total = 0
    for idx, record in enumerate(deserialize(open(filepath, "rb"))):
        total = idx + 1
        expected_message = expected[idx]
        assert record == expected_message
    assert total == len(expected)
