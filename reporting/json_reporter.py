from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path


def serialize(obj):
    """
    Recursively convert custom objects into JSON-safe structures.
    """

    if obj is None:
        return None

    if isinstance(obj, (str, int, float, bool)):
        return obj

    if isinstance(obj, list):
        return [serialize(i) for i in obj]

    if isinstance(obj, tuple):
        return [serialize(i) for i in obj]

    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}

    if hasattr(obj, "to_dict"):
        return serialize(obj.to_dict())

    if is_dataclass(obj):
        return serialize(asdict(obj))

    if hasattr(obj, "__dict__"):
        return serialize(vars(obj))

    return str(obj)


class JSONReporter:

    def write(self, result, output_file):

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            json.dump(
                serialize(result),
                f,
                indent=2,
                ensure_ascii=False,
            )

        return str(path)