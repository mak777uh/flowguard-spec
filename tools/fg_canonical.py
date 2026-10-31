#!/usr/bin/env python3
"""fg_canonical — RFC 8785 (JCS) JSON, so two implementations agree on the bytes.

The old `canon()` was `json.dumps(..., sort_keys=True)`, whose docstring called itself "RFC 8785-shaped for this
subset". For numbers it was not: Python writes `0.0`, `-0.0`, `1.0`, `1e+20` and `1e-06` where the rule requires
`0`, `0`, `1`, `100000000000000000000` and `0.000001`. Six of the twelve published number cases diverged, and
`E-M71` had already measured the same split against JavaScript — 6 of 10 floats.

Numbers are the whole difficulty; strings, keys and structure are the same as before.

    from fg_canonical import canonical_bytes
    canonical_bytes({"coverage": 0.0})     # b'{"coverage":0}'
"""
import json
import math
from decimal import Decimal


def _es_number(value: float) -> str:
    """ECMAScript Number::toString for a finite double — the rule RFC 8785 §3.2.2.3 points at."""
    if value == 0:
        return "0"                      # covers -0.0: the rule has one zero
    sign = "-" if value < 0 else ""
    if value < 0:
        value = -value

    # repr() is the shortest string that round-trips, which is the same digit set the rule asks for;
    # Decimal turns it into digits and a decimal exponent without arithmetic of our own.
    dec = Decimal(repr(value))
    digits = "".join(str(d) for d in dec.as_tuple().digits)
    exponent = dec.as_tuple().exponent
    while len(digits) > 1 and digits.endswith("0"):
        digits = digits[:-1]
        exponent += 1

    n = len(digits)
    k = n + exponent                # position of the decimal point relative to the digits

    if k >= n and k <= 21:
        out = digits + "0" * (k - n)
    elif 0 < k <= 21:
        out = digits[:k] + "." + digits[k:]
    elif -6 < k <= 0:
        out = "0." + "0" * (-k) + digits
    else:
        head, tail = digits[0], digits[1:]
        out = head + ("." + tail if tail else "") + "e" + ("+" if k - 1 >= 0 else "-") + str(abs(k - 1))
    return sign + out


def _dumps(value, out):
    if value is None:
        out.append("null")
    elif value is True:
        out.append("true")
    elif value is False:
        out.append("false")
    elif isinstance(value, str):
        out.append(json.dumps(value, ensure_ascii=False))
    elif isinstance(value, int):
        out.append(str(value))
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number in a document that must be canonical")
        out.append(_es_number(value))
    elif isinstance(value, (list, tuple)):
        out.append("[")
        for i, item in enumerate(value):
            if i:
                out.append(",")
            _dumps(item, out)
        out.append("]")
    elif isinstance(value, dict):
        out.append("{")
        for i, key in enumerate(sorted(value)):
            if i:
                out.append(",")
            out.append(json.dumps(key, ensure_ascii=False))
            out.append(":")
            _dumps(value[key], out)
        out.append("}")
    else:
        raise TypeError(f"{type(value).__name__} is not JSON")


def canonical_text(doc) -> str:
    out = []
    _dumps(doc, out)
    return "".join(out)


def canonical_bytes(doc) -> bytes:
    return canonical_text(doc).encode()
