import jsonpatch, json, itertools
from itertools import zip_longest


def merge(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        d = dict(a)
        d.update({k: merge(a.get(k, None), b[k]) for k in b if b[k]})
        return d

    if isinstance(a, list) and isinstance(b, list):
        return [merge(x, y) for x, y in itertools.zip_longest(a, b)]

    return a if b is None else b


d1 = {"data": [{"a": 1}, {"b": None}, {"a": 1}, {"b": 1}]}
d2 = {"data": [{}, {"b": 2}, {}, {}]}

print(merge(d1, d2))
