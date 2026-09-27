"""
Dataset schema, loading, and validation.

One CSV row per *observed circle*, not per transition. Transitions are derived,
because deriving them is where the errors show up: a missing phase silently
becomes a double-size jump and inflates every displacement statistic.

Required columns
----------------
match_id      stable identifier for the match (tournament + day + match number)
map_name      erangel | miramar | sanhok | vikendi | livik | rondo | ...
phase         integer, 1-based, the phase this circle belongs to
x, y, r       normalised map coordinates, all in [0, 1]
source        provenance string: URL or file plus timestamp, required
n_alive       teams or players alive when the circle was revealed (optional)
fit_quality   good | fair | poor - from the CV fitter or the human annotator

Provenance is not optional. An observation whose source cannot be re-checked
cannot be corrected later, and a dataset that cannot be corrected will quietly
carry its first mistakes into every model built on it.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np

from .geometry import Circle, Transition

REQUIRED = ["match_id", "map_name", "phase", "x", "y", "r", "source"]
OPTIONAL = ["n_alive", "fit_quality", "timestamp", "notes"]


def write_template(path: str | Path) -> Path:
    """Write an empty CSV with the right header and one worked example row."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(REQUIRED + OPTIONAL)
        w.writerow([
            "EXAMPLE-2026-D1-M3", "erangel", 1, 0.4812, 0.5533, 0.3100,
            "vod://example-tournament/day1?t=00:12:41", 64, "good",
            "00:12:41", "delete this row before use",
        ])
    return path


def load_circles(path: str | Path) -> list[dict]:
    with Path(path).open() as f:
        rows = list(csv.DictReader(f))
    out = []
    for i, row in enumerate(rows, start=2):
        if row.get("notes", "").startswith("delete this row"):
            continue
        try:
            out.append({
                "match_id": row["match_id"].strip(),
                "map_name": row["map_name"].strip().lower(),
                "phase": int(row["phase"]),
                "x": float(row["x"]), "y": float(row["y"]), "r": float(row["r"]),
                "source": row.get("source", "").strip(),
                "n_alive": int(row["n_alive"]) if row.get("n_alive") else None,
                "fit_quality": row.get("fit_quality", "").strip() or "unknown",
            })
        except (KeyError, ValueError) as e:
            raise ValueError(f"row {i} of {path} is malformed: {e}") from e
    return out


def validate(circles: list[dict]) -> list[str]:
    """Return a list of problems. An empty list is the only acceptable result."""
    problems: list[str] = []
    by_match: dict[str, list[dict]] = {}

    for c in circles:
        tag = f"{c['match_id']} phase {c['phase']}"
        for k in ("x", "y", "r"):
            if not (0.0 <= c[k] <= 1.0):
                problems.append(f"{tag}: {k}={c[k]} outside [0,1] - check normalisation")
        if c["r"] <= 0:
            problems.append(f"{tag}: non-positive radius")
        if not c["source"]:
            problems.append(f"{tag}: missing provenance")
        by_match.setdefault(c["match_id"], []).append(c)

    for mid, cs in by_match.items():
        cs = sorted(cs, key=lambda c: c["phase"])
        phases = [c["phase"] for c in cs]
        if len(set(phases)) != len(phases):
            problems.append(f"{mid}: duplicate phase numbers {phases}")
        gaps = [b - a for a, b in zip(phases, phases[1:]) if b - a != 1]
        if gaps:
            problems.append(
                f"{mid}: phase numbers skip ({phases}) - a missing phase looks like a "
                "double-size jump and will corrupt every displacement statistic"
            )
        maps = {c["map_name"] for c in cs}
        if len(maps) > 1:
            problems.append(f"{mid}: more than one map name {maps}")
        for a, b in zip(cs, cs[1:]):
            if b["r"] >= a["r"]:
                problems.append(f"{mid} phase {a['phase']}->{b['phase']}: radius does not shrink")
    return problems


def to_transitions(circles: list[dict], drop_poor: bool = True) -> list[Transition]:
    """Build consecutive-phase transitions, one match at a time."""
    by_match: dict[str, list[dict]] = {}
    for c in circles:
        if drop_poor and c["fit_quality"] == "poor":
            continue
        by_match.setdefault(c["match_id"], []).append(c)

    out: list[Transition] = []
    for mid, cs in by_match.items():
        cs = sorted(cs, key=lambda c: c["phase"])
        for a, b in zip(cs, cs[1:]):
            if b["phase"] != a["phase"] + 1:
                continue
            out.append(Transition(
                match_id=mid, map_name=a["map_name"], phase=a["phase"],
                prev=Circle(a["x"], a["y"], a["r"]),
                next=Circle(b["x"], b["y"], b["r"]),
                n_alive=b.get("n_alive"), source=b.get("source", ""),
            ))
    return out


def match_level_split(
    transitions: list[Transition], frac_train: float = 0.6, frac_val: float = 0.2, seed: int = 0
):
    """Split by match, never by transition.

    Transitions from one match share a first circle and a radius schedule, so a
    random split leaks information across the boundary and reports an accuracy
    the model does not have on a match it has never seen.
    """
    rng = np.random.default_rng(seed)
    matches = sorted({t.match_id for t in transitions})
    rng.shuffle(matches)
    n = len(matches)
    n_tr, n_va = int(n * frac_train), int(n * frac_val)
    train, val = set(matches[:n_tr]), set(matches[n_tr:n_tr + n_va])
    return (
        [t for t in transitions if t.match_id in train],
        [t for t in transitions if t.match_id in val],
        [t for t in transitions if t.match_id not in train and t.match_id not in val],
    )
