from multiprocessing import cpu_count


def header_date(headers_dict):
    ts = headers_dict.get("Date") or headers_dict.get("date")
    if not ts:
        raise KeyError("No presence of 'date' or 'Date' keys in 'headers_dict' dict")
    return ts


MAX_WORKERS = cpu_count() * 2 + 1

__all__ = [header_date, MAX_WORKERS]
