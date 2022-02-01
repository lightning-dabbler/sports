"""
SERDE (Serialization-Deserialization) Strategies
"""
import csv
import json

from smart_open.compression import _COMPRESSOR_REGISTRY

SERIALIZER_REGISTRY = {}
DESERIALIZER_REGISTRY = {}


def register_strategy(registry, key):
    """Decorator for adding strategies to a lookup
    :param dict registry: available strategies
    :param str key: identifier for this strategy
    :return: return a registered strategy function
    """

    def register(strategy):
        registry[key] = strategy
        return strategy

    return register


def get_strategy(registry, strategy):
    if callable(strategy):
        return strategy
    elif isinstance(strategy, str):
        return registry[strategy]
    else:
        raise ValueError(f"type '{type(strategy)}' is not supported")


@register_strategy(DESERIALIZER_REGISTRY, "json-lines")
def deserialize_json_lines(f, **kwargs):
    """
    json newline delimited message decoding strategy
    :param f: a file handle or iterable of bytes
    """
    for line in f:
        yield json.loads(line)


@register_strategy(DESERIALIZER_REGISTRY, "csv")
def deserialize_csv(f, **kwargs):
    """
    csv message decoding strategy
    :param f: a file handle or iterable of bytes
    """
    reader = csv.DictReader(f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
    for line in reader:
        yield line


@register_strategy(SERIALIZER_REGISTRY, "json-lines")
def serialize_json_lines(f, data, **kwargs):
    """
    json newline delimited message encoding strategy
    :param f: a file handle or iterable of bytes
    :param iterable data:
    """
    record_count = 0
    for record in data:
        f.write(json.dumps(record).encode("utf-8") + b"\n")
        record_count += 1
    return record_count


@register_strategy(SERIALIZER_REGISTRY, "csv")
def serialize_csv(f, data, **kwargs):
    """
    csv delimited message encoding strategy
    :param f: a file handle or iterable of bytes
    :param iterable data:
    """
    record_count = 0
    writer = None
    for record in data:
        if not writer:
            writer = csv.DictWriter(f, fieldnames=record.keys(), delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writeheader()
        writer.writerow(record)
        record_count += 1
    return record_count


FILE_EXT = {"json-lines": ".jsonl", "csv": ".csv"}
WRITE_ACTION = {"csv": "w"}
APPEND_ACTION = {"csv": "a"}
COMPRESSION_OPTIONS = _COMPRESSOR_REGISTRY.keys()
FILE_TYPE_OPTIONS = FILE_EXT.keys()
